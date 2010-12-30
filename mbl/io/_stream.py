from types import StringType, UnicodeType, IntType, LongType
from mbl.io import Timeout


# ------------------------------------------------------------------------------
# functions
# ------------------------------------------------------------------------------

def _positiveNumberCheck(number):
	if type(number) not in (IntType, LongType):
		raise AttributeError('Bytes argument must be integer: ' % str(type(number)))
	if number < 1:
		raise AttributeError('Bytes argument must be positive number: %d' % number)


def _stringCheck(data):
	if type(data) != StringType:
		raise AttributeError("Data must be string type: %s" % str(type(data)))


# ------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------

class ClosedStreamError(IOError):
	pass


# ------------------------------------------------------------------------------
# Closer
# ------------------------------------------------------------------------------

class Closer(object):
	def __init__(self):
		self.__closed = False


	def close(self):
		self._checkClosed()
		self.__closed = True


 	def _checkClosed(self):
 		if self.__closed:
 			raise ClosedStreamError


# ------------------------------------------------------------------------------
# InputStream
# ------------------------------------------------------------------------------

class InputStream(Closer):
	def __init__(self):
		super(InputStream, self).__init__()


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return False


	def read(self, bytes):
		self._checkClosed()
		_positiveNumberCheck(bytes)
		return ''


 	def skip(self, bytes):
 		self._checkClosed()
 		return 0


# ------------------------------------------------------------------------------
# OutputStream
# ------------------------------------------------------------------------------

class OutputStream(Closer):
	def __init__(self):
		super(OutputStream, self).__init__()


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return False


	def flush(self):
		self._checkClosed()


	def write(self, data):
		self._checkClosed()
		_stringCheck(data)


	def writeNonblock(self, data):
		self._checkClosed()
		_stringCheck(data)
		return 0
	

# ------------------------------------------------------------------------------
# IOStream
# ------------------------------------------------------------------------------

class IOStream(Closer):
	def __init__(self, inputStream, outputStream):
		super(IOStream, self).__init__()
		self.__inputStream = inputStream
		self.__outputStream = outputStream


	def inputStream(self):
		return self.__inputStream


	def outputStream(self):
		return self.__outputStream


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return self.__inputStream.ready()


	def read(self, bytes):
		self._checkClosed()
		return self.__inputStream.read(bytes)


 	def skip(self, bytes):
 		self._checkClosed()
 		return self.__inputStream.skip(bytes)


	def flush(self):
		self._checkClosed()
		return self.__outputStream.flush()


	def write(self, data):
		self._checkClosed()
		return self.__outputStream.write(data)


	def writeNonblock(self, data):
		self._checkClosed()
		return self.__outputStream.writeNonblock(data)


	def close(self):
		super(IOStream, self).close()
		self.__inputStream.close()
		self.__outputStream.close()


# ------------------------------------------------------------------------------
# Reader
# ------------------------------------------------------------------------------

class Reader(Closer):
	def __init__(self):
		super(Reader, self).__init__()


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return False


	def read(self, chars):
		self._checkClosed()
		_positiveNumberCheck(chars)
		return ''


 	def skip(self, chars):
 		self._checkClosed()
 		_positiveNumberCheck(chars)
 		return 0


# ------------------------------------------------------------------------------
# Writer
# ------------------------------------------------------------------------------

class Writer(Closer):
	def __init__(self):
		super(Writer, self).__init__()


	def flush(self):
		self._checkClosed()


	def write(self, text):
		self._checkClosed()
		if type(text) != UnicodeType:
			raise AttributeError('Text must be unicode: %s' % str(type(text)))
		return 0


# ------------------------------------------------------------------------------
# ReaderWriter
# ------------------------------------------------------------------------------

class ReaderWriter(Closer):
	def __init__(self, reader, writer):
		super(ReaderWriter, self).__init__()
		self.__reader = reader
		self.__writer = writer


	def reader(self):
		return self.__reader


	def writer(self):
		return self.__writer


	def read(self, chars):
		self._checkClosed()
		return self.__reader.read(chars)


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return self.__reader.ready()


 	def skip(self, chars):
 		self._checkClosed()
 		return self.__reader.skip(chars)


	def flush(self):	
		self._checkClosed()
		return self.__writer.flush()


	def write(self, text):
		self._checkClosed()
		return self.__writer.write(text)


	def close(self):
		super(ReaderWriter, self).close()
		self.__reader.close()
		self.__writer.close()


