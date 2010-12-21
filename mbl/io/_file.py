import os
from mbl.io import InputStream, OutputStream


# ------------------------------------------------------------------------------
# FileInputStream
# ------------------------------------------------------------------------------

class FileInputStream(InputStream):
	def __init__(self, pathname):
		super(FileInputStream, self).__init__()
		self.__file = file(pathname, 'rb')


	def isReady(self):
		# POZOR muze otevrit rouru a pak se tam ty data budou zjevovat prubezne
		self._checkClosed()
		return True


	def availableBytes(self):
		self._checkClosed()

		actualOffset = self.tell()
		endOffset = self.seek(0, os.SEEK_END)
		self.seek(actualOffset, os.SEEK_CUR)
		return endOffset - endOffset


	def close(self):
		self._checkClosed()
		self.__file.close()


	def read(self, bytes = 1):
		super(FileInputStream, self).read(bytes)
		return self.__file.read(bytes)


 	def skip(self, bytes):
 		super(FileInputStream, self).skip(bytes)
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


