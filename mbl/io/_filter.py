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


	def flush(self):
		return self.__outputStream.flush()


	def write(self, data):
		return self.__outputStream.write(data)


	def close(self):
		return self.__outputStream.close()


# ------------------------------------------------------------------------------
# FilterDuplexStream
# ------------------------------------------------------------------------------

class FilterDuplexStream(object):
	def __init__(self, duplexStream):
		self.__duplexStream = duplexStream


	def inputStream(self):
		return self.__duplexStream.inputStream()


	def outputStream(self):
		return self.__duplexStream.outputStream()


	def ready(self, timeout = Timeout.NONBLOCK):
		return self.__duplexStream.ready(timeout)


	def read(self, bytes):
		return self.__duplexStream.read(bytes)


 	def skip(self, bytes):
 		return self.__duplexStream.skip(bytes)


	def flush(self):
		return self.__duplexStream.flush()


	def write(self, data):
		return self.__duplexStream.write(data)


	def close(self):
		return self.__duplexStream.close()


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


# ------------------------------------------------------------------------------
# FilterReaderWriter
# ------------------------------------------------------------------------------

class FilterReaderWriter(object):
	def __init__(self, readerWriter):
		self.__readerWriter = readerWriter


	def ready(self, timeout = Timeout.NONBLOCK):
		return self.__readerWriter.ready(timeout)


	def read(self, chars):
		return self.__readerWriter.read(chars)


 	def skip(self, chars):
 		return self.__readerWriter.skip(chars)


	def flush(self):
		return self.__readerWriter.flush()


	def write(self, text):
		return self.__readerWriter.write(text)


	def close(self):
		return self.__readerWriter.close()

