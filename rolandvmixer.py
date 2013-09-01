"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer interface for Mix Maestro.
"""


# Standard library imports
import binascii
import logging
import threading

# Additional library imports
import serial

# Mix Maestro imports
import mixer


# Named logger for this module
_logger = logging.getLogger(__name__)


# TODO move everything inside the class
# Info on the mixer
_NUM_INPUTS = 48
_NUM_AUXES = 16

# Codes for command transmission
_STX = '\x02'
_ACK = '\x06'
_TERM = ';'
_ERROR = _STX + 'ERR'

# Roland identifiers for specific channels
_INPUT_IDS = ['I{0}'.format(i+1) for i in range(_NUM_INPUTS)]
_AUX_IDS = ['AX{0}'.format(a+1) for a in range(_NUM_AUXES)]


def _level2str(level):
    level = float(level)
    if level < mixer.Mixer._MIN_LEVEL:
        return 'INF'
    if level < -80.0:
        return '-80.0'  # THINK ABOUT THIS!!!
    if level > 10.0:
        return '10.0'
    return '{0:0.1f}'.format(level)


def _str2level(levelstr):
    try:
        if levelstr == 'INF':
            raise ValueError
        level = float(levelstr)
        level = max(mixer.Mixer._MIN_LEVEL, level)  # improve this!! TODO
        level = min(mixer.Mixer._MAX_LEVEL, level)
        return level
    except ValueError:
        return mixer.Mixer._MIN_LEVEL


class RolandVMixer(mixer.Mixer):

    def _writereq(self, cmd, params=[]):
        paramstr = ':' + ','.join(map(str, params)) if params else ''
        req = ''.join((_STX, cmd, paramstr, ';'))
        self._port.write(req.encode('utf-8'))

    def _readres(self):
        res = ''
        while res[-1:] not in (_ACK, _TERM):
            res += self._port.read().decode('utf-8')
        return res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')

    def getinputlevel(self, num):
        inputid = 'I{0}'.format(num)
        self._writereq('FDQ', [inputid])
        res = self._readres()
        return {'level': _str2level(res[2])}

    def setinputlevel(self, num, level):
        inputid = 'I{0}'.format(num)
        levelstr = _level2str(level)
        print(level, levelstr)
        self._writereq('FDC', [inputid, levelstr])
        res = self._readres()
        return self.getinputlevel(num)

    def __init__(self, port='/dev/ttyAMA0'):
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = 115200
        self._port.xonxoff = True
        self._port.timeout = 1.0
        self._port.open()