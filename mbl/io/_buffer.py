from types import StringType
from StringIO import StringIO
from mbl.io import InputStream, OutputStream
from mbl.io import Timeout


# ------------------------------------------------------------------------------
#
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
#
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


	def __str__(self):
		return self.__buffer.getvalue()


	def __eq__(self, other):
		return str(self) == str(other)


	def __hash__(self):
		return hash(str(self))


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class BufferedInputStream(InputStream):
	def __init__(self, inputStream, bufferSize):
		super(BufferedInputStream, self).__init__()
		# kontrola bufferSize
		self.__buffer = ''
	
	
	def ready(self, timeout = Timeout.NONBLOCK):
		super(BufferedInputStream, self).ready(timeout)

		return False



# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class BufferedOutputStream(InputStream):
	def __init__(self, outputStream, bufferSize):
		pass

