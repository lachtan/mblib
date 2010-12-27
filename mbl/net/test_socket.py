import unittest
import socket
from mbl.net import SocketInputStream
from mbl.io import Timeout


class SocketInputStreamTest(unittest.TestCase):
	def setUp(self):
		self.__left, self.__right = socket.socketpair()
	
	
	def tearDown(self):
		self.__left.close()
		self.__right.close()
	
	
	def test_readyNonblockTrue(self):
		inputStream = SocketInputStream(self.__left, Timeout.NONBLOCK)
		self.assertFalse(inputStream.ready())


	def test_readyNonblockFalse(self):
		inputStream = SocketInputStream(self.__left, Timeout.NONBLOCK)
		self.__right.sendall('some data')
		self.assertTrue(inputStream.ready())

	
"""	
def __init__(self, socket, timeout):
def read(self, bytes = 1):
def ready(self, timeout = Timeout.NONBLOCK):
"""

