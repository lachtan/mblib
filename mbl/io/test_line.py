import unittest
from StringIO import StringIO
from mbl.io import LineInputStream


class FakeInputStream(object):
	def __init__(self, buffer):
		self.__stream = StringIO(buffer)
	
	
	def read(self, bytes):
		return self.__stream.read(bytes)
	
	
class TestLineScanner(unittest.TestCase):
	def setUp(self):
		inputStream = FakeInputStream('one line\ntwo line\r\nth\reline')
		self.__lineInputStream = LineInputStream(inputStream)
	
	
	def tearDown(self):
		self.__lineInputStream = None


	def test_basicFuncionality(self):
		expectedLines = ['one line\n', 'two line\r\n', 'th\reline']
		self.__checkLines(expectedLines)
	
	
	def test_badTypeEndLineList(self):
		self.assertRaises(AttributeError, self.__lineInputStream.setEndLineList, [u'\r'])
	
	
	def test_badLengthEndLineList(self):
		self.assertRaises(AttributeError, self.__lineInputStream.setEndLineList, [''])


	def test_endLineList(self):
		self.__lineInputStream.setEndLineList(['\r'])
		expectedLines = ['one line\ntwo line\r', '\nth\r', 'eline']
		self.__checkLines(expectedLines)
	
	
	def test_deleteEol(self):
		self.__lineInputStream.setDeleteEol(True)
		expectedLines = ['one line', 'two line', 'th\reline']
		self.__checkLines(expectedLines)
	
	
	def test_maxLineLength(self):
		self.__lineInputStream.setMaxLineLength(5)
		expectedLines = ['one l', 'ine\n', 'two l', 'ine\r\n', 'th\rel', 'ine']
		self.__checkLines(expectedLines)
	
	
	def test_lineGenerator(self):
		lines = [line for line in self.__lineInputStream]
		expectedLines = ['one line\n', 'two line\r\n', 'th\reline']
		self.assertEqual(expectedLines, lines)
		
	
	def __checkLines(self, expectedLines):
		lines = []
		while True:
			line = self.__lineInputStream.readLine()
			if line == '':
				break
			lines.append(line)
		self.assertEqual(expectedLines, lines)

