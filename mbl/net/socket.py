"""
TODO

- vlastnosti socketu
- timeout
- pouziti select

jak sem pak nacpat socket pair minimalne kvuli testovani
"""

from __future__ import absolute_import
import socket
import select
from mbl.io import InputStream, OutputStream, IOStream
from mbl.io import TimeoutError


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
		self.__outputStream.close()
		self.__socket.close()


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
	def __init__(self, socket, timeout):
		self.__socket = socket
		self.__timeout = timeout


	def read(self, bytes = 1):
		try:
			return self.__read(bytes)
		except	socket.timeout:
			raise TimeoutError


	def __read(self, bytes = 1):
		data = ''
		while len(data) < bytes:
			self.__wait(self.__timeout)
			data += self.__socket.recv(bytes - len(data))
		return data


	def __wait(self, timeout):
		status = select.select([self.__socket], [], [], timeout)
		ready = len(status[0]) == 1
		if not ready:
			raise TimeoutError('read', timeout)



# ------------------------------------------------------------------------------
# SocketOutputStream
# ------------------------------------------------------------------------------

class SocketOutputStream(OutputStream):
	def __init__(self, socket, timeout):
		super(SocketOutputStream, self).__init__()
		self.__socket = socket
		self.__timeout = timeout


	def write(self, data):
		super(SocketOutputStream, self).write(data)
		startTime = time()
		writtenBytes = 0
		while True:
			now = time()
			duration = now - startTime
			if duration > self.__timeout:
				raise TimeoutError
			timeout = self.__timeout - duration
			self.__waitForWrite(timeout)
			bytes = self.__socket.send(data[writtenBytes:])
			writtenBytes += bytes
			if writtenBytes == len(data):
				return


	def __waitForWrite(self, timeout):
		status = select([], [self.__socket], [], timeout)
		if len(status[1]) == 0:
			raise TimeoutError


	def _write(self, data):
		super(SocketOutputStream, self).write(data)
		self.__socket.sendall(data)


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


	def accept(self)
		clientSocket, clientAddress = self.__socket.accept()
		return Socket(clientSocket, clientAddress)


	def mainLoop(self, callback, args):
		while True:
			clientSocket = self.accept()
			callback(clientSocket, args)
