"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides the HTTP server for Mix Maestro.
"""


# Standard library imports
import threading

# Additional library imports
import bottle


# Increase the maximum body size allowed by bottle
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

# Mixer object storage
_mixer = {}

# Regular expressions that define a legal channel number and list of numbers
_numregex = '[0-9]+'
_numsregex = '[0-9]+(,[0-9]+)*'


@bottle.get('/mixer')
def _getmixer():
    return _mixer['mixer'].getmixer()


@bottle.get('/inputs')
@bottle.get('/inputs/<inums:re:{0}>'.format(_numsregex))
def _getinputs(inums=None):
    return _mixer['mixer'].getinputs(inums)


@bottle.get('/auxes')
@bottle.get('/auxes/<anums:re:{0}>'.format(_numsregex))
def _getinputs(anums=None):
    return _mixer['mixer'].getauxes(anums)


@bottle.get('/auxes/<anum:re:{0}>/inputs'.format(_numregex))
@bottle.get('/auxes/<anum:re:{0}>/inputs/<inums:re:{1}>'.format(_numregex, _numsregex))
def _getauxesinputs(anum, inums=None):
    return _mixer['mixer'].getauxinputs(anum, inums)


@bottle.put('/inputs')
@bottle.put('/inputs/<inums:re:{0}>'.format(_numsregex))
def _putinputs(inums=None):
    _mixer['mixer'].setinputs(inums, bottle.request.json)


@bottle.put('/auxes')
@bottle.put('/auxes/<anums:re:{0}>'.format(_numsregex))
def _putauxes(anums=None):
    _mixer['mixer'].setauxes(anums, bottle.request.json)


@bottle.put('/auxes/<anum:re:{0}>/inputs'.format(_numregex))
@bottle.put('/auxes/<anum:re:{0}>/inputs/<inums:re:{1}>'.format(_numregex, _numsregex))
def _putauxesinputs(anum, inums=None):
    _mixer['mixer'].setauxinputs(anum, inums, bottle.request.json)


@bottle.get('/')
@bottle.get('/<filename:path>')
def _getfile(filename='index.html'):
    return bottle.static_file(filename, root='web')


def start(mixer):
    """
    Initializes the module.
    @param mixer: The mixer object into which the interface functions will call.
    """
    _mixer['mixer'] = mixer
    kwargs = {'host': '0.0.0.0', 'port': 80, 'debug': False, 'quiet': True}
    threading.Thread(target=bottle.run, kwargs=kwargs).start()
