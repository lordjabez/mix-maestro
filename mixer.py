"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides a generic mixer API for the Roland V-Mixer interface.
"""


# Standard library imports
import logging

# Additional library imports
import serial


# Named logger for this module
_logger = logging.getLogger(__name__)

# The serial port object
_port = serial.Serial()


#input
#return
#aux
#matrix
#main


def get(channel, number):
    cmd = '\x02' + channel + number
    _port.write(cmd.encode('utf-8'))
    data = _port.read(1024)
    return data


def start():
    """Initializes the module."""
    _port.baudrate = 115200
    _port.port = 'COM4'
    _port.xonxoff = True
    _port.timeout = 1.0
    _port.open()
    _logger.info('Initialized serial port: ' + repr(_port))