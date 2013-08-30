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

# The serial port object
_port = serial.Serial()


class RolandVMixer(mixer.Mixer):
    def __init__():


def writereq(cmd, params=[]):
    req = _STX + cmd
    if params:
        req += ':' + ','.join(map(str, params))
    req += ';'
    _port.write(req.encode('utf-8'))


def readres():
    res = ''
    while res[-1:] not in (_ACK, _TERM):
        res += _port.read().decode('utf-8')
    return res.strip(_STX + _ACK + _TERM).replace(':', ',').split(',')


def isack(res):
    return res == _ACK


def iserror(res):
    return res[:4] == _ERROR


def getlevel(id):
    res = processreq('FDQ', [id])
    if not iserror(res):
        level = _getparams(res)[1]
        if level == 'INF':
            return -100.0
        else:
            return level
    else:
        return None


def getauxlevel(id, aux):
    res = processreq('AXQ', [id, aux])
    if not iserror(res):
        level = _getparams(res)[2]
        if level == 'INF':
            return -100.0
        else:
            return level
    else:
        return None


def _writedata():
    for i in _INPUT_IDS:
        writereq('FDQ', [i])
        for a in _AUX_IDs
            writereq('AXQ', [i, a])


def _readdata():
    while True:
        res = readres()
        if res[0] == 'FDS':
            channelinput = mixer['channels']['inputs'].get(res[1], {})
            channelinput['level'] = res[2]
            mixer['channels']['inputs'][res[1]] = channelinput
        elif res[0] == 'AXS':
            channelinput = mixer['channels']['inputs'].get(res[1], {})
            channelinput.get('auxes')['level'] = res[2]
            channelaux = 
            
            # save aux level
        else
            pass # not yet implemented


def getmixer():
    return mixer


def start(port='/dev/ttyAMA0'):
    _port.port = port
    _port.baudrate = 115200
    _port.xonxoff = True
    _port.timeout = 1.0
    _port.open()
    #threading.Thread(target=_writedata).start()
    threading.Thread(target=_readdata).start()


# TODO REMOVE (for windows testing only)
if __name__ == "main":
    start('COM1')
