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


# Named logger for this module
_logger = logging.getLogger(__name__)

# Codes for command transmission
_STX = '\x02'
_ACK = '\x06'
_TERM = ';'
_ERROR = _STX + 'ERR'

# The serial port object
_port = serial.Serial()

# The data object itself
_data = {}
_data['channels'] = {}
_data['settings'] = {}
# TODO _data['channels']['inputs'] = []
#_data['channels']['returns'] = []
#_data['channels']['auxes'] = []
#_data['channels']['matrices'] = []
#_data['channels']['mains'] = []


def processreq(cmd, params=[]):
    req = _STX + cmd
    if params:
        req += ':' + ','.join(map(str, params))
    req += ';'
    _port.write(req.upper().encode('utf-8'))
    res = ''
    while res[-1:] not in (_ACK, _TERM):
        res += _port.read().decode('utf-8')
    return res


def isack(res):
    return res == _ACK


def iserror(res):
    return res[:4] == _ERROR


def _getparams(res):
    params = res.split(':')[1].strip(';')
    return params.split(',')


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


def _run():
    _data['channels']['inputs'] = []
    for i in range(24):
        inputid = 'I{0}'.format((i+1))
        inputdata = {}
        inputdata['level'] = getlevel(inputid)
        inputdata['auxes'] = []
        for a in range(7):
            auxid = 'AX{0}'.format((a+1))
            auxdata = {}
            auxdata['level'] = getauxlevel(inputid, auxid)
            inputdata['auxes'].append(auxdata)
        _data['channels']['inputs'].append(inputdata)
        print('Finished channel ', i)
    print(_data)


def getmixer():
    return _data


def start(port='/dev/ttyAMA0'):
    _port.port = port
    _port.baudrate = 115200
    _port.xonxoff = True
    _port.timeout = 1.0
    _port.open()
    threading.Thread(target=_run).start()