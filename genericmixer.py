"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Generic mixer interface for Mix Maestro.
"""


# Standard library imports
import logging

# Mix Maestro imports
import mixer


# Named logger for this module
_logger = logging.getLogger(__name__)


# Info on the mixer
_NUM_INPUTS = 48
_NUM_RETURNS = 6
_NUM_AUXES = 16
_NUM_MATRICES = 8
_NUM_GROUPS = 24
_NUM_MAINS = 3

# Generic channel ID information to pass to the mixer object
_ids = {
    'inputs': [i + 1 for i in range(_NUM_INPUTS)],
    'returns': [r + 1 for r in range(_NUM_RETURNS)],
    'auxes': [a + 1 for a in range(_NUM_AUXES)],
    'matrices': [t + 1 for t in range(_NUM_MATRICES)],
    'groups': [g + 1 for g in range(_NUM_GROUPS)],
    'mains': [m + 1 for m in range(_NUM_MAINS)]
}


class GenericMixer(mixer.Mixer):
    """Provide a generic mixer class that's useful for testing."""

    def __init__(self):
        super().__init__(_ids)
        _logger.info('Initialized interface')
        for i, inp in self._inputs.items():
            inp['name'] = 'INP{0:02}'.format(i)
            inp['level'] = -(i + 0.99)
            for a, aux in inp['auxes'].items():
                aux['level'] = -(i + a / 100.0)
        for a, aux in self._auxes.items():
            aux['name'] = 'AUX{0:02}'.format(a)
            aux['level'] = -(a + 0.98)
