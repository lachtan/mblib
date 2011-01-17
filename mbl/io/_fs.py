"""
Jake metody by jeste mel mit File? YAGNI!

implementovat?
abspath - normpath(join(os.getcwd(), path))
realpath

zpracovavat symlink kdyz je to adresar? -> cyklicke odkazy
skakat na dalsi fs?
vytvorit prvne skutecnou cestu realpath() ?
jak testovat?
"""

import re
import os
import os.path
from fnmatch import fnmatch
from datetime import datetime


# ------------------------------------------------------------------------------
# BaseFile
# ------------------------------------------------------------------------------

class BaseFile(object):
	def __init__(self, path):
		self.__path = path


	def __str__(self):
		return self.__path


	def __eq__(self, other):
		return self.__path == other.path()


	def path(self):
		return self.__path


	def isAbsolute(self):
		return os.path.isabs(self.__path)


	def normalizePath(self):
		return os.path.normpath(self.__path)


	def baseName(self):
		return os.path.basename(self.__path)


	def dirName(self):
		return os.path.dirname(self.__path)


	def splitExt(self):
		return os.path.splitext(self.baseName())


	def fileName(self):
		return self.splitExt()[0]


	def extension(self):
		return self.splitExt()[1]


	def _datetime(self, stamp):
		return datetime.fromtimestamp(stamp)


# ------------------------------------------------------------------------------
# File
# ------------------------------------------------------------------------------

class File(BaseFile):
	def __init__(self, path):
		super(File, self).__init__(path)
		self.__path = path


	def exists(self):
		return os.path.exists(self.__path)


	def isFile(self):
		return os.path.isfile(self.__path)


	def isDirectory(self):
		return os.path.isdir(self.__path)


	def isLink(self):
		return os.path.islink(self.__path)


	def isMount(self):
		return os.path.ismount(self.__path)


	def stat(self):
		return os.stat(self.__path__)


	def size(self):
		return os.path.getsize(self.__path__)


	def atime(self):
		return self._datetime(os.path.getatime(self.__path__))


	def mtime(self):
		return self._datetime(os.path.getmtime(self.__path__))


	def ctime(self):
		return self._datetime(os.path.getctime(self.__path__))


# ------------------------------------------------------------------------------
# ImmutableFile
# ------------------------------------------------------------------------------

class ImmutableFile(BaseFile):
	def __init__(self, path):
		super(ImmutableFile, self).__init__(path)
		self.__path = path
		self.__stat = stat(path)
		self.__isMount = os.path.ismount(path)


	def exists(self):
		return True


	def isFile(self):
		return stat.S_ISREG(self.__stat.st_mode)


	def isDirectory(self):
		return stat.S_ISDIR(self.__stat.st_mode)


	def isLink(self):
		return stat.S_ISLNK(self.__stat.st_mode)


	def isMount(self):
		raise self.__isMount


	def stat(self):
		return self.__stat


	def size(self):
		return self.__stat.st_size


	def atime(self):
		return self._datetime(self.__stat.st_atime)


	def mtime(self):
		return self._datetime(self.__stat.st_mtime)


	def ctime(self):
		return self._datetime(self.__stat.st_actime)


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
		self.setErrorHandler(self.__raiseError)


	def setFilter(self, fileFilter):
		self.__fileFilter = fileFilter


	def setShortEval(self, shortEval):
		self.__shortEval = shortEval


	def setMaxDepth(self, maxDepth):
		self.__maxDepth = maxDepth


	def setErrorHandler(self, errorHandler):
		self.__errorHandler = errorHandler


	def ignoreErrors(self):
		self.setErrorHandler(self.__ignoreError)


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
			yield file
		for file in files:
			if file.isDirectory() and not file.isLink():
				for innerFile in self.__listFilesRecursive(file.path(), depth + 1):
					yield innerFile


	def __listFiles(self, path):
		for filename in self.__listDirectory(path):
			file = self.__fileClass(os.path.join(path, filename))
			if not self.__shortEval or self.__fileFilter(file):
				yield file


	def __noFilter(self, file):
		return True


	def __listDirectory(self, path):
		try:
			return self._listdir(path)
		except OSError, exception:
			self.__errorHandler(exception)
			return []


	def __raiseError(self, exception):
		raise exception


	def __ignoreError(self, exception):
		pass


	def _listdir(self, path):
		return os.listdir(path)


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

def globeFilter(mask):
	return lambda file: fnmatch(file.baseName(), mask)


