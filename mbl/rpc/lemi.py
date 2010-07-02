from threading import Lock

INFINITE_TIMEOUT = None
BLOCK = None

# ------------------------------------------------------------------------------
# TidGenerator
# ------------------------------------------------------------------------------

class TidGenerator(object):
	__digits = 6


	def __init__(self):
		self.__lock = Lock()
		self.__counter = 0


	def __inc(self):
		if self.__counter == 10 ** self.__digits:
			self.__counter = 0
		else:
			self.__counter += 1


	def get(self):
		self.__lock.acquire()
		tid = '%s~%0*d~%d' % (self._now(), self.__digits, self.__counter, self._random())		
		self.__inc()
		self.__lock.release()
		return tid
	
	
	def _now(self):
		return datetime.now().isoformat().replace('T', '~')
	
	
	def _random(self):
		return randint(100000, 999999)


# ------------------------------------------------------------------------------
# PacketReceiver
# ------------------------------------------------------------------------------

class PacketReceiver(PacketQueue):
	def __init__(self, inputStream, queueSize = 0):
		PacketQueue.__init__(self, queueSize)
		self.__inputStream = inputStream
	
	
	def iteration(self):
		packet = packetParser.parse(self.__inputStream)
		self.put(packet)
		# musi to nekam cpat
	

# ------------------------------------------------------------------------------
# PacketSender
# ------------------------------------------------------------------------------

class PacketSender(PacketQueue):
	def __init__(self, outputStream, queueSize = 0):
		PacketQueue.__init__(self, queueSize)
	
	
	def iteration(self):
		packet = self.get()
		if packet is not None:
			packetFactory.export(packet)


# ------------------------------------------------------------------------------
# PacketQueue
# ------------------------------------------------------------------------------

class PacketQueue(object):
	def __init__(self, queueSize = 0):
		self.__queue = FreezeQueue(queueSize)


	def put(self, packet):
		try:
			return self.__queue.put(packet)
		except ValueError, exc:
			pass


	def get(self):
		try:
			return self.__queue.get()
		except ValueError, exc:
			pass


# ------------------------------------------------------------------------------
# PacketFactory
# ------------------------------------------------------------------------------

class PacketFactory(object):
	def createRequest(self, data):
		idTransaction = self.__idTransaction()
		return Packet(idTransaction, 'request', data)
	
	
	def parse(self, inputStream):
		packetParser = PacketParser()
		return packetParser.parse(inputStream)
		
	
	def export(self, outputStream, packet):
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
# PacketParser
# ------------------------------------------------------------------------------

class PacketParser(object):
	def parse(self, inputStream):
		infoLine = inputStream.readLine().trim()
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
# Packet
# ------------------------------------------------------------------------------

class Packet(object):
	REQUEST = 'request'
	RESPONSE = 'response'
	CANCEL = 'cancel'
	__TYPES = (
		REQUEST,
		RESPONSE,
		CANCEL
	)
	
	
	def __init__(self, tid, type, data):
		self.__tid = tid
		self.__checkType(type)
		self.__type = type
		self.__data = data


	def __checkType(self, type):
		if type not in self.__TYPES:
			raise AttributeError('Packet type %s is unknown' % type)
	
	
	def __nonzero__(self):
		return True
	
	
	def tid(self):
		return tid	
	
	
	def type(self):
		return self.__type


	def data(self):
		return data


# ------------------------------------------------------------------------------
# Transaction
# ------------------------------------------------------------------------------

class Transaction(object):
	OPEN = 'open'
	DONE = 'done'
	CANCEL = 'cancel'
	
	
	def __init__(self, data, timeout):
		self.__request = PacketFactory.createRequest(data)
		self.__response = None
		self.__state = Transaction.OPEN
		self.__timeout = timeout
		# jak to tady poladit? - ptat se na to nekoho jineho :)
		self.__createTime = time()
		self.__event = Event()

	
	def tid(self):
		return self.__request.tid()
	
	
	@synchronize
	def setResponse(self, data):
		if not self.isOpen():
			raise
		if self.isTimeout():
			return False
		self.__doneTime = time()
		self.__state = Transaction.DONE
		self.__response = data
		self.__event.set()
		return True


	def waitResponse(self, blocking = True):
		if blocking:
			self.__event.wait()
		if self.isTimeout():
			raise TransactionTimeout()
		if self.isCancel():
			raise
		if self.isDone():
			return self.__response


	def getRequest(self):
		return self.__request


	@synchronize
	def checkTimeout(self):
		if self.__isTimeout():
			self.__event.set()
			return True
		else:
			return False


	def cancel(self):
		self.__state = Transaction.CANCEL
	
	
	def isOpen(self):
		return self.__state == Transaction.OPEN


	def isDone(self):
		return self.__state == Transaction.DONE


	def isTimeout(self):
		# porovnej casy
		return False


	def isCancel(self):
		return self.__state == Transaction.CANCEL


# ------------------------------------------------------------------------------
# TransactionTable
# ------------------------------------------------------------------------------

class TransactionTable(object):
	def createTransaction(self, data, timeout):
		return packet


	def setResponse(self, packet):
		pass


	def waitResponse(self, transactionId, blocking = True):
		return data


	def iteration(self):
		self.__cleanTimeouted()
		self.__cleanOld()


# ------------------------------------------------------------------------------
# LemiCamel
# ------------------------------------------------------------------------------

class LemiCamel(object):
	def __init__(self, packetReceiver, packetSender, transactions):
		self.__transactions = transactions
		self.__packetReceiver = packetReceiver
		self.__packetReceiver = packetSender
		self.__requests = FreezeQueue()


	def sendRequest(self, data, timeout = INFINITE_TIMEOUT):
		packet = self.__transactions.createTransaction(data, timeout)
		self.__packetSender.put(packet)
		return packet.tid()


	def getResponse(self, tid, timeout = BLOCK):
		return self.__transactions.waitResponse(tid, timeout)


	def getRequest(self):
		packet = self.__requests.get()
		return packet.tid(), packet.data()


	def sendResponse(self, tid, data):
		packet = Packet(tid, Packet.RESPONSE, data)
		while not self.__packetSender.put(packet):
			pass
	
	
	def putPacket(self, packet):
		if packet.type() == Packet.REQUEST:
			while not self.__requests.put(packet):
				pass
		elif packet.type() == Packet.RESPONSE:
			self.__transactions.setResponse(packet)
		else:
			logging.warning('Unknown packet type %s' % packet.type())


"""
dodat tridu na rychle posazeni na TcpServer a spojeni s jsonrpc
"""