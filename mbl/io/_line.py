from types import StringType, UnicodeType
from mbl.io import FilterInputStream, FilterOutputStream
from mbl.io import FilterDuplexStream
from mbl.io import FilterReader, FilterWriter

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
			self.__check(endLine)
		self.__endLineList = tuple(endLineList)
		self.__endChars = set([endLine[-1] for endLine in endLineList])


	def __check(self, text):
		if type(text) != self.__enabledType:
			textType = str(type(text))
			enabledType = str(self.__enabledType)
			raise AttributeError('Type %s is not %s' % (textType, enabledType))
		if text == '':
			raise AttributeError('Length of line end must be positive')


	def setMaxLineLength(self, maxLineLength):
		_maxLineLength = int(maxLineLength)
		if _maxLineLength < 0:
			raise AttributeError("Length can't be negative: %d" % _maxLineLength)
		self.__maxLineLength = _maxLineLength


	def setDeleteEol(self, deleteEol):
		self.__deleteEol = bool(deleteEol)


	def readLine(self):
		self.__line = ''
		self.__char = None
		while True:
			if self.__isEndedLine():
				self.__correctLine()
				return self.__line
			self.__char = self.__input.read(1)
			if self.__char == '':
				return self.__line
			self.__line += self.__char


	def __iter__(self):
		while True:
			line = self.readLine()
			if line == '':
				return
			else:
				yield line


	def __isEndedLine(self):
		if self.__maxLineLength > 0 and len(self.__line) >= self.__maxLineLength:
			self.__end = ''
			return True
		if self.__char not in self.__endChars:
			return False
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

class LineInputStream(FilterInputStream):
	__END_LINE_LIST = ('\r\n', '\n')


	def __init__(self, inputStream):
		super(LineInputStream, self).__init__(inputStream)
		self.__inputStream = inputStream
		self.__lineScanner = LineScanner(inputStream, StringType)
		self.__lineScanner.setEndLineList(self.__END_LINE_LIST)


	def setEndLineList(self, endLineList):
		self.__lineScanner.setEndLineList(endLineList)


	def setMaxLineLength(self, maxLineLength):
		self.__lineScanner.setMaxLineLength(maxLineLength)


	def setDeleteEol(self, deleteEol):
		self.__lineScanner.setDeleteEol(deleteEol)


	def readLine(self):
		return self.__lineScanner.readLine()
	
	
	def __iter__(self):
		for line in self.__lineScanner:
			yield line


# ------------------------------------------------------------------------------
# LineOutputStream
# ------------------------------------------------------------------------------

class LineOutputStream(FilterOutputStream):
	def __init__(self, outputStream):
		super(LineOutputStream, self).__init__(outputStream)
		self.__outputStream = outputStream
		self.setEol('\n')


	def setEol(self, eol):
		self.__eol = eol


	def newLine(self):
		self.write(self.__eol)


	def writeLine(self, text):
		_text = text + self.__eol
		self.write(_text)


# ------------------------------------------------------------------------------
# LineDuplexStream
# ------------------------------------------------------------------------------

class LineDuplexStream(FilterDuplexStream):
	def __init__(self, duplexStream):
		super(LineDuplexStream, self).__init__(duplexStream)
		self.__lineInputStream = LineInputStream(duplexStream.inputStream())
		self.__lineOutputStream = LineOutputStream(duplexStream.outputStream())


	def inputStream(self):
		return self.__lineInputStream


	def outputStream(self):
		return self.__lineOutputStream


	def setEndLineList(self, endLineList):
		self.__lineInputStream.setEndLineList(endLineList)


	def setMaxLineLength(self, maxLineLength):
		self.__lineInputStream.setMaxLineLength(maxLineLength)


	def setDeleteEol(self, deleteEol):
		self.__lineInputStream.setDeleteEol(deleteEol)


	def readLine(self):
		return self.__lineInputStream.readLine()


	def __iter__(self):
		for line in self.__lineInputStream:
			yield line


	def setEol(self, eol):
		self.__lineOutputStreamsetEof(eol)


	def newLine(self):
		self.__lineOutputStream.newLine()


	def writeLine(self, text):
		self.__lineOutputStream.writeLine()


	def close(self):
		super(LineDuplexStream, self).close()
		self.__lineInputStream = None
		self.__lineOutputStream = None


# ------------------------------------------------------------------------------
# LineReader
# ------------------------------------------------------------------------------

class LineReader(FilterReader):
	__END_LINE_LIST = (u'\r\n', u'\n')


	def __init__(self, reader):
		super(Reader, self).__init__(reader)
		self.__reader = reader
		self.__lineScanner = LineScanner(reder, UnicodeType)
		self.__lineScanner.setEndLineList(self.__END_LINE_LIST)


	def setEndLineList(self, endLineList):
		self.__lineScanner.setEndLineList(endLineList)


	def setMaxLineLength(self, maxLineLength):
		self.__lineScanner.setMaxLineLength(maxLineLength)


	def setDeleteEol(self, deleteEol):
		self.__lineScanner.setDeleteEol(deleteEol)


	def readLine(self):
		return self.__lineScanner.readLine()


	def __iter__(self):
		for line in self.__lineScanner:
			yield line


# ------------------------------------------------------------------------------
# LineWriter
# ------------------------------------------------------------------------------

class LineWriter(FilterWriter):
	def __init__(self, writer):
		super(LineWriter, self).__init__(writer)
		self.__writer = writer
		self.setEol(u'\n')


	def setEol(self, eol):
		self.__eol = eol


	def newLine(self):
		self.write(self.__eol)


	def writeLine(self, *args):
		text = u''.join(map(str, args)) + self.__eol
		self.write(text)


# ------------------------------------------------------------------------------
# LineReaderWriter
# ------------------------------------------------------------------------------

# TODO :)
