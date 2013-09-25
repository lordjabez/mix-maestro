"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides a mixer API for Mix Maestro.
"""


# Standard library imports
import logging


# Named logger for this module
_logger = logging.getLogger(__name__)


def _getlist(nums):
    if type(nums) is str:
        return (int(n) for n in nums.split(','))


class Mixer:
    """Abstract class from which all other mixer classes inherit."""

    MIN_LEVEL = -100.0
    MAX_LEVEL = 20.0

    def _updateinput(self, i, params):
        self._inputs[i].update(params)    

    def _updateaux(self, a, params):
        self._auxes[a].update(params)

    def _updateauxinput(self, a, i, params):
        self._inputs[i]['auxes'][a].update(params)

    def getmixer(self):
        """
        Provide all mixer values.
        @return: Dictionary containing the entire mixer structure
        """
        mixer = {
            'inputs': self._inputs,
            'returns': self._returns,
            'auxes': self._auxes,
            'matrices': self._matrices,
            'groups': self._groups,
            'mains': self._mains,
            'settings': self._settings
        }
        return mixer

    def getsettings(self):
        """
        Provide mixer settings.
        @return: Dictionary containing the mixer settings
        """
        return self._settings

    def getinputs(self, inums):
        """
        Provide information for a set of input channels.
        @param inums: String containing a comma-separated list of input identifiers
        @return: Dictionary containing the mixer settings
        """
        ilist = _getlist(inums) or self._inputs.keys()
        return {i: self._inputs[i] for i in ilist}

    def getauxes(self, anums):
        """
        Provide information for a set of aux channels.
        @param anums: String containing a comma-separated list of aux identifiers
        @return: Dictionary containing the mixer settings
        """
        alist = _getlist(anums) or self._auxes.keys()
        return {a: self._auxes[a] for a in alist}
            
    def getauxinputs(self, anum, inums):
        """
        Provide information for a set of inputs channels going to an aux channel.
        @param anum: Identifies a particular aux channel
        @param inums: String containing a comma-separated list of input identifiers
        @return: Dictionary containing the mixer settings
        """
        ilist = _getlist(inums) or self._inputs.keys()
        a = int(anum)
        auxinputs = {i: self._inputs[i]['auxes'][a] for i in ilist}
        for i, inp in auxinputs.items():
            inp['name'] = self._inputs[i].get('name', '')
        return {'name': self._auxes[a]['name'], 'inputs': auxinputs}
    
    def setinputs(self, inums, params):
        """
        Update information on a set of input channels.
        @param inums: String containing a comma-separated list of input identifiers
        @param params: Dictionary of data to update
        """
        ilist = _getlist(inums) or self._inputs.keys()
        for i in ilist:
            self._updateinput(i, params)

    def setauxes(self, anums, params):
        """
        Update information on a set of aux channels.
        @param anums: String containing a comma-separated list of aux identifiers
        @param params: Dictionary of data to update
        """
        alist = _getlist(anums) or self._auxes.keys()
        for a in alist:
            self._updateaux(a, params)

    def setauxinputs(self, anum, inums, params):
        """
        Update information on a set of inputs channels for an aux channel.
        @param anum: Identifies a particular aux channel
        @param inums: String containing a comma-separated list of input identifiers
        @param params: Dictionary of data to update
        @return: Dictionary containing the mixer settings
        """
        ilist = _getlist(inums) or self._inputs.keys()
        a = int(anum)
        for i in ilist:
            self._updateauxinput(a, i, params)

    def __init__(self, ids):
        self._inputs = {i: {} for i in ids['inputs']}
        for i in self._inputs:
            self._inputs[i]['auxes'] = {a: {} for a in ids['auxes']}
        self._returns = {r: {} for r in ids['returns']}
        self._auxes = {a: {} for a in ids['auxes']}
        self._matrices = {t: {} for t in ids['matrices']}
        self._groups = {g: {} for g in ids['groups']}
        self._mains = {m: {} for m in ids['mains']}
        self._settings = {}

