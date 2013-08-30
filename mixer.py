"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides a generic mixer API.
"""


# Named logger for this module
_logger = logging.getLogger(__name__)


class Mixer:

    def getinput(num):
        return self._mixer['channels']['inputs'].get(num, None)

    def getaux(num):
        return self._mixer['channels']['auxes'].get(num, None)
    
    def setinput(num, params):
        self._mixer['channels']['inputs'][num] = params

    def setaux(num, params):
        self._mixer['channels']['auxes'][num] = params
        
    def __init__(numinputs, numauxes):
        self._numinputs = numinputs
        self._numauxes = numauxes
        self._mixer = {}
        self._mixer['channels'] = {}
        self._mixer['settings'] = {}
        self._mixer['channels']['inputs'] = {}
        self._mixer['channels']['returns'] = {}
        self._mixer['channels']['auxes'] = {}
        self._mixer['channels']['matrices'] = {}
        self._mixer['channels']['dcas'] = {}
        self._mixer['channels']['mains'] = {}