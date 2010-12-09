"""
TODO

- vlastnosti socketu
- timeout
- pouziti select
"""

from __future__ import absolute_import
import socket
import select
from mbl.io.stream import InputStream, OutputStream
from mbl.io.timeout import TimeoutError


# ------------------------------------------------------------------------------
# SocketClient
# ------------------------------------------------------------------------------

class SocketClient(object):
	def __init__(self, address):
		self.__address = address
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.setConnectTimeout(None)
		self.setTimeout(None)
		self.__inputStream = SocketInputStream(self.__socket, self.__timeout)
		self.__outputStream = SocketOutputStream(self.__socket, self.__timeout)


	def connect(self):
		self.__socket.settimeout(self.__connectTimeout)
		try:
			self.__socket.connect(self.__address)
		except socket.timeout:
			raise TimeoutError('connect', self.__connectTimeout)
		self.__socket.setblocking(0)


	def setConnectTimeout(self, timeout):
		self.__connectTimeout = timeout


	def setTimeout(self, timeout):
		self.__timeout = timeout


	def inputStream(self):
		return self.__inputStream


	def outputStream(self):
		return self.__outputStream


	def close(self):
		self.__socket.close()


	def shutdown(self):
		self.__socket.shutdown(socket.SHUT_RDWR)


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
		self.__socket = socket


	def write(self, text):
		return self.__socket.sendall(text)

