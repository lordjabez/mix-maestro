"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Main module for Mix Maestro.
"""


# Standard library imports
import argparse
import logging
import sys

# Application imports
import httpserver

# Parse the command line parameters
_parser = argparse.ArgumentParser()
_parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='enable debug logging')
_parser.add_argument('-m', '--mixer', default='GenericMixer', help='mixer module to use')
_parser.add_argument('-p', '--port', help='serial port used by the mixer module')
_args = _parser.parse_args()

# Configure the logging module.
_logformat = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
_loglevel = logging.DEBUG if _args.debug else logging.INFO
logging.basicConfig(format=_logformat, level=_loglevel)

# Initialize the mixer object depending on command line parameters.
mixer = __import__(_args.mixer.lower())
Mixer = getattr(mixer, _args.mixer)
if _args.port:
    _mixer = Mixer(_args.port)
else:
    _mixer = Mixer()

# Start the application components
httpserver.start(_mixer)
