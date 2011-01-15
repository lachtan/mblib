import re
from mbl.io import TreeScanner

class FakeFile(object):
	def __init__(self, path):
		self.__path = path
	
	
	def __str__(self):
		return 'FakeFile(%s)' % self.__path


def pyFilter(file):
	return file.extension().lower() == '.py'

scanner = TreeScanner('.')
scanner.setFilter(pyFilter)
scanner.setMaxDepth(2)
for file in scanner.files():
	print file