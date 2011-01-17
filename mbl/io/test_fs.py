import re
from mbl.io import TreeScanner

class FakeFile(object):
	def __init__(self, path):
		self.__path = path


	def __str__(self):
		return 'FakeFile(%s)' % self.__path


def pyFilter(file):
	return file.extension().lower() == '.py'


def errorHandler(error):
	print 'ERROR', error, error.args


from sys import argv

path = argv[1]
scanner = TreeScanner(path)
scanner.setFilter(pyFilter)
#scanner.setMaxDepth(2)
scanner.setErrorHandler(errorHandler)
#scanner.ignoreErrors()
for file in scanner.files():
	print file