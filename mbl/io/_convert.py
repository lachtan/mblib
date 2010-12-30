
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class ByteToUnicode(object):
	def __init__(self, inputStream, encoding):
		super(InputStreamReader, self).__init__()		
		self.__inputStream = inputStream
		codecs.lookup(encoding)
		self.__encoding = encoding
		self.__buffer = ''
		
	
	def read(self, chars = 1):
		# pracuje se self.__buffer
		# bytes se musi nejak kouzelne nacitat
		data = self.__inputStream(bytes)
		# pokus se cast textu dekodovat
		# UnicodeDecodeError
		pass
	
	
	def isReady(self):
		return False
		
	
	def close(self):
		return self.__inputStream.close()


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class UnicodeToByte(object):
	def __init__(self, outputStream, encoding):
		super(OutputStreamWriter, self).__init__()		
		self.__outputStream = outputStream
		codecs.lookup(encoding)
		self.__encoding = encoding


	def flush(self):
		return self.__outputStream.flush()


	def write(self, text):
		super(OutputStreamWriter, self).write(text)
		# UnicodeEncodeError -> prebalit do IOError?
		data = text.encode(self.__encoding)
		bytes = self.__outputStream.write(data)
		# co kdyz je bytes != len(data) ? jak to prepoctu na unicode znaky?
		return len(text)

