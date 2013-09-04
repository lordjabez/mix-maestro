"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Generic test mixer interface for Mix Maestro.
"""


# Standard library imports
import logging
import os
import queue
import threading

# Additional library imports
import serial

# Mix Maestro imports
import mixer


# Named logger for this module
_logger = logging.getLogger(__name__)


# Info on the mixer
_NUM_CHANNELS = 8
_NUM_RETURNS = 2
_NUM_AUXES = 2
_NUM_MATRICES = 1
_NUM_GROUPS = 2
_NUM_MAINS = 2

# Generic channel ID information to pass to the mixer object
_ids = {}
_ids['channels'] = [c + 1 for c in range(_NUM_CHANNELS)]
_ids['returns'] = [r + 1 for r in range(_NUM_RETURNS)]
_ids['auxes'] = [a + 1 for a in range(_NUM_AUXES)]
_ids['matrices'] = [t + 1 for t in range(_NUM_MATRICES)]
_ids['groups'] = [g + 1 for g in range(_NUM_GROUPS)]
_ids['mains'] = [m + 1 for m in range(_NUM_MAINS)]


class TestMixer(mixer.Mixer):

    def __init__(self):
        super().__init__(_ids)
        _logger.info('Initialized interface')
