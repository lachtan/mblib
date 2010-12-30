import codecs
from mbl.io import Reader, Writer
from mbl.io import Timeout


# ------------------------------------------------------------------------------
# FilterInputStream
# ------------------------------------------------------------------------------

class FilterInputStream(object):
	def __init__(self, inputStream):
		self.__inputStream = inputStream


	def ready(self, timeout = Timeout.NONBLOCK):
		return self.__inputStream.ready(timeout)


	def read(self, bytes):
		return self.__inputStream.read(bytes)


 	def skip(self, bytes):
 		return self.__inputStream.bytes()


	def close(self):
		return self.__inputStream.close()


# ------------------------------------------------------------------------------
# FilterOutputStream
# ------------------------------------------------------------------------------

class FilterOutputStream(object):
	def __init__(self, outputStream):
		self.__outputStream = outputStream


	def ready(self, timeout = Timeout.NONBLOCK):
		return self.__outputStream.ready(timeout)


	def flush(self):
		return self.__outputStream.flush()


	def write(self, data):
		return self.__outputStream.write(data)


	def writeNonblock(self, data):
		return self.__outputStream.writeNonblock(data)


	def close(self):
		return self.__outputStream.close()


