"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Roland V-Mixer test interface for Mix Maestro.
"""


# Standard library imports
import logging
import queue
import threading

# Additional library imports
import serial

# Mix Maestro imports
import mixer
import rolandvmixer


# Named logger for this module
_logger = logging.getLogger(__name__)


class TestRolandVMixer(mixer.Mixer):
    """This special mixer class is used to test the Roland V-Mixer class."""

    def _readrequests(self):
        while True:
            req = ''
            while req[-1:] not in (rolandvmixer._ACK, rolandvmixer._TERM):
                req += self._port.read().decode('utf-8')
            _logger.debug('Received {0} from {1}'.format(req.encode(), self._port.port))
            self._requestqueue.put(rolandvmixer._decoderes(req))

    def _processrequests(self):
        while True:
            cmd, data = self._requestqueue.get()
            if cmd == 'FDC':
                iid, level = data
                params = {'level': rolandvmixer._decodelevel(level)}
                item, num = rolandvmixer._decodeid(iid)
                if item == 'input':
                    self._inputs[num].update(params)
                elif item == 'aux':
                    self._auxes[num].update(params)
                self._responsequeue.put(rolandvmixer._ACK.encode())
            elif cmd == 'AXC':
                iid, aid, level, pan = data
                params = {'pan': rolandvmixer._decodepan(pan), 'level': rolandvmixer._decodelevel(level)}
                iitem, inum = rolandvmixer._decodeid(iid)
                if iitem == 'input':
                    aitem, anum = rolandvmixer._decodeid(aid)
                    if aitem == 'aux':
                        self._inputs[inum]['auxes'][anum].update(params)
                self._responsequeue.put(rolandvmixer._ACK.encode())
            elif cmd == 'CNQ':
                xid, = data
                item, num = rolandvmixer._decodeid(xid)
                if item == 'input':
                    name = self._inputs[num].get('name', '      ')
                elif item == 'aux':
                    name = self._auxes[num].get('name', '      ')
                else:
                    name = '      '
                self._responsequeue.put(rolandvmixer._encodereq('CNS', [xid, name]))
            elif cmd == 'FDQ':
                xid, = data
                item, num = rolandvmixer._decodeid(xid)
                if item == 'input':
                    levelstr = rolandvmixer._encodelevel(self._inputs[num].get('level', -100.0))
                elif item == 'aux':
                    levelstr = rolandvmixer._encodelevel(self._auxes[num].get('level', -100.0))
                else:
                    levelstr = rolandvmixer._encodelevel(-100.0)
                self._responsequeue.put(rolandvmixer._encodereq('FDS', [xid, levelstr]))
            elif cmd == 'AXQ':
                iid, aid = data
                iitem, inum = rolandvmixer._decodeid(iid)
                if iitem == 'input':
                    aitem, anum = rolandvmixer._decodeid(aid)
                    if aitem == 'aux':
                        levelstr = rolandvmixer._encodelevel(self._inputs[inum]['auxes'][anum].get('level', -100.0))
                        panstr = rolandvmixer._encodepan(self._inputs[inum]['auxes'][anum].get('pan', 0.0))
                        self._responsequeue.put(rolandvmixer._encodereq('AXS', [iid, aid, levelstr, panstr]))

    def _writeresponses(self):
        while True:
            res = self._responsequeue.get()
            self._port.write(res)
            _logger.debug('Sent {0} to {1}'.format(res, self._port.port))

    def __init__(self, port):
        super().__init__(rolandvmixer._ids)
        self._requestqueue = queue.Queue()
        self._responsequeue = queue.Queue()
        self._port = serial.Serial()
        self._port.port = port
        self._port.baudrate = 115200
        self._port.xonxoff = True
        try:
            self._port.open()
            threading.Thread(target=self._writeresponses).start()
            threading.Thread(target=self._processrequests).start()
            threading.Thread(target=self._readrequests).start()
            _logger.info('Initialized interface at ' + port)
        except serial.SerialException:
            _logger.error('Unable to initialize interface at port ' + port)
