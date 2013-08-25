"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Provides the HTTP server for the Roland V-Mixer interface.
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


@bottle.get('/channels/<id>')
def _getchannel(id):
    """Pass get request into the mixer interface."""
    return mixer.getchannel(id)


@bottle.put('/channels/<id>')
def _setchannel(id):
    """Pass set request into the mixer interface."""
    return mixer.setchannel(id, bottle.request.json)


def _run():
    """Executes the webserver and never returns."""
    bottle.run(host=_host, port=_port)


def start():
    """Initializes the module."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
    threading.Thread(target=_run).start()
