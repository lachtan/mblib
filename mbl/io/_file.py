import os
from mbl.io import InputStream, OutputStream
from mbl.io import Timeout


# ------------------------------------------------------------------------------
# FileInputStream
# ------------------------------------------------------------------------------

class FileInputStream(InputStream):
	def __init__(self, pathname):
		super(FileInputStream, self).__init__()
		self.__file = file(pathname, 'rb')
		self.__select = SimpleSelect(self.__file, Timeout.BLOCK)


	def ready(self, timeout = Timeout.NONBLOCK):
		super(FileInputStream, self).ready(timeout)
		return self.__select.readReady()

	def ready(self, timeout = Timeout.BLOCK):
		# POZOR muze otevrit rouru a pak se tam ty data budou zjevovat prubezne
		self._checkClosed()
		return True



	def read(self, bytes = 1):
		super(FileInputStream, self).read(bytes)
		return self.__file.read(bytes)


 	def skip(self, bytes):
 		super(FileInputStream, self).skip(bytes)
 		originalOffset = self.tell()
 		self.seek(bytes, os.SEEK_CUR)
 		newOffset = self.tell()
 		return newOffset - originalOffset


	def fileno(self):
		return self.__stream.fileno()


	def close(self):
		self._checkClosed()
		self.__file.close()


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
