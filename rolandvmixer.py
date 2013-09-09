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
_NUM_CHANNELS = 48
_NUM_RETURNS = 8
_NUM_AUXES = 16
_NUM_MATRICES = 8
_NUM_GROUPS = 24
_NUM_MAINS = 3

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
_NAME_POLL_DELAY = 300.0

# If no level items are enqueued, wait this amount before trying again.
# Without this delay having no configured channels busy waits the CPU.
_LEVEL_POLL_DELAY = 1.0


# Generic channel ID information to pass to the mixer object
_ids = {}
_ids['channels'] = [c + 1 for c in range(_NUM_CHANNELS)]
_ids['returns'] = [r + 1 for r in range(_NUM_RETURNS)]
_ids['auxes'] = [a + 1 for a in range(_NUM_AUXES)]
_ids['matrices'] = [t + 1 for t in range(_NUM_MATRICES)]
_ids['groups'] = [g + 1 for g in range(_NUM_GROUPS)]
_ids['mains'] = [m + 1 for m in range(_NUM_MAINS)]


def _encodeid(item, num):
    if item == 'channel':
        return 'I{0}'.format(num)
    elif item == 'aux':
        return 'AX{0}'.format(num)
    else:
        raise ValueError


def _decodeid(id):
    if id[0] == 'I':
        return 'channel', int(id[1:])
    elif id[0:2] == 'AX':
        return 'aux', int(id[2:])
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
    if level < mixer.Mixer._MIN_LEVEL:
        return 'INF'
    if level < -80.0:
        return '-80.0'  # THINK ABOUT THIS!!!
    if level > 10.0:
        return '10.0'
    return '{0:0.1f}'.format(level)


def _decodelevel(levelstr):
    if levelstr == 'INF':
        return mixer.Mixer._MIN_LEVEL
    level = float(levelstr)
    level = max(mixer.Mixer._MIN_LEVEL, level)
    level = min(mixer.Mixer._MAX_LEVEL, level)
    return level


def _encodereq(cmd, data=[]):
    datastr = ':' + ','.join(map(str, data)) if data else ''
    req = ''.join((_STX, cmd, datastr, ';'))
    return req.encode('utf-8')


def _decoderes(res):
    cmddata = res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')
    return cmddata[0], cmddata[1:]


class RolandVMixer(mixer.Mixer):

    def _updatechannel(self, c, params):
        cid = _encodeid('channel', c)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('FDC', [cid, levelstr])))

    def _updateaux(self, a, params):
        aid = _encodeid('aux', a)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('FDC', [aid, levelstr])))

    def _updateauxchannel(self, a, c, params):
        aid = _encodeid('aux', a)
        cid = _encodeid('channel', c)
        for name, value in params.items():
            if name == 'level':
                levelstr = _encodelevel(value)
                panstr = _encodepan(params.get('pan', self._channels[c]['auxes'][a].get('pan', 0)))
                self._commandqueue.put((_TYPE_API_COMMAND, _encodereq('AXC', [cid, aid, levelstr, panstr])))
        self._channels[c]['auxes'][a].update(params)

    def _sendcommands(self):
        while True:
            self._commandsemaphore.acquire()
            typ, req = self._commandqueue.get()
            self._port.write(req)
            _logger.debug('Sent {0} to {1}'.format(req, self._port.port))
            self._commandqueue.task_done()

    def _recvcommands(self):
        while True:
            # TODO is there a better way to read results other than 1 byte at a time?
            res = ''
            while res[-1:] not in (_ACK, _TERM):
                res += self._port.read().decode('utf-8')
            self._commandsemaphore.release()
            _logger.debug('Received {0} from {1}'.format(res.encode('utf-8'), self._port.port))
            cmd, data = _decoderes(res)
            if cmd == 'CNS':
                id, name = data
                params = {'name': name.strip()}
                item, num = _decodeid(id)
                if item == 'channel':
                    self._channels[num].update(params)
                elif item == 'aux':
                    self._auxes[num].update(params)
            elif cmd == 'FDS':
                id, level = data
                params = {'level': _decodelevel(level)}
                item, num = _decodeid(id)
                if item == 'channel':
                    self._channels[num].update(params)
                elif item == 'aux':
                    self._auxes[num].update(params)
            elif cmd == 'AXS':
                cid, aid, level, pan = data
                params = {'pan': _decodepan(pan), 'level': _decodelevel(level)}
                citem, cnum = _decodeid(cid)
                if citem == 'channel':
                    aitem, anum = _decodeid(aid)
                    if aitem == 'aux':
                        self._channels[cnum]['auxes'][anum].update(params)

    def _namepoller(self):
        while True:
            for cid in (_encodeid('channel', c) for c in self._channels):
                self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [cid])))
            for aid in (_encodeid('aux', a) for a in self._auxes):
                self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [aid])))
            _logger.info('Completed poll of names.')
            time.sleep(_NAME_POLL_DELAY)

    def _levelpoller(self):
        while True:
            for cid in (_encodeid('channel', c) for c in self._channels if self._channels[c].get('name', '')):
                self._commandqueue.put((_TYPE_LEVEL_POLL, _encodereq('FDQ', [cid])))
                for aid in (_encodeid('aux', a) for a in self._auxes if self._auxes[a].get('name', '')):
                    self._commandqueue.put((_TYPE_LEVEL_POLL, _encodereq('AXQ', [cid, aid])))
            _logger.info('Completed poll of levels.')
            if not self._commandqueue.empty():
                self._commandqueue.join()
            else:
                time.sleep(_LEVEL_POLL_DELAY)


    def __init__(self, port):
        super().__init__(_ids)
        self._commandsemaphore = threading.BoundedSemaphore(4)
        self._commandqueue = queue.PriorityQueue(_COMMAND_QUEUE_SIZE)
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = 115200
        self._port.xonxoff = True
        self._port.timeout = 1.0
        try:
            self._port.open()
            threading.Thread(target=self._recvcommands).start()
            threading.Thread(target=self._sendcommands).start()
            threading.Thread(target=self._namepoller).start()
            threading.Thread(target=self._levelpoller).start()
            _logger.info('Initialized interface at ' + port)
        except serial.SerialException:
            _logger.error('Unable to initialize interface at port ' + port)
