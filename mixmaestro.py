"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Main module for Mix Maestro.
"""


# Standard library imports
import logging

# Application imports
import httpserver
import mixer


# Configure the logging module.
_logformat = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
logging.basicConfig(format=_logformat, level=logging.INFO)


# Initialize the mixer object
_ids = {}
_ids['channels'] = list(map(str, range(1, 49)))
_ids['returns'] = list(map(str, range(1, 7)))
_ids['auxes'] = list(map(str, range(1, 17)))
_ids['matrices'] = list(map(str, range(1, 9)))
_ids['groups'] = list(map(str, range(1, 25)))
_ids['mains'] = list(map(str, range(1, 4)))
_mixer = mixer.Mixer(_ids)

# Start the application components
httpserver.start(_mixer)
