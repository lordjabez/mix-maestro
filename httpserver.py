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
def _getmixer():
    return _mixer['mixer'].getmixer()


@bottle.get('/channels')
@bottle.get('/channels/<inums>')
def _getchannels(cnums=None):
    return _mixer['mixer'].getchannels(cnums)


@bottle.get('/auxes')
@bottle.get('/auxes/<anums>')
def _getchannels(anums=None):
    return _mixer['mixer'].getauxes(anums)


@bottle.get('/auxes/<anum>/channels')
@bottle.get('/auxes/<anum>/channels/<inums>')
def _getauxeschannels(anum, cnums=None):
    return _mixer['mixer'].getauxchannels(anum, cnums)


# TODO more here

@bottle.get('/settings')
def _getsettings():
    return _mixer['mixer'].getsettings()






@bottle.put('/channels')
@bottle.put('/channels/<inums>')
def _putchannels(cnums=None):
    _mixer['mixer'].setchannels(inums, bottle.request.json)



#@bottle.put('/auxes')
#@bottle.put('/auxes/<num>')
#@bottle.put('/auxes/channels')
#@bottle.put('/auxes/channels/<num>')





@bottle.get('/')
@bottle.get('/<filename:path>')
def _getfile(filename='index.html'):
    return bottle.static_file(filename, root='web')






# TODO consolidate this with kwargs
def _run():
    """Executes the webserver and never returns."""
    bottle.run(host='0.0.0.0', port=80)


def start(mixer):
    """Initializes the module."""
    _mixer['mixer'] = mixer
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
    threading.Thread(target=_run).start()
