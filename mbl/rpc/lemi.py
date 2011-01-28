import re
import cjson as json
from threading import Thread, RLock
from datetime import datetime
from random import randint
from types import StringType
from mbl.io import Timeout


# ------------------------------------------------------------------------------
# Packet
# ------------------------------------------------------------------------------

class Packet(object):
	REQUEST = 'request'
	SIGNAL = 'signal'
	RESPONSE = 'response'
	__TYPES = (
		SIGNAL,
		REQUEST,
		RESPONSE
	)


	def __init__(self, type, tid, data):
		self.__checkType(type)
		self.__checkData(data)
		if tid is None:
			self.__tid = Packet.SIGNAL
		else:
			self.__tid = tid
		self.__type = type
		self.__data = data


	def __checkType(self, type):
		if type not in self.__TYPES:
			raise AttributeError('Packet type %s is unknown' % type)


	def __checkData(self, data):
		if type(data) != StringType:
			raise AttributeError('Data must be string: %s' % str(type(data)))


	def __nonzero__(self):
		return True


	def tid(self):
		return self.__tid


	def type(self):
		return self.__type


	def data(self):
		return self.__data


	def __eq__(self, other):
		return self.__tid == other.tid()


	def __hash__(self):
		return hash(self.__tid)


# ------------------------------------------------------------------------------
# PacketReceiver
# ------------------------------------------------------------------------------

class PacketReceiver(object):
	def __init__(self, inputStream):
		self.__inputStream = LineBlocking(inputStream)


	def get(self):
		# asi by byl lepsi oddeleny parser ne?
		infoLine = inputStream.readLine().strip()
		match = re.match('^lemi\s+(%d)\s+(%d)$')
		if not match:
			raise
		totalSize = int(match.group(1))
		headerSize = int(match.group(2))
		# kontrola totalSize >= headerSize
		dataSize = totalSize - headerSize
		# cist to metodou a kontrolovat nactene velikosti
		header = inputStream.read(headerSize)
		header = json.decode(header)
		data = inputStream.read(dataSize)
		packet = Packet(header['tid'], header['type'], data)
		return packet


# ------------------------------------------------------------------------------
# PacketSender
# ------------------------------------------------------------------------------

class PacketSender(Thread):
	def __init__(self, outputStream, queueSize):
		Thread.__init__()
		self.setDaemon()
		self.__outputStream = outputStream
		self.__queue = Queue(queueSize)


	def put(self, packet):
		self.__queue.put(packet)


	def run(self):
		while True:
			self.iteration()


	def iteration(self):
		packet = self.__queue.get()
		self.__export(packet)


	def __export(self, packet):
		# chci oddelene aby slo testovat
		header = {
			'tid': packet.tid(),
			'type': packet.type()
		}
		header = json.encode(header)
		headerSize = len(header)
		dataSize = len(packet.data())
		totalSize = headerSize + dataSize
		infoLine = 'lemi %d %d' % (totalSize, headerSize)
		outputStream.writeLine(infoLine)
		outputStream.write(header)
		outputStream.write(data)


# ------------------------------------------------------------------------------
# TidGenerator
# ------------------------------------------------------------------------------

class TidGenerator(object):
	__digits = 6
	__mask = '%s~%0*d~%d'


	def __init__(self):
		self.__lock = RLock()
		self.__counter = 0


	def __inc(self):
		if self.__counter == 10 ** self.__digits:
			self.__counter = 0
		else:
			self.__counter += 1


	def get(self):
		self.__lock.acquire()
		args = (self._now(), self.__digits, self.__counter, self._random())
		tid = self.__mask % args
		self.__inc()
		self.__lock.release()
		return tid


	def _now(self):
		return datetime.now().isoformat().replace('T', '~')


	def _random(self):
		return randint(100000, 999999)


# ------------------------------------------------------------------------------
# LemiCamel
# ------------------------------------------------------------------------------

class LemiCamel(Thread):
	def __init__(self, packetReceiver, packetSender, requestHandler):
		Thread.__init__(self)
		self.setDaemon()
		self.__packetReceiver = packetReceiver
		self.__packetSender = packetSender
		self.__requestHandler = requestHandler
		self.__responseTable = EventDict()


	def call(self, data, timeout = Timeout.BLOCK):
		tid = self.__tid()
		self.__responseTable.create(tid)
		packet = Packet(Packet.RESPONSE, tid, request)
		self.__packetSender.put(packet)
		return self.__responseTable.pop(tid, timeout)


	def signal(self, data):
		tid = self.__tid()
		packet = Packet(Packet.SIGNAL, tid, data)
		self.__packetSender.put(packet)


	def run(self):
		while True:
			self.iteration()


	def iteration(self):
		packet = self.__packetReceiver.get()
		packetType = packet.type()
		if packetType == Packet.REQUEST:
			self.__putRequest(packet)
		if packetType == packet.SIGNAL:
			self.__putSignal(packet)
		elif packetType == Packet.RESPONSE:
			self.__response(packet)


	def __putRequest(self, packet):
		self.__requestHandler.request(self, packet.tid(), packet.data())


	def __putSignal(self, packet):
		self.__requestHandler.signal(self, packet.tid(), packet.data())


	def putResponse(self, tid, data):
		packet = Packet(Packet.RESPONSE, inPacket.tid(), response)
		self.__packetSender.put(packet)


	def __response(self, packet):
		self.__responseTable.put(packet.tid(), packet.data())

