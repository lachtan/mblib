from __future__ import absolute_import
import socket
import select
import errno
from mbl.io import InputStream, OutputStream, IOStream
from mbl.io import Timeout, TimeoutError
from mbl.sys.select import SimpleSelect


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
			if e.errno == errno.EINTR:
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
		self.__inputStream = SocketInputStream(self.__socket, Timeout.BLOCK)
		self.__outputStream = SocketOutputStream(self.__socket, Timeout.BLOCK)


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


	def fileno(self):
		self.self.__socket.fileno()
	
	
	def getsockopt(self, level, optname, buflen = None):
		if buflen is None:
			return self.self.__socket.getsockopt(level, optname)
		else:
			return self.self.__socket.getsockopt(level, optname, buflen)
		
	
	def setsockopt(self, level, optname, value):
		return self.__socket.setsockopt(level, optname, value)
	
	
	def close(self):
		self.__inputStream.close()
		self.__outputStream.close()
		self.__socket.close()


# ------------------------------------------------------------------------------
# SocketInputStream
# ------------------------------------------------------------------------------

class SocketInputStream(InputStream):
	def __init__(self, socket, timeout):
		super(SocketInputStream, self).__init__()
		self.__socket = socket
		self.__timeout = timeout
		self.__select = SimpleSelect(socket)


	def ready(self, timeout = Timeout.NONBLOCK):
		super(SocketInputStream, self).ready(timeout)
		return self.__select.readReady(timeout)


	def read(self, bytes):
		super(SocketInputStream, self).read(bytes)
		try:
			return self.__read(bytes)
		except socket.timeout:
			raise TimeoutError
	
	
	def __read(self, bytes):
		if self.ready(self.__timeout):
			return signalSafeCall(self.__socket.recv, bytes)
		else:
			raise TimeoutError

	
# ------------------------------------------------------------------------------
# SocketOutputStream
# ------------------------------------------------------------------------------

class SocketOutputStream(OutputStream):
	def __init__(self, socket, timeout):
		super(SocketOutputStream, self).__init__()
		self.__socket = socket
		self.__timeout = timeout
		self.__select = SimpleSelect(socket)


	def ready(self, timeout = Timeout.NONBLOCK):
		super(SocketOutputStream, self).ready(timeout)
		return self.__select.writeReady(timeout)


	def write(self, data):
		super(SocketOutputStream, self).write(data)
		try:
			self.__write(data)
		except socket.timeout:
			raise TimeoutError
	
	
	def __write(self, data):
		if self.ready(self.__timeout):
			return signalSafeCall(self.__socket.sendall, data)
		else:
			raise TimeoutError
	
	
	def writeNonblock(self, data):
		super(SocketOutputStream, self).writeNonblock(data)
		return signalSafeCall(self.__socket.send, data)
		

# ------------------------------------------------------------------------------
# TcpClient
# ------------------------------------------------------------------------------

class TcpClient(object):
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
		_socket.setblocking(1)
		return Socket(_socket, self.__address)


	def setConnectTimeout(self, timeout):
		self.__connectTimeout = timeout
	
	
# ------------------------------------------------------------------------------
# TcpServer
# ------------------------------------------------------------------------------

class TcpServer(object):
	def __init__(self, serverAddress):
		self.__serverAddress = serverAddress
		self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__serverSocket.bind()
		self.listen(1)		
		# timeouty!


	def listen(self, value):
		self.__serverSocket.listen(value)
	
	
	def setsockopt(self, level, optname, value):
		return self.__serverSocket.setsockopt(level, optname, value)

	
	def accept(self):
		clientSocket, clientAddress = self.__socket.accept()
		return Socket(clientSocket, clientAddress)


	def mainLoop(self, callback, args):
		while True:
			clientSocket = self.accept()
			callback(clientSocket, args)

