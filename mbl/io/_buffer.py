from types import StringType
from StringIO import StringIO
from mbl.io import InputStream, OutputStream
from mbl.io import FilterInputStream, FilterOutputStream
from mbl.io import Timeout

# 32kB
DEFAULT_BUFFER_SIZE = 2 ** 15

# ------------------------------------------------------------------------------
# BufferInputStream
# ------------------------------------------------------------------------------

class BufferInputStream(InputStream):
	def __init__(self, buffer):
		super(BufferInputStream, self).__init__()
		if type(buffer) != StringType:
			raise AttributeError("Buffer is not str type: %s" % str(type(buffer)))
		self.__buffer = buffer
		self.__length = len(buffer)
		self.__actualPosition = 0


	def ready(self, timeout = Timeout.NONBLOCK):
		self._checkClosed()
		return True


	def read(self, bytes):
		super(BufferInputStream, self).read(bytes)
		data = self.__buffer[self.__actualPosition:self.__actualPosition + bytes]
		self.__actualPosition = min(self.__actualPosition + bytes, self.__length)
		return data


 	def skip(self, bytes): 		 		
 		super(BufferInputStream, self).skip(bytes) 
 		newActualPosition = min(self.__actualPosition + bytes, self.__length)
 		skipBytes = newActualPosition - self.__actualPosition
 		self.__actualPosition = newActualPosition
 		return skipBytes


 	def __hash__(self):
 		return hash((self.__buffer, self.__actualPosition, self.__closed))


# ------------------------------------------------------------------------------
# BufferOutputStream
# ------------------------------------------------------------------------------

class BufferOutputStream(OutputStream):
	def __init__(self, maxBufferLength = 0):
		super(BufferOutputStream, self).__init__()
		self.__maxBufferLength = maxBufferLength
		self.__buffer = StringIO()


	def ready(self, timeout = Timeout.NONBLOCK):
		super(BufferOutputStream, self).ready(timeout)
		return True
	

	def write(self, data):
		super(BufferOutputStream, self).write(data)
		self.__buffer.write(data)
	
	
	def writeNonblock(self, data):
		self.write(data)
		return len(data)


	def close(self):
		super(BufferOutputStream, self).close()
		self.__buffer.close()


	def buffer(self):
		return self.__buffer.getvalue()


	def __hash__(self):
		return hash(self.buffer())


# ------------------------------------------------------------------------------
# CachedInputStream
# ------------------------------------------------------------------------------

# Optimalizovat pro StringIO

class CachedInputStream(FilterInputStream):
	def __init__(self, inputStream, bufferSize = DEFAULT_BUFFER_SIZE):
		super(CachedInputStream, self).__init__(inputStream)
		self.__inputStream = inputStream
		self.__chekBufferSize(bufferSize)
		self.__bufferSize = int(bufferSize)
		self.__buffer = ''
	
	
	def __chekBufferSize(self, bufferSize):
		if int(bufferSize) <= 0:
			raise AttributeError('Buffer size must be integer positive number: %s' % str(bufferSize))
	
	
	def ready(self, timeout = Timeout.NONBLOCK):
		super(BufferedInputStream, self).ready(timeout)
		return (not self.__isEmpty()) or self.__inputStream.ready(timeout)
	
	
	def __isEmpty(self):
		return self.__buffer == ''
		
	
	def read(self, bytes):
		super(CachedInputStream, self).read(bytes)
		if bytes > self.__bufferSize or bytes > len(self.__buffer):
			self.__fillBuffer()
		return self.__read(bytes)
	
	
	def __fillBuffer(self):
		if self.__isEmpty():
			self.__buffer = self.__inputStream.read(self.__bufferSize)
		if self.__isEmpty():
			return
		while len(self.__buffer) < self.__bufferSize:
			if not self.__inputStream.ready():
				return
			bytes = self.__bufferSize - len(self.__buffer)
			data = self.__inputStream.read(bytes)
			if data == '':
				return
			self.__buffer += data
	
	
	def __read(self, bytes):
		if self.__isEmpty():
			return ''
		data = self.__buffer[:bytes]
		self.__buffer = self.__buffer[len(data):]
		return data
	
	
	def _buffer(self):
		return self.__buffer
	
	
# ------------------------------------------------------------------------------
# CachedOutputStream
# ------------------------------------------------------------------------------

class CachedOutputStream(FilterOutputStream):
	def __init__(self, outputStream, bufferSize = DEFAULT_BUFFER_SIZE):
		super(CachedOutputStream, self).__init__(outputStream)
		self.__bufferSize = bufferSize
		self.__outputStream = outputStream
	
	
	def ready(self, timeout = Timeout.NONBLOCK):
		raise NotImplementedError
	
	
	def write(self, data):
		raise NotImplementedError
		
	
	def flush(self):
		raise NotImplementedError

