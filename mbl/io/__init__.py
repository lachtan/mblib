"""
Vyjimky pro chyby

Fyzicke streamy
soubor
socket
memory buffer

Filtry

Reader
Writer

FileInputStream
FileOutputStream

FilterInputStream
FilterOutputStream

FileReader
FileWriter

StringBufferInputStream

StringReader
StringWriter

BufferedInputStream
BufferedOutputStream

BufferedReader
BufferedWriter


InputStreamReader(InputStream in)
          Create an InputStreamReader that uses the default charset.
InputStreamReader(InputStream in, Charset cs) 
          Create an InputStreamReader that uses the given charset.
InputStreamReader(InputStream in, CharsetDecoder dec) 
          Create an InputStreamReader that uses the given charset decoder.
InputStreamReader(InputStream in, String charsetName) 
          Create an InputStreamReader that uses the named charset.
          
IOError
  - TimeoutError
  - EOFError
"""


class InputStream(object):
	def available(self):
		"""IOError"""
		raise NotImplementedError
	
	
	def close(self):
		"""IOError"""
		raise NotImplementedError
	
	
	def read(self, bytes = 1):
		"""Returns string or '' if end of data
		IOError"""
		raise NotImplementedError

 	
 	def skip(self, bytes):
 		"""returns number of bytes where skipped
 		IOError"""
 		raise NotImplementedError


class OutputStream(object):
	def close(self):
		"""IOError"""
		raise NotImplementedError
	

	def flush(self):
		"""IOError"""
		raise NotImplementedError
	
	
	def write(self, data):
		"""IOError"""
		raise NotImplementedError


class Reader(object):
	def __init__(self, lock = None):
		pass


	def close(self):
		raise NotImplementedError
	
	
	def read(self, bytes = 1):
		raise NotImplementedError
	
	
	def ready(self):
		raise NotImplementedError
 
 	
 	def skip(self):
 		raise NotImplementedError
 
 
 class Writer(object):
	def __init__(self, lock = None):
		if lock is None:
			self._lock = RLock()
		else:
			self._lock = lock


	def close(self):
		raise NotImplementedError
	
	
	def flush(self):
		raise NotImplementedError
	

	def write(self, text):
		raise NotImplementedError


class LineReader(Reader):
	__LINE_END = ('\r\n', '\n')
	
	def __init__(self, reader):
		Reader.__init__(self)
		self.__reader = reader
		self.setLineEnd(self.__LINE_END)
	
	
	def setLineEnd(self, endList):
		self.__endList = endList


	def readLine(self, maxLineLength = 0, deleteEol = False):
		"""
		jak by mela metoda uplne spravne vypadat?
		co se ma delat pri prekroceni delky? vratit data? vyjimka?
		je spravne sem davat deleteEol?
		mel by byt ukoncovaci znak jen jeden?
		nastavovat omezeni globalne?
		
		maxLineLength - maximalni delka nacitaneho radku (<=0 neomezena)
		deleteEol - umazat nalezeny znak konce radku
		"""
		self.__line = ''
		while True:
			if self.__isEndedLine():
				return self.__correctedLine()
			char = self.read()
			if char == '':
				# pokud se nenacetlo nic nemela by to byt vyjimka? (self.__line == '')
				return self.__line
			self.__line += char
	
	
	def __isEndedLine(self):
		if maxLineLength > 0 and len(self.__line) >= maxLineLength:
			self.__end = ''
			return True
		for self.__end in self.__endList:
			if self.__line.endswith(self.__end):
				return True
		return False
	
	
	 def __correctedLine(self):
		if deleteEol:
			return self.__line[:-len(self.__end)]
		else:
			return self.__line


	def close(self):
		return self.__reader.close()
	
	
	def read(self, *args, **kwargs):
		return self.__reader.read(*args, **kwargs)
	
	
	def ready(self):
		return self.__reader.ready()
 
 	
 	def skip(self):
 		return self.__reader.skip()


class LineWriter(Writer):
	def __init__(self, writer):
		self.__writer = writer
		

	def newLine(self):
		self.write('\n')
	
	
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

