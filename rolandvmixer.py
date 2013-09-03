"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer interface for Mix Maestro.
"""


# Standard library imports
import logging
import os
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

# Roland identifiers for specific items
_CHANNEL_IDS = ['I{0}'.format(c + 1) for c in range(_NUM_CHANNELS)]
_AUX_IDS = ['AX{0}'.format(a + 1) for a in range(_NUM_AUXES)]

# Command types (used to prioritize command sends)
_TYPE_IMMEDIATE = 0
_TYPE_NAME_POLL = 10
_TYPE_LEVEL_POLL = 100

# Maximum size of the command queue (if this gets full, the mixer
# isn't talking back fast enough, if we're talking to it at all.
_COMMAND_QUEUE_SIZE = 1024

# Poll rate for names. Faster rates catch name
# changes sooner but will slow down other polling.
_NAME_POLL_DELAY = 120.0

# Generic channel ID information to pass to the mixer object
# TODO change all these to integer lookups in all places
_ids = {}
_ids['channels'] = [str(c + 1) for c in range(_NUM_CHANNELS)]
_ids['returns'] = [str(r + 1) for r in range(_NUM_RETURNS)]
_ids['auxes'] = [str(a + 1) for a in range(_NUM_AUXES)]
_ids['matrices'] = [str(t + 1) for t in range(_NUM_MATRICES)]
_ids['groups'] = [str(g + 1) for g in range(_NUM_GROUPS)]
_ids['mains'] = [str(m + 1) for m in range(_NUM_MAINS)]


# TODO encode/decode ids

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
    try:
        if levelstr == 'INF':
            raise ValueError
        level = float(levelstr)
        level = max(mixer.Mixer._MIN_LEVEL, level)
        level = min(mixer.Mixer._MAX_LEVEL, level)
        return level
    except ValueError:
        return mixer.Mixer._MIN_LEVEL


def _encodepan(pan):
    if pan < 0.0:
        return 'L{0}'.format(min(-int(pan / 100.0 * 63.0), 63))
    elif pan > 0.0:
        return 'R{0}'.format(min(int(pan / 100.0 * 63.0), 63))
    else:
        return 'C'    


def _decodepan(panstr):
    if panstr[0] == 'L':
        return -int(float(panstr[1:]) * 100.0 / 63.0)
    elif panstr[0] == 'R':
        return int(float(panstr[1:]) * 100.0 / 63.0)
    else:
        return 0


def _encodereq(cmd, data=[]):
    datastr = ':' + ','.join(map(str, data)) if data else ''
    req = ''.join((_STX, cmd, datastr, ';'))
    return req.encode('utf-8')


def _decoderes(res):
    return res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')


class RolandVMixer(mixer.Mixer):

    def _processcommands(self):
        while True:
            typ, req = self._commandqueue.get()
            self._port.write(req)
            # TODO is there a better way to read results other than 1 byte at a time?
            res = ''
            while res[-1:] not in (_ACK, _TERM):
                res += self._port.read().decode('utf-8')
            cmd, data = _decoderes(res)
            # TODO incorporate id encode/decode
            if cmd == 'CNS':
                cid, name = data
                params = {'name': name.strip()}
                if cid[0] == 'I':
                    self.setchannels(cid[1:], params)
                elif cid[0:2] == 'AX':
                    self.setauxes(cid[2:], params)
            elif cmd == 'FDS':
                cid, level = data
                params = {'level': _decodelevel(level)}
                if cid[0] == 'I':
                    self.setchannels(cid[1:], params)
                elif cid[0:2] == 'AX':
                    self.setauxes(cid[2:], params)
            elif cmd == 'AXS':
                cid, aid, pan, level = data
                params = {'pan': _decodepan(pan), 'level': _decodelevel(level)}
                if cid[0] == 'I':
                    self.setauxes(aid[2:], cid[1:], params)
            # Requeue the level polls so they always happen if nothing else is going on.
            if typ == _TYPE_LEVEL_POLL:
                self._commandqueue.put(req)

    # TODO iterate over actual mixer object dictionary and encode IDs
    def _namepoller(self):
        for c in _CHANNEL_IDS:
            self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [c])))
        for a in _AUX_IDS:
            self._commandqueue.put((_TYPE_NAME_POLL, _encodereq('CNQ', [a])))
        time.sleep(_NAME_POLL_DELAY)

    # TODO mod this to only poll channels with non-empty names
    def _levelpoller(self):
        pass # TODO remove
        #for c in _CHANNEL_IDS:
        #    self._commandqueue.put(_encodereq('FDQ', [c]))


    def __init__(self, port):
        super().__init__(_ids)
        self._commandqueue = queue.PriorityQueue(_COMMAND_QUEUE_SIZE)
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = 115200
        self._port.xonxoff = True
        self._port.timeout = 1.0
        try:
            self._port.open()
            threading.Thread(target=self._processcommands).start()
            threading.Thread(target=self._namepoller).start()
            threading.Thread(target=self._levelpoller).start()
            _logger.info('Initialized interface at ' + port)
        except serial.SerialException:
            _logger.error('Unable to initialize interface at port ' + port)
