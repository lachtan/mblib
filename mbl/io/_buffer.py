from types import StringType
from StringIO import StringIO
from mbl.io import InputStream, OutputStream


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


	def isReady(self):
		self._checkClosed()
		return True


	def availableBytes(self):
		self._checkClosed()
		return self.__length - self.__actualPosition


	def read(self, bytes = 1):
		super(BufferInputStream, self).read(bytes)
		if int(bytes) <= 0:
			raise AttributeError('Number of bytes must be positive integer number: %s' % str(bytes))
		data = self.__buffer[self.__actualPosition:self.__actualPosition + bytes]
		self.__actualPosition = min(self.__actualPosition + bytes, self.__length)
		return data


 	def skip(self, bytes):
 		return len(self.read(bytes))


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


	def close(self):
		super(BufferOutputStream, self).close()
		self.__buffer.close()


	def write(self, data):
		super(BufferOutputStream, self).write(data)
		self.__buffer.write(data)


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
	pass

