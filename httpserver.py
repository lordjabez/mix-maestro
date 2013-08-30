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


# Host and port number
_host = '0.0.0.0'
_port = 80

# Mixer object
_mixer = None


@bottle.get('/mixer')
def _getmixer():
    return rolandvmixer.getmixer()


@bottle.get('/<filename:path>')
def _getfile(filename):
    return bottle.static_file(filename, root='web')


@bottle.get('/')
def _index():
    return bottle.static_file('index.html', root='web')


def _run():
    """Executes the webserver and never returns."""
    bottle.run(host=_host, port=_port)


def start(mixer=mixer.Mixer()):
    """Initializes the module."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
    _mixer = mixer
    threading.Thread(target=_run).start()
