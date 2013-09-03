"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides the HTTP server for Mix Maestro.
"""


# Standard library imports
import threading

# Additional library imports
import bottle

# Application imports
import mixer


# Mixer object (TODO improve this)
_mixer = {}


@bottle.get('/mixer')
def _getchannels(cnums=None):
    return _mixer['mixer'].getmixer()


@bottle.get('/channels')
@bottle.get('/channels/<cnums>')
def _getchannels(cnums=None):
    return _mixer['mixer'].getchannels(cnums)


@bottle.get('/auxes')
@bottle.get('/auxes/<anums>')
def _getchannels(anums=None):
    return _mixer['mixer'].getauxes(anums)


@bottle.get('/auxes/<anum>/channels')
@bottle.get('/auxes/<anum>/channels/<cnums>')
def _getauxeschannels(anum, cnums=None):
    return _mixer['mixer'].getauxchannels(anum, cnums)


@bottle.put('/channels')
@bottle.put('/channels/<cnums>')
def _putchannels(cnums=None):
    _mixer['mixer'].setchannels(cnums, bottle.request.json)


@bottle.put('/auxes')
@bottle.put('/auxes/<anums>')
def _putauxes(anums=None):
    _mixer['mixer'].setauxes(anums, bottle.request.json)


@bottle.put('/auxes/<anum>/channels')
@bottle.put('/auxes/<anum>/channels/<cnums>')
def _putauxeschannels(anum, cnums=None):
    _mixer['mixer'].setauxchannels(anum, cnums, bottle.request.json)


@bottle.get('/')
@bottle.get('/<filename:path>')
def _getfile(filename='index.html'):
    return bottle.static_file(filename, root='web')


def start(mixer):
    """Initializes the module."""
    _mixer['mixer'] = mixer
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
    kwargs = {'host': '0.0.0.0', 'port': 80, 'debug': False, 'quiet': True}
    threading.Thread(target=bottle.run, kwargs=kwargs).start()
