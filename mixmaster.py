"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Main module for the Roland V-Mixer interface.
"""


# Standard library imports
import logging

# Application imports
import mixer
import httpserver


# Configure the logging module.
_logformat = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
logging.basicConfig(format=_logformat, level=logging.INFO)

# Start the application components.
mixer.start()
httpserver.start()
