"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides a mixer API for Mix Maestro.
"""


# Standard library imports
import logging


# Named logger for this module
_logger = logging.getLogger(__name__)


class Mixer:

    _MIN_LEVEL = -100.0
    _MAX_LEVEL = 20.0

    def getmixer(self):
        mixer = {}
        mixer['channels'] = self._channels
        mixer['returns'] = self._returns
        mixer['auxes'] = self._auxes
        mixer['matrices'] = self._matrices
        mixer['groups'] = self._groups
        mixer['mains'] = self._mains
        mixer['settings'] = self._settings
        return mixer

    def getsettings(self):
        return self._settings

    def getchannels(self, cnums):
        if cnums:
            cnumlist = cnums.split(',')
            return {c: self._channels[c] for c in cnumlist}
        else:
            return self._channels

    def getauxes(self, anums):
        if anums:
            anumlist = anums.split(',')
            return {a: self._auxes[a] for a in anumlist}
        else:
            return self._auxes
            
    def getauxchannels(self, anum, cnums):
        if cnums:
            cnumlist = cnums.split(',')
        else:
            cnumlist = self._channels.keys()
        return {c: self._channels[c]['auxes'][anum] for c in cnumlist}


    # TODO add validation to all set commands

    def setchannels(self, cnums, params):
        if cnums:
            cnumlist = cnums.split(',')
        else:
            cnumlist = self._channels.keys()
        for c in cnumlist:
            self._channels[c].update(params)

    def setauxes(self, anums, params):
        if anums:
            anumlist = anums.split(',')
        else:
            anumlist = self._auxes.keys()
        for a in anumlist:
            self._auxes[a].update(params)

    def setauxchannels(self, anum, cnums, params):
        if cnums:
            cnumlist = cnums.split(',')
        else:
            cnumlist = self._channels.keys()
        for c in cnumlist:
            self._channels[c]['auxes'][anum].update(params)

    def __init__(self, ids):
        self._channels = {c: {} for c in ids['channels']}
        for c in self._channels:
            self._channels[c]['auxes'] = {a: {} for a in ids['auxes']}
        self._returns = {r: {} for r in ids['returns']}
        self._auxes = {a: {} for a in ids['auxes']}
        self._matrices = {t: {} for t in ids['matrices']}
        self._groups = {g: {} for g in ids['groups']}
        self._mains = {m: {} for m in ids['mains']}
        self._settings = {}
