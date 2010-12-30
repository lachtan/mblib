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


# ------------------------------------------------------------------------------
# FilterReader
# ------------------------------------------------------------------------------

class FilterReader(object):
	def __init__(self, reader):
		self.__reader = reader


	def ready(self, timeout = Timeout.NONBLOCK):
		return self.__reader.ready(timeout)
	
	
	def read(self, chars):
		return self.__reader.read(chars)


 	def skip(self, chars):
 		return self.__reader.skip(chars)
 		

	def close(self):
		return self.__reader.close()


# ------------------------------------------------------------------------------
# FilterWriter
# ------------------------------------------------------------------------------

class FilterWriter(object):
	def __init__(self, writer):
		self.__writer = writer


	def flush(self):
		return self.__writer.flush()


	def write(self, text):
		return self.__writer.write(text)


	def close(self):
		return self.__writer.close()


