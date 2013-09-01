"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides the HTTP server for Mix Maestro.
"""


# Standard library imports
import threading

# Additional library imports
import bottle

# Application imports
import rolandvmixer


# Host and port number
_host = '0.0.0.0'
_port = 80

# Mixer object
_mixer = rolandvmixer.RolandVMixer()


@bottle.put('/mixer/channels/inputs/<num>')
def _putinput(num):
    data = bottle.request.json
    level = data['level']
    return _mixer.setinputlevel(num, level)


@bottle.get('/<filename:path>')
def _getfile(filename):
    return bottle.static_file(filename, root='web')


@bottle.get('/')
def _index():
    return bottle.static_file('index.html', root='web')


def _run():
    """Executes the webserver and never returns."""
    bottle.run(host=_host, port=_port)


def start():
    """Initializes the module."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
    threading.Thread(target=_run).start()
