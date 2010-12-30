"""
TODO

Jak hezky udelat spoecnou tridu pro cteni a zapis, z ktere potom
pujdou lehce odvodit LineInputStream, ...
"""

from types import StringType, UnicodeType
from mbl.io import InputStream, OutputStream
from mbl.io import Reader, Writer

# ------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------

UNLIMITED_LINE_LENGTH = 0


# ------------------------------------------------------------------------------
# LineScanner
# ------------------------------------------------------------------------------

class LineScanner(object):
	def __init__(self, input, enabledType):
		self.__input = input
		self.__enabledType = enabledType
		self.setMaxLineLength(UNLIMITED_LINE_LENGTH)
		self.setDeleteEol(False)


	def setEndLineList(self, endLineList):
		for endLine in endLineList:
			self.__checkType(endLine)
		self.__endLineList = tuple(endLineList)


	def __checkType(self, text):
		if type(text) != self.__enabledType:
			raise AttributeError('Bad type %s' % str(type(text)))


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
			char = self.__input.read(1)
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


# ------------------------------------------------------------------------------
# LineInputStream
# ------------------------------------------------------------------------------

class LineInputStream(InputStream):
	__END_LINE_LIST = ('\r\n', '\n')


	def __init__(self, inputStream):
		super(LineInputStream, self).__init__()
		self.__inputStream = inputStream
		self.__lineScanner = LineScanner(inputStream, StringType)
		self.__lineScanner.setEndLineList(self.__END_LINE_LIST)


	def readLine(self):
		return self.__lineScanner.readLine()


	def read(self, chars):
		return self.__inputStream.read(chars)


	def ready(self, timeout):
		return self.__inputStream.ready(timeout)


 	def skip(self, chars):
 		return self.__inputStream.skip(chars)


	def close(self):
		return self.__inputStream.close()


# ------------------------------------------------------------------------------
# LineOutputStream
# ------------------------------------------------------------------------------

class LineOutputStream(OutputStream):
	def __init__(self, outputStream):
		super(LineOutputStream, self).__init__()
		self.__outputStream = outputStream
		self.setEol('\n')


	def setEol(self, eol):
		self.__eol = eol


	def newLine(self):
		self.write(self.__eol)


	def writeLine(self, *args):
		text = ''.join(map(str, args)) + self.__eol
		self.write(text)


	
	def flush(self):
		return self.__outputStream.flush()


	def write(self, text):
		return self.__outputStream.write(text)
	
	
	def writeNonblock(self, data):
		return __outputStream.writeNonblock(data)


	def close(self):
		return self.__outputStream.close()


# ------------------------------------------------------------------------------
# LineReader
# ------------------------------------------------------------------------------

class LineReader(Reader):
	__END_LINE_LIST = (u'\r\n', u'\n')


	def __init__(self, reader):
		super(Reader, self).__init__()
		self.__reader = reader
		self.__lineScanner = LineScanner(reder, UnicodeType)
		self.__lineScanner.setEndLineList(self.__END_LINE_LIST)


	def readLine(self):
		return self.__lineScanner.readLine()


	def read(self, chars):
		return self.__reader.read(chars)


	def ready(self, timeout):
		return self.__reader.ready(timeout)


 	def skip(self, chars):
 		return self.__reader.skip(chars)


	def close(self):
		return self.__reader.close()


# ------------------------------------------------------------------------------
# LineWriter
# ------------------------------------------------------------------------------

class LineWriter(Writer):
	pass
	
