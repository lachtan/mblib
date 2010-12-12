"""
InputStream
	int   available()
	str   read(bytes)
	int   skip(bytes)
	None  close()

OutputStream
	None  write(data)
	None  flush()
	None  close()

Reader
	bool  ready()
	str   read(chars)
	int   skip(chars)
	None  close()

IOError
	TimeoutError
	EOFError
	
# NOTICE #
read() a skip() vzdy ceka na nejaky vstup, do te doby je blokujici, vratit
muze pocet mensi nez vyzadovany, alze vzdy aspon jeden byte ci znak. Pri konci
streamu - EOS vraci prazdny retezec. Pri chybe vyhazuje vyjimku IOError nebo jejiho
potomka.
Jakakoliv ze zakladnich metod muze vyhodit vyjiku IOError


Stream types
	file
	socket
	buffer (in memory)
	serial port


# QUESTIONS #
Mely by byt operace nad temito tridami synchronizovany? Nebo je lepsi udelat
dalsi obalove tridy, ktere toto budou resit?


# NOTICE "ASCII8"
cp437
http://ascii-table.com/ascii-extended-pc-list.php
http://ascii-table.com/ansi-codes.php


# poznamka k prevodu neznamych znaku do unicode v jave
http://en.wikipedia.org/wiki/Specials_(Unicode_block)
"""

import os


__all__ = (
	'InputStream',
	'OutputStream',
	'Reader',
	'Writer',
	'LineReader',
	'LineWriter',
)


# ------------------------------------------------------------------------------
# InputStream
# ------------------------------------------------------------------------------

class InputStream(object):
	def available(self):
		""" Returns an estimate of the number of bytes that can be read
		(or skipped over) from this input stream without blocking by the next
		invocation of a method for this input stream."""
		# IOError
		raise NotImplementedError


	def close(self):
		# IOError
		raise NotImplementedError


	def read(self, bytes = 1):
		"""Returns string or '' if end of data"""
		# IOError
		raise NotImplementedError


 	def skip(self, bytes):
 		"""Returns number of bytes where skipped"""
 		# IOError
 		raise NotImplementedError


# ------------------------------------------------------------------------------
# OutputStream
# ------------------------------------------------------------------------------

class OutputStream(object):
	def close(self):
		# IOError
		raise NotImplementedError


	def flush(self):
		# IOError
		raise NotImplementedError


	def write(self, data):
		# IOError
		raise NotImplementedError


# ------------------------------------------------------------------------------
# Reader
# ------------------------------------------------------------------------------

class Reader(object):
	def __init__(self, lock = None):
		pass


	def close(self):
		raise NotImplementedError


	def read(self, chars = 1):
		raise NotImplementedError


	def ready(self):
		#  Tells whether this stream is ready to be read.
		raise NotImplementedError


 	def skip(self, characters):
 		raise NotImplementedError


# ------------------------------------------------------------------------------
# Writer
# ------------------------------------------------------------------------------

class Writer(object):
	def __init__(self, lock = None):
		pass


	def close(self):
		raise NotImplementedError


	def flush(self):
		raise NotImplementedError


	def write(self, text):
		raise NotImplementedError


# ------------------------------------------------------------------------------
# LineReader
# ------------------------------------------------------------------------------

class LineReader(Reader):
	__END_LINE_LIST = ('\r\n', '\n')
	__UNLIMITED_LINE_LENGTH = 0


	def __init__(self, reader):
		Reader.__init__(self)
		self.__reader = reader
		self.setEndLineList(self.__END_LINE_LIST)
		self.setMaxLineLength(self.__UNLIMITED_LINE_LENGTH)
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


	def read(self, *args, **kwargs):
		return self.__reader.read(*args, **kwargs)


	def ready(self):
		return self.__reader.ready()


 	def skip(self, characters):
 		return self.__reader.skip(characters)


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
		text = ''.join(map(str, args))
		self.write(text)
		self.newLine()


	def close(self):
		return self.__writer.close()


	def flush(self):
		return self.__writer.flush()


	def write(self, text):
		return self.__writer.write(text)


# ------------------------------------------------------------------------------
# FileInputStream
# ------------------------------------------------------------------------------


class FileInputStream(InputStream):
	def __init__(self, pathname):
		self.__stream = file(pathname, 'rb')


	def available(self):
		actualOffset = self.tell()
		endOffset = self.seek(0, os.SEEK_END)
		self.seek(actualOffset, os.SEEK_CUR)
		return endOffset - endOffset


	def close(self):
		self.__stream.close()


	def read(self, bytes = 1):
		return self.__stream.read(bytes)


 	def skip(self, bytes):
 		originalOffset = self.tell()
 		self.seek(bytes, os.SEEK_CUR)
 		newOffset = self.tell()
 		return newOffset - originalOffset


 	def tell(self):
 		return self.__stream.tell()


 	def seek(self, offset, whence = os.SEEK_CUR):
 		self.__stream.seek(offset, whence)


	def fileno(self):
		return self.__stream.fileno()