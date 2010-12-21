"""
TODO
pracuje s bajty:
LineInputStream
LineOutputStream
LineIOStream ?

pracuji s unicode:
LineReader
LineWriter
Line???

"""

from types import StringType, UnicodeType, IntType, LongType


# ------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------

UNLIMITED_LINE_LENGTH = 0


# ------------------------------------------------------------------------------
# functions
# ------------------------------------------------------------------------------

def _positiveNumberCheck(number):
	if type(number) not in (IntType, LongType):
		raise AttributeError('Bytes argument must be integer: ' % str(type(number)))
	if bytes < 1:
		raise AttributeError('Bytes argument must be positive number: %d' % number)


# ------------------------------------------------------------------------------
# _Stream
# ------------------------------------------------------------------------------

class _Stream(object):
	def __init__(self):
		self.__closed = False


	def close(self):
		self._checkClosed()
		self.__closed = True


 	def _checkClosed(self):
 		if self.__closed:
 			# Nejaka vhodnejsi vyjimka?
 			raise IOError('Stream already closed')


# ------------------------------------------------------------------------------
# InputStream
# ------------------------------------------------------------------------------

class InputStream(_Stream):
	def __init__(self):
		super(InputStream, self).__init__()


	def isReady(self):
		self._checkClosed()
		return False


	def availableBytes(self):
		self._checkClosed()
		return 0


	def close(self):
		self._checkClosed()


	def read(self, bytes = 1):
		self._checkClosed()
		_positiveNumberCheck(bytes)


 	def skip(self, bytes):
 		self._checkClosed()
 		_positiveNumberCheck(bytes)


# ------------------------------------------------------------------------------
# OutputStream
# ------------------------------------------------------------------------------

class OutputStream(_Stream):
	def __init__(self):
		super(OutputStream, self).__init__()


	def flush(self):
		self._checkClosed()


	def write(self, data):
		self._checkClosed()
		if type(data) != StringType:
			raise AttributeError("Data must be string type: %s" % str(type(data)))


# ------------------------------------------------------------------------------
# IOStream
# ------------------------------------------------------------------------------

class IOStream(_Stream):
	def __init__(self, inputStream, outputStream):
		super(IOStream, self).__init__()
		self.__inputStream = inputStream
		self.__outputStream = outputStream


	def inputStream(self):
		return self.__inputStream


	def outputStream(self):
		return self.__outputStream


	def isReady(self):
		self._checkClosed()
		return self.__inputStream.isReady()


	def availableBytes(self):
		self._checkClosed()
		return self.__inputStream.availableBytes()


	def read(self, bytes = 1):
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


	def close(self):
		super(IOStream, self).close()
		self.__inputStream.close()
		self.__outputStream.close()


# ------------------------------------------------------------------------------
# Reader
# ------------------------------------------------------------------------------

class Reader(_Stream):
	def __init__(self):
		super(Reader, self).__init__()


	def read(self, chars = 1):
		self._checkClosed()
		_positiveNumberCheck(chars)
		return ''


	def isReady(self):
		self._checkClosed()
		return False


 	def skip(self, chars):
 		self._checkClosed()
 		_positiveNumberCheck(chars)
 		return 0


# ------------------------------------------------------------------------------
# Writer
# ------------------------------------------------------------------------------

class Writer(_Stream):
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

class ReaderWriter(_Stream):
	def __init__(self, reader, writer):
		super(ReaderWriter, self).__init__()
		self.__reader = reader
		self.__writer = writer


	def reader(self):
		return self.__reader


	def writer(self):
		return self.__writer


	def read(self, chars = 1):
		self._checkClosed()
		return self.__reader.read(chars)


	def isReady(self):
		self._checkClosed()
		return self.__reader.isReady()


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


# ------------------------------------------------------------------------------
# LineReader
# ------------------------------------------------------------------------------

class LineReader(Reader):
	__END_LINE_LIST = ('\r\n', '\n')


	def __init__(self, reader):
		Reader.__init__(self)
		self.__reader = reader
		self.setEndLineList(self.__END_LINE_LIST)
		self.setMaxLineLength(self.UNLIMITED_LINE_LENGTH)
		self.setDeleteEol(False)


	def setEndLineList(self, endLineList):
		for endLine in endLineList:
			if type(endLine) not in (StringType, UnicodeType):
				raise AttributeError('Not str or unicode %s' % repr(endLine))
		self.__endLineList = tuple(endLineList)


	def setMaxLineLength(self, maxLineLength):
		_maxLineLength = int(maxLineLength)
		if _maxLineLength < 0:
			raise AttributeError("Length can't be negative: %d" % _maxLineLength)
		self.__maxLineLength = _maxLineLength


	def setDeleteEol(self, deleteEol):
		self.__deleteEol = bool(deleteEol)


	def readLine(self):
		self.__line = ''
		while True:
			if self.__isEndedLine():
				self.__correctLine()
				return self.__line
			char = self.read(1)
			if char == '':
				return self.__line
			self.__line += char


	def __isEndedLine(self):
		if self.__maxLineLength > 0 and len(self.__line) >= self.__maxLineLength:
			self.__end = ''
			return True
		for self.__end in self.__endLineList:
			if self.__line.endswith(self.__end):
				return True
		return False


	def __correctLine(self):
		if self.__deleteEol and self.__end:
			self.__line = self.__line[:-len(self.__end)]


	def close(self):
		return self.__reader.close()


	def read(self, chars = 1):
		return self.__reader.read(chars)


	def isReady(self):
		return self.__reader.isReady()


 	def skip(self, chars):
 		return self.__reader.skip(chars)


# ------------------------------------------------------------------------------
# LineWriter
# ------------------------------------------------------------------------------

class LineWriter(Writer):
	def __init__(self, writer):
		self.__writer = writer
		self.setEol('\n')


	def setEol(self, eol):
		self.__eol = eol


	def newLine(self):
		self.write(self.__eol)


	def writeLine(self, *args):
		text = u''.join(map(str, args)) + self.__eol
		self.write(text)


	def close(self):
		return self.__writer.close()


	def flush(self):
		return self.__writer.flush()


	def write(self, text):
		return self.__writer.write(text)


# ------------------------------------------------------------------------------
# cleaning
# ------------------------------------------------------------------------------

del _Stream
del _positiveNumberCheck

