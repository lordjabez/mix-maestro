"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer interface for Mix Maestro.
"""


# Standard library imports
import collections
import logging
import queue
import threading
import time

# Additional library imports
import serial

# Mix Maestro imports
import mixer


# Named logger for this module
_logger = logging.getLogger(__name__)


# Info on the mixer
_NUM_INPUTS = 48
_NUM_RETURNS = 8
_NUM_AUXES = 16
_NUM_MATRICES = 8
_NUM_GROUPS = 24
_NUM_MAINS = 3

# Speed at which to communicate with the mixer.
_PORT_BAUDRATE = 115200

# Timeout value for serial port reads in seconds. If this much
# time goes by without any response, give up on the read.
_PORT_TIMEOUT = 1.0

# Codes for command transmission
_STX = '\x02'
_ACK = '\x06'
_TERM = ';'
_ERROR = _STX + 'ERR'

# Defines priority mapping for command types.
_TYPE_API_COMMAND = 0
_TYPE_API_QUERY = 1
_TYPE_NAME_POLL = 10
_TYPE_LEVEL_POLL = 100

# Maximum size of the command queue. If this gets full, the mixer
# isn't talking back fast enough, if we're talking to it at all.
_COMMAND_QUEUE_SIZE = 1024

# Poll rate for names. Faster rates catch name
# changes sooner but will slow down other polling.
_NAME_POLL_DELAY = 60.0

# If no level items are queued, wait this amount before trying again.
# Without this delay having no configured channels busy waits the CPU.
_LEVEL_POLL_DELAY = 1.0

# Minimum and maximum for the fader levels.
_MIN_LEVEL = -80.0
_MAX_LEVEL = 10.0

# Generic channel ID information to pass to the mixer object
_ids = {
    'inputs': [i + 1 for i in range(_NUM_INPUTS)],
    'returns': [r + 1 for r in range(_NUM_RETURNS)],
    'auxes': [a + 1 for a in range(_NUM_AUXES)],
    'matrices': [t + 1 for t in range(_NUM_MATRICES)],
    'groups': [g + 1 for g in range(_NUM_GROUPS)],
    'mains': [m + 1 for m in range(_NUM_MAINS)]
}


def _encodeid(chantype, num):
    if chantype == 'input':
        return 'I{0}'.format(num)
    elif chantype == 'aux':
        return 'AX{0}'.format(num)
    else:
        raise ValueError


def _decodeid(iid):
    if iid[0] == 'I':
        return 'input', int(iid[1:])
    elif iid[0:2] == 'AX':
        return 'aux', int(iid[2:])
    else:
        raise ValueError


def _encodepan(pan):
    try:
        pan = float(pan)
    except TypeError:
        raise ValueError
    if pan < 0.0:
        return 'L{0}'.format(min(-int(pan * 63.0), 63))
    elif pan > 0.0:
        return 'R{0}'.format(min(int(pan * 63.0), 63))
    else:
        return 'C'


def _decodepan(panstr):
    if panstr[0] == 'L':
        return -float(panstr[1:]) / 63.0
    elif panstr[0] == 'R':
        return float(panstr[1:]) / 63.0
    else:
        return 0.0


def _encodelevel(level):
    try:
        level = float(level)
    except TypeError:
        raise ValueError
    level = max(_MIN_LEVEL, level)
    level = min(_MAX_LEVEL, level)
    return '{0:0.1f}'.format(level) if level > _MIN_LEVEL else 'INF'


def _decodelevel(levelstr):
    if levelstr == 'INF':
        return _MIN_LEVEL
    level = float(levelstr)
    level = max(_MIN_LEVEL, level)
    level = min(_MAX_LEVEL, level)
    return level


def _encodereq(cmd, data=None):
    datastr = ':' + ','.join(map(str, data)) if data else ''
    req = ''.join((_STX, cmd, datastr, ';'))
    return req.encode()


def _decoderes(res):
    try:
        cmddata = res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')
        return cmddata[0], cmddata[1:]
    except (AttributeError, IndexError):
        return None, None


class RolandVMixer(mixer.Mixer):
    """The mixer class that operates with the Roland V-Mixer products."""

    def _enqueuecommand(self, typ, cmd):
        self._commandqueue.put((typ,cmd))
        self._counts['commandsqueued'] += 1

    def _updateinput(self, i, params):
        iid = _encodeid('input', i)
        for name, value in params.items():
            if name == 'level':
                try:
                    levelstr = _encodelevel(value)
                except ValueError:
                    return
                self._enqueuecommand(_TYPE_API_COMMAND, _encodereq('FDC', [iid, levelstr]))
                self._enqueuecommand(_TYPE_API_QUERY, _encodereq('FDQ', [iid]))

    def _updateaux(self, a, params):
        aid = _encodeid('aux', a)
        for name, value in params.items():
            if name == 'level':
                try:
                    levelstr = _encodelevel(value)
                except ValueError:
                    return
                self._enqueuecommand(_TYPE_API_COMMAND, _encodereq('FDC', [aid, levelstr]))
                self._enqueuecommand(_TYPE_API_QUERY, _encodereq('FDQ', [aid]))

    def _updateauxinput(self, a, i, params):
        aid = _encodeid('aux', a)
        iid = _encodeid('input', i)
        for name, value in params.items():
            if name == 'level':
                try:
                    levelstr = _encodelevel(value)
                    panstr = _encodepan(params.get('pan', self._inputs[i]['auxes'][a].get('pan', 0)))
                except ValueError:
                    return
                self._enqueuecommand(_TYPE_API_COMMAND, _encodereq('AXC', [iid, aid, levelstr, panstr]))
                self._enqueuecommand(_TYPE_API_QUERY, _encodereq('AXQ', [iid, aid]))

    def _writecommand(self, req):
        if not self._port.isOpen():
            try:
                self._port.open()
            except IOError:
                if self._portavailable:
                    _logger.error('Unable to open port {0}'.format(self._port.name))
                    self._portavailable = False
                    self._mixerresponding = False
                self._counts['writeerrors'] += 1
                return False
            if not self._portavailable:
                self._portavailable = True
                _logger.info('Opened port {0}'.format(self._port.name))
        try:
            self._port.write(req)
        except IOError:
            _logger.warning('Could not write to port {0}'.format(self._port.name))
            self._port.close()
            self._counts['writeerrors'] += 1
            return False
        _logger.debug('Sent {0} to port {1}'.format(req, self._port.port))
        return True

    def _readresponse(self):
        res = ''
        while res[-1:] not in (_ACK, _TERM):
            try:
                data = self._port.read()
            except IOError:
                if self._mixerresponding:
                    _logger.warning('Could not read from port {0}'.format(self._port.name))
                    self._mixerresponding = False
                self._port.close()
                self._counts['readerrors'] += 1
                return
            if data:
                try:
                    res += data.decode('utf-8')
                except UnicodeDecodeError:
                    if self._mixerresponding:
                        _logger.warning('Received undecodable data on port {0}'.format(self._port.port))
                        self._mixerresponding = False
                    self._port.close()
                    self._counts['readerrors'] += 1
                    return
            else:
                if self._mixerresponding:
                    _logger.warning('Port {0} timed out'.format(self._port.port))
                    self._mixerresponding = False
                self._port.close()
                self._counts['readerrors'] += 1
                return
            # No response should ever be this long
            if len(res) > 1024:
                if self._mixerresponding:
                    _logger.warning('Received too much data on port {0} without terminator'.format(self._port.port))
                    self._mixerresponding = False
                self._port.close()
                self._counts['readerrors'] += 1
                return
        _logger.debug('Received {0} on port {1}'.format(res.encode(), self._port.port))
        if not self._mixerresponding:
            _logger.info('Mixer responding on port {0}'.format(self._port.name))
            self._mixerresponding = True
            self._pollnames()
        return res

    def _processresponse(self, res):
        cmd, data = _decoderes(res)
        if cmd == 'CNS':
            iid, name = data
            params = {'name': name.strip(" \"")}
            chantype, num = _decodeid(iid)
            if chantype == 'input':
                self._inputs[num].update(params)
            elif chantype == 'aux':
                self._auxes[num].update(params)
            self._counts['responsesprocessed'] += 1
        elif cmd == 'FDS':
            iid, level = data
            params = {'level': _decodelevel(level)}
            chantype, num = _decodeid(iid)
            if chantype == 'input':
                self._inputs[num].update(params)
            elif chantype == 'aux':
                self._auxes[num].update(params)
            self._counts['responsesprocessed'] += 1
        elif cmd == 'AXS':
            cid, aid, level, pan = data
            params = {'pan': _decodepan(pan), 'level': _decodelevel(level)}
            chantype, cnum = _decodeid(cid)
            anum = _decodeid(aid)[1]
            if chantype == 'input':
                self._inputs[cnum]['auxes'][anum].update(params)
            self._counts['responsesprocessed'] += 1

    def _processcommands(self):
        while True:
            typ, req = self._commandqueue.get()
            success = self._writecommand(req)
            if success:
                self._counts['commandssent'] += 1
                res = self._readresponse()
            else:
                res = None
            self._processresponse(res)
            self._commandqueue.task_done()

    def _pollnames(self):
        for iid in (_encodeid('input', i) for i in self._inputs):
            self._enqueuecommand(_TYPE_NAME_POLL, _encodereq('CNQ', [iid]))
        for aid in (_encodeid('aux', a) for a in self._auxes):
            self._enqueuecommand(_TYPE_NAME_POLL, _encodereq('CNQ', [aid]))

    def _polllevels(self):
        for iid in (_encodeid('input', i) for i in self._inputs if self._inputs[i].get('name', '')):
            self._enqueuecommand(_TYPE_LEVEL_POLL, _encodereq('FDQ', [iid]))
            for aid in (_encodeid('aux', a) for a in self._auxes if self._auxes[a].get('name', '')):
                self._enqueuecommand(_TYPE_LEVEL_POLL, _encodereq('AXQ', [iid, aid]))

    def _namepoller(self):
        while True:
            self._pollnames()
            time.sleep(_NAME_POLL_DELAY)

    def _levelpoller(self):
        while True:
            self._polllevels()
            if not self._commandqueue.empty():
                self._commandqueue.join()
            else:
                time.sleep(_LEVEL_POLL_DELAY)

    def __init__(self, port):
        super().__init__(_ids)
        self._commandqueue = queue.PriorityQueue(_COMMAND_QUEUE_SIZE)
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = _PORT_BAUDRATE
        self._port.timeout = _PORT_TIMEOUT
        self._port.xonxoff = True
        self._portavailable = False
        self._mixerresponding = False
        self._counts = collections.defaultdict(int)
        threading.Thread(target=self._processcommands).start()
        threading.Thread(target=self._namepoller).start()
        threading.Thread(target=self._levelpoller).start()
        _logger.info('Roland V-Mixer interface initialized')


    def getstatus(self):
        """
        Provide status information for the connection to the mixer.
        @return: Dictionary containing status information
        """
        if self._portavailable:
            if self._mixerresponding:
                return {'condition': 'operational', 'counts': self._counts}
            else:
                return {'condition': 'degraded', 'counts': self._counts}
        else:
            return {'condition': 'nonoperational', 'counts': self._counts}


    def resetstatus(self):
        """Reset status information for the connection to the mixer."""
        self._counts = collections.defaultdict(int)
