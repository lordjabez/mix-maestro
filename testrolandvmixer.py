"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer test interface for Mix Maestro.
"""


# Standard library imports
import logging
import queue
import threading
import time

# Additional library imports
import serial

# Mix Maestro imports
import mixer
import rolandvmixer


# Named logger for this module
_logger = logging.getLogger(__name__)


class TestRolandVMixer(mixer.Mixer):

    def _readrequests(self):
        while True:
            req = ''
            while req[-1:] not in (rolandvmixer._ACK, rolandvmixer._TERM):
                req += self._port.read().decode('utf-8')
            self._requestqueue.put(rolandvmixer._decoderes(req))
    
    def _processrequests(self):
         while True:
            cmd, data = self._requestqueue.get()
            if cmd == 'FDC':
                cid, level = data
                params = {'level': rolandvmixer._decodelevel(level)}
                item, num = _decodeid(cid)
                if item == 'channel':
                    self._channels[num].update(params)
                elif item == 'aux':
                    self._auxes[num].update(params)
                self._responsequeue.put(rolandvmixer._ACK.encode('utf-8'))
            elif cmd == 'AXC':
                cid, aid, pan, level = data
                params = {'pan': rolandvmixer._decodepan(pan), 'level': rolandvmixer._decodelevel(level)}
                citem, cnum = _decodeid(cid)
                if citem == 'channel':
                    aitem, anum = _decodeid(aid)
                    if aitem == 'aux':
                        self._channels[cnum]['auxes'][anum].update(params)
                self._responsequeue.put(rolandvmixer._ACK.encode('utf-8'))
            elif cmd == 'CNQ':
                id, = data
                item, num = rolandvmixer._decodeid(id)
                if item == 'channel':
                    name = self._channels[num].get('name', '      ')
                elif item == 'aux':
                    name = self._auxes[num].get('name', '      ')
                self._responsequeue.put(rolandvmixer._encodereq('CNS', [id, name]))
            elif cmd == 'FDQ':
                id, = data
                item, num = rolandvmixer._decodeid(id)
                if item == 'channel':
                    levelstr = rolandvmixer._encodelevel(self._channels[num].get('level', -100.0))
                elif item == 'aux':
                    levelstr = rolandvmixer._encodelevel(self._auxes[num].get('level', -100.0))
                self._responsequeue.put(rolandvmixer._encodereq('FDS', [cid, levelstr]))
            elif cmd == 'AXQ':
                cid, aid = data
                citem, cnum = _decodeid(cid)
                if citem == 'channel':
                    aitem, anum = _decodeid(aid)
                    if aitem == 'aux':
                        levelstr = rolandvmixer._encodelevel(self._channels[cnum]['auxes'][anum].get('level', -100.0))
                        panstr = rolandvmixer._encodepan(self._channels[cnum]['auxes'][anum].get('pan', 0.0))
                        self._responsequeue.put(rolandvmixer._encodereq('AXS', [cid, aid, levelstr, panstr]))

    def _writeresponses(self):
        while True:
            self._port.write(self._responsequeue.get())

    def __init__(self, port):
        super().__init__(rolandvmixer._ids)
        self._requestqueue = queue.Queue()
        self._responsequeue = queue.Queue()
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = 115200
        self._port.xonxoff = True
        self._port.timeout = 1.0
        try:
            self._port.open()
            threading.Thread(target=self._writeresponses).start()
            threading.Thread(target=self._processrequests).start()
            threading.Thread(target=self._readrequests).start()
            _logger.info('Initialized interface at ' + port)
        except serial.SerialException:
            _logger.error('Unable to initialize interface at port ' + port)
