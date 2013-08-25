"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides a generic mixer API for the Roland V-Mixer interface.
"""


# Standard library imports
import binascii
import logging

# Additional library imports
import serial


# Named logger for this module
_logger = logging.getLogger(__name__)

# The serial port object
_port = serial.Serial()

# Codes for command transmission
_STX = '\x02'
_ACK = '\x06'
_TERM = ';'
_ERROR = _STX + 'ERR'


#input
#return
#aux
#matrix
#main
#dca
#user

def _getparams(data):
    params = data.split(':')[1].strip(';')
    return params.split(',')


def getchannel(id):
    command = _STX + 'FDQ:{0};'.format(id.upper())
    _port.write(command.encode('utf-8'))
    data = ''
    while data[-1:] not in (_ACK, _TERM):
        data += _port.read().decode('utf-8')
    if data[:4] != _ERROR:
        fader = _getparams(data)[0]
        values = {'id': id, 'fader': fader}
        return values
    else:
        return None


def setchannel(id, values):
    command = _STX + 'FDC:{0};'.format(id.upper())
    _port.write(command.encode('utf-8'))
    data = ''
    while data[-1:] not in (_ACK, _TERM):
        data += _port.read().decode('utf-8')
    if data == _ACK:
        return getchannel(id)
    else:
        return None


def start():
    """Initializes the module."""
    _port.baudrate = 115200
    _port.port = 'COM4'
    _port.xonxoff = True
    _port.timeout = 1.0
    _port.open()
    _logger.info('Initialized serial port: ' + repr(_port))