"""
14.1.2011
FS operace
class File - zjistuje informace o konkretni ceste
class ImmutableFile - zjisti informace pouze pri vytvoreni
- spojovani cest pres operator '+'
Prochazeni adresarovou strukturou
- moznost rekurze
- filtrovani ktere polozky se pouziji
- moznost zkraceneho vyhodnocovani (pokud adresar nevyhovi filtru, uz se v nem
  ani dale nehleda)
- uplne prochazeni stromem
- omezeni urovne zanoreni
- casto pouzivane filtry
- ignorovani chyb behem prochazeni stromu nebo volani error handleru, ktery
  posoudi, zda lze chybu ignorovat ci nikoliv
"""


import re
from os import listdir
from os.path import join, isfile, isdir, basename, dirname, splitext


def nofilter(item):
	return True


# ------------------------------------------------------------------------------
# File
# ------------------------------------------------------------------------------

class File(object):
	def __init__(self, path):
		self.__path = path


	def __str__(self):
		return self.__path


	def __eq__(self, other):
		return self.__path == other.path()


	def path(self):
		return self.__path


	def exists(self):
		return exists(self.__path)


	def isFile(self):
		return isfile(self.__path)


	def isDirectory(self):
		return isdir(self.__path)


	def baseName(self):
		return basename(self.__path)


	def dirName(self):
		return dirname(self.__path)


	def splitExt(self):
		return splitext(self.baseName())


	def fileName(self):
		return self.splitExt()[0]


	def extension(self):
		return self.splitExt()[1]


	def stat(self):
		# nevratit nejakou hezci strukturu?
		return stat(self.__path__)


	"""
	abspath
	atime
	mtime
	ctime
	size
	islink
	normpath
	realpath
	"""


# ------------------------------------------------------------------------------
# ImmutableFile
# ------------------------------------------------------------------------------

class ImmutableFile(object):
	def __init__(self, path):
		self.__path = path
	

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class TreeScanner(object):
	def __init__(self, path):
		self.__path = path
		self.setFilter(self.__noFilter)
		self.setShortEval(False)
		self.setMaxDepth(None)
		self.setFileClass(File)
	
	
	def setFilter(self, fileFilter):
		self.__fileFilter = fileFilter
	
	
	def setShortEval(self, shortEval):
		self.__shortEval = shortEval
	
	
	def setMaxDepth(self, maxDepth):
		self.__maxDepth = maxDepth
	
	
	def setErrorHandler(self, errorHandler):
		self.__errorHandler = errorHandler
	
	
	def setIgnoreErrors(self, ignoreErrors):
		self.__ignoreErrors = ignoreErrors
	
	
	def setFileClass(self, fileClass):
		self.__fileClass = fileClass
	
	
	def files(self):
		for file in self.__listFilesRecursive(self.__path, 0):
			if self.__shortEval or self.__fileFilter(file):
				yield file
	
	
	def __listFilesRecursive(self, path, depth):
		if self.__maxDepth is not None and depth > self.__maxDepth:
			return
		files = list(self.__listFiles(path))
		for file in files:
			if not file.isDirectory():
				yield file
		for file in files:
			if file.isDirectory():
				yield file
				for innerFile in self.__listFilesRecursive(file.path(), depth + 1):
					yield innerFile


	def __listFiles(self, path):
		for filename in self._listdir(path):
			file = self.__fileClass(join(path, filename)) 
			if not self.__shortEval or self.__fileFilter(file):
				yield file
	
	
	def __noFilter(self, file):
		return True
	
	
	def _listdir(self, path):
		return listdir(path)
	



"""
def documentFilter(file):
	return numberDirectoryFilter(file) or textFilesFilter(file)


def numberDirectoryFilter(file):
	return file.isdir() and file.basename().isdigit()


def textFilesFilter(file):
	return re.search(r'.+\.(doc|pdf|rtf|txt)', file.basename(), re.I)



for file in filter(methodcaller('isfile'), File('.').listFilesRecursive(documentFilter)):
	print file

"""
