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

    _MIN_LEVEL = -100.0
    _MAX_LEVEL = 20.0

    def _updateinput(self, i, params):
        self._inputs[i].update(params)    

    def _updateaux(self, a, params):
        self._auxes[a].update(params)

    def _updateauxinput(self, a, i, params):
        self._input[i]['auxes'][a].update(params)

    def getmixer(self):
        mixer = {}
        mixer['inputs'] = self._inputs
        mixer['returns'] = self._returns
        mixer['auxes'] = self._auxes
        mixer['matrices'] = self._matrices
        mixer['groups'] = self._groups                                                       
        mixer['mains'] = self._mains
        mixer['settings'] = self._settings
        return mixer

    def getsettings(self):
        return self._settings

    def getinputs(self, inums):
        ilist = _getlist(inums)
        return {i: self._inputs[i] for i in ilist} if ilist else self._inputs

    def getauxes(self, anums):
        alist = _getlist(anums)
        return {a: self._auxes[a] for a in alist} if alist else self._auxes
            
    def getauxinputs(self, anum, inums):
        ilist = _getlist(inums) if inums else self._inputs.keys()
        a = int(anum)
        return {i: self._inputs[i]['auxes'][a] for i in ilist}
    
    def setinputs(self, inums, params):
        ilist = _getlist(inums) if inums else self._inputs.keys()
        for i in ilist:
            self._updateinput(i, params)

    def setauxes(self, anums, params):
        alist = _getlist(anums) if anums else self._auxes.keys()
        for a in alist:
            self._updateaux(a, params)

    def setauxinputs(self, anum, inums, params):
        ilist = _getlist(inums) if inums else self._inputs.keys()
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
