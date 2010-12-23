from __future__ import absolute_import
import socket
import select
import errno
from mbl.io import InputStream, OutputStream, IOStream
from mbl.io import Timeout, TimeoutError


"""
class SignalSafe(object):
	def __init__(self, exceptionClass):
	def call(callback, *args, **kwargs):
"""


def signalSafeCall(callback, *args):
	while True:
		try:
			return callback(*args)
		except socket.error, e:
			errorCode = e.args[0]
			if errorCode == errno.EINTR:
				continue
			else:
				raise

# ------------------------------------------------------------------------------
# Socket
# ------------------------------------------------------------------------------

class Socket(object):
	def __init__(self, socket, address):
		self.__address = address
		self.__socket = socket
		self.__inputStream = SocketInputStream(self.__socket)
		self.__outputStream = SocketOutputStream(self.__socket)


	def address(self):
		return self.__address


	def inputStream(self):
		return self.__inputStream


	def outputStream(self):
		return self.__outputStream


	def ioStream(self):
		return IOStream(self.__inputStream, self.__outputStream)


	def shutdown(self):
		self.__socket.shutdown(socket.SHUT_RDWR)
		self.close()


	def close(self):
		self.__inputStream.close()
		self.__outputStream.close()
		self.__socket.close()


# ------------------------------------------------------------------------------
# SocketClient
# ------------------------------------------------------------------------------

class SocketClient(object):
	def __init__(self, address):
		self.__address = address
		self.setConnectTimeout(None)


	def connect(self):
		_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_socket.settimeout(self.__connectTimeout)
		try:
			_socket.connect(self.__address)
		except socket.timeout:
			raise TimeoutError('connect', self.__connectTimeout)
		#_socket.setblocking(0)
		return Socket(_socket, self.__address)


	def setConnectTimeout(self, timeout):
		self.__connectTimeout = timeout


# ------------------------------------------------------------------------------
# SocketInputStream
# ------------------------------------------------------------------------------

class SocketInputStream(InputStream):
	__SELECT_READ_INDEX = 0
	
	
	def __init__(self, socket, timeout):
		super(SocketInputStream, self).__init__()
		self.__socket = socket
		self.__timeout = timeout
		self.__select = SimpleSelect(socket, timeout)


	def read(self, bytes = 1):
		super(SocketInputStream, self).read(bytes)
		try:
			return self.__read(bytes)
		except socket.timeout:
			raise TimeoutError
	
	
	def __read(self, bytes):
		if self.ready(self.__timeout):
			return signalSafeCall(self.__recv, bytes)
		else:
			raise TimeoutError
	

	def ready(self, timeout = Timeout.NONBLOCK):
		super(SocketInputStream, self).ready(timeout)
		return self.__select.readReady()
	
	
# ------------------------------------------------------------------------------
# SocketOutputStream
# ------------------------------------------------------------------------------

class SocketOutputStream(OutputStream):
	__SELECT_WRITE_INDEX = 1
	
	
	def __init__(self, socket, timeout):
		super(SocketOutputStream, self).__init__()
		self.__socket = socket
		self.__timeout = timeout
		self.__select = SimpleSelect(socket, timeout)


	def ready(self, timeout = Timeout.NONBLOCK):
		super(SocketOutputStream, self).ready(timeout)
		return self.__select.writeReady()


	def write(self, data):
		super(SocketOutputStream, self).write(data)
		try:
			self.__write(data)
		except socket.timeout:
			raise TimeoutError
	
	
	def __write(self, data):
		if self.ready(self.__timeout):
			return signalSafeCall(self.__sendall, data)
		else:
			raise TimeoutError
	
	
	def writeNonblock(self, data):
		super(SocketOutputStream, self).writeNonblock(data)
		return signalSafeCall(self.__socket.send, data)
		

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class SocketServer(object):
	def __init__(self, serverAddress):
		self.__serverAddress = serverAddress
		self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# a nejake dalsi srandicky
		# s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		# kde tohle volat?
		self.__serverSocket.bind()
		self.__serverSocket.listen(1)
		# timeouty!


	def accept(self):
		clientSocket, clientAddress = self.__socket.accept()
		return Socket(clientSocket, clientAddress)


	def mainLoop(self, callback, args):
		while True:
			clientSocket = self.accept()
			callback(clientSocket, args)

