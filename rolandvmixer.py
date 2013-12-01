"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer interface for Mix Maestro.
"""


# Standard library imports
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
# time goes by without any response, give up on the read, blow
# away any queued up requests, and start over with polling.
_PORT_TIMEOUT = 1.0

# Codes for command transmission
_STX = '\x02'
_ACK = '\x06'
_TERM = ';'
_ERROR = _STX + 'ERR'

# Defines priority mapping for command types.
_TYPE_API_COMMAND = 0
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
    level = float(level)
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
    cmddata = res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')
    try:
        return cmddata[0], cmddata[1:]
    except IndexError:
        return 'BAD'


class RolandVMixer(mixer.Mixer):
    """The mixer class that operates with the Roland V-Mixer products."""

    def _updateinput(self, i, params):
        iid = _encodeid('input', i)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('FDC', [iid, levelstr])))

    def _updateaux(self, a, params):
        aid = _encodeid('aux', a)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('FDC', [aid, levelstr])))

    def _updateauxinput(self, a, i, params):
        aid = _encodeid('aux', a)
        iid = _encodeid('input', i)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                panstr = _encodepan(params.get('pan', self._inputs[i]['auxes'][a].get('pan', 0)))
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('AXC', [iid, aid, levelstr, panstr])))
        self._inputs[i]['auxes'][a].update(params)

    def _processcommands(self):
        while True:
            typ, req = self._commandqueue.get()
            self._port.write(req)
            _logger.debug('Sent {0} to {1}'.format(req, self._port.port))
            res = ''
            while res[-1:] not in (_ACK, _TERM):
                data = self._port.read().decode('utf-8')
                if data:
                    res += data
                else:
                    _logger.warning('Port {0} timed out, flushing data'.format(self._port.port))
                    self._port.flushInput()
                    self._port.flushOutput()
                    break
            _logger.debug('Received {0} from {1}'.format(res.encode(), self._port.port))
            cmd, data = _decoderes(res)
            if cmd == 'CNS':
                iid, name = data
                params = {'name': name.strip(" \"")}
                chantype, num = _decodeid(iid)
                if chantype == 'input':
                    self._inputs[num].update(params)
                elif chantype == 'aux':
                    self._auxes[num].update(params)
            elif cmd == 'FDS':
                iid, level = data
                params = {'level': _decodelevel(level)}
                chantype, num = _decodeid(iid)
                if chantype == 'input':
                    self._inputs[num].update(params)
                elif chantype == 'aux':
                    self._auxes[num].update(params)
            elif cmd == 'AXS':
                cid, aid, level, pan = data
                params = {'pan': _decodepan(pan), 'level': _decodelevel(level)}
                chantype, cnum = _decodeid(cid)
                anum = _decodeid(aid)[1]
                if chantype == 'input':
                    self._inputs[cnum]['auxes'][anum].update(params)
            self._commandqueue.task_done()

    def _namepoller(self):
        while True:
            for iid in (_encodeid('input', i) for i in self._inputs):
                self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [iid])))
            for aid in (_encodeid('aux', a) for a in self._auxes):
                self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [aid])))
            time.sleep(_NAME_POLL_DELAY)

    def _levelpoller(self):
        while True:
            for iid in (_encodeid('input', i) for i in self._inputs if self._inputs[i].get('name', '')):
                self._commandqueue.put((_TYPE_LEVEL_POLL, _encodereq('FDQ', [iid])))
                for aid in (_encodeid('aux', a) for a in self._auxes if self._auxes[a].get('name', '')):
                    self._commandqueue.put((_TYPE_LEVEL_POLL, _encodereq('AXQ', [iid, aid])))
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
        try:
            self._port.open()
            threading.Thread(target=self._processcommands).start()
            threading.Thread(target=self._namepoller).start()
            threading.Thread(target=self._levelpoller).start()
            _logger.info('Initialized interface at ' + port)
        except serial.SerialException:
            _logger.error('Unable to initialize interface at port ' + port)
