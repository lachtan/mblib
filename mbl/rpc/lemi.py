import re
import cjson as json
from threading import RLock
from datetime import datetime
from random import randint
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
	SIGNAL_TID = '~~signal~~'


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
		data = inputStream.read(dataSize)
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
# Transaction
# ------------------------------------------------------------------------------

class Transaction(object):
	OPEN = 'open'
	DONE = 'done'


	def __init__(self, tid, timeout):
		self.__response = None
		self.__state = Transaction.OPEN
		self.__timeout = timeout
		self.__createTime = time()


	def tid(self):
		return self.__request.tid()


	def setResponse(self, response):
		if self.isDone():
			return
		self.__state = Transaction.DONE
		self.__response = response
		self.__doneTime = time()


	def response(self):
		return self.__response


	def isDone(self):
		return self.__state == Transaction.DONE


	def doneAge(self):
		return time() - self.__doneTime


	def __cmp__(self, other):
		return cmp(self.doneAge(), other.doneAge())


	def isTimeout(self):
		return (time() - self.__createTime) > self.__timeout


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
#
# ------------------------------------------------------------------------------

class TransactionTable(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.setDaemon()
		self.__openTransaction = SyncHash()
		self.__doneTransaction = SyncHash()
		self.__tidGenerator = TidGenerator()


	def createTransaction(self, timeout):
		tid = self.__tidGenerator.get()
		transaction = Transaction(tid, timeout)
		self.__openTransaction.put(tid, transaction)
		return transaction


	def setResponse(self, packet) {
		tid = packet.tid()
		transaction = self.__openTransaction.remove(tid)
		if transaction:
			transaction.setResponse(packet.data())
			self.__doneTransaction[tid] = transaction


	def getResponse(self, tid, timeout):
		transaction = self.__doneTransaction.remove(tid, timeout)
		if transaction:
			return transaction.getResponse()
		else:
			return None


	def __deleteTimeoutedTransactions(self):
		for tid, transaction in self.__openTransaction.itmes():
			if transaction.isTimeout():
				self.__openTransaction.remove(tid)


	def __deleteForgottenTransactions(self):
		for tid, transaction in self.__doneTransaction.itmes():
			if transaction.getDoneAge() > maxDoneWaitTime:
				self.__doneTransaction.remove(tid)


	def __deleteOldDoneTransaction(self):
		if len(self.__doneTransaction) < self.__maxDoneCount:
		transactions = self.__doneTransaction.values()
		transactions.sort()
		for index in xrange(self.__maxDoneCount, len(transactions)):
			transaction = transactions[index]
			tid = transaction.tid()
			self.__doneTransaction.remove(tid)


	def run(self):
		while True:
			self.iteration()


	def iteration(self):
		self.__deleteTimeoutedTransactions()
		self.__deleteForgottenTransactions()
		self.__deleteOldDoneTransaction()
		sleep(1.0)


# ------------------------------------------------------------------------------
# LemiCamel
# ------------------------------------------------------------------------------

class LemiCamel(Thread):
	def __init__(self, packetReceiver, packetSender, transactions):
		Thread.__init__(self)
		self.setDaemon()
		self.__transactions = transactions
		self.__packetReceiver = packetReceiver
		self.__packetSender = packetSender
		self.__requests = Queue()


	# --------------------------------------------------------------------------
	# Client side
	# --------------------------------------------------------------------------

	def sendRequest(self, data, timeout = Timeout.BLOCK):
		""" Send request to server """
		transaction = self.__transactions.createTransaction(timeout)
		tid = transaction.tid()
		packet = Packet(Packet.RESPONSE, tid, data)
		self.__packetSender.put(packet)
		return tid


	def sendSignal(self, data):
		""" Send signal to server """
		packet = Packet(Packet.SIGNAL, None, data)
		self.__packetSender.put(packet)


	def getResponse(self, tid, timeout = Timeout.BLOCK):
		""" Receive response from server """
		return self.__transactions.getResponse(tid, timeout)


	# --------------------------------------------------------------------------
	# Server side
	# --------------------------------------------------------------------------

	def getRequest(self):
		""" Get request for processing """
		packet = self.__requests.get()
		return packet.tid(), packet.data()


	def sendResponse(self, tid, data):
		""" Send response for processed request """
		packet = Packet(Packet.RESPONSE, tid, data)
		self.__packetSender.put(packet)


	# --------------------------------------------------------------------------
	#
	# --------------------------------------------------------------------------

	def run(self):
		while True:
			self.iteration()


	def iteration(self):
		packet = self.__packetReceiver.get()
		packetType = packet.type()
		if packetType in (Packet.REQUEST, Packet.SIGNAL):
			self.__requests.put(packet):
		elif packetType == Packet.RESPONSE:
			self.__transactions.setResponse(packet)
		else:
			# Neznamy typ packetu
			pass
