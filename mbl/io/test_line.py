import unittest
from StringIO import StringIO
from mbl.io import LineInputStream


class FakeInputStream(object):
	def __init__(self, buffer):
		self.__stream = StringIO(buffer)
	
	
	def read(self, bytes):
		return self.__stream.read(bytes)
	
	
class TestLineScanner(unittest.TestCase):
	def test_basicFuncionality(self):
		lineInputStream = self.__prepareLineInputStream()
		expectedLines = ['one line\n', 'two line\r\n', 'th\reline']
		self.__checkLines(expectedLines, lineInputStream)
	
	
	def test_badTypeEndLineList(self):
		lineInputStream = self.__prepareLineInputStream()
		self.assertRaises(AttributeError, lineInputStream.setEndLineList, [u'\r'])
	
	
	def test_badLengthEndLineList(self):
		lineInputStream = self.__prepareLineInputStream()
		self.assertRaises(AttributeError, lineInputStream.setEndLineList, [''])


	def test_endLineList(self):
		lineInputStream = self.__prepareLineInputStream()
		lineInputStream.setEndLineList(['\r'])
		expectedLines = ['one line\ntwo line\r', '\nth\r', 'eline']
		self.__checkLines(expectedLines, lineInputStream)
	
	
	def test_deleteEol(self):
		lineInputStream = self.__prepareLineInputStream()
		lineInputStream.setDeleteEol(True)
		expectedLines = ['one line', 'two line', 'th\reline']
		self.__checkLines(expectedLines, lineInputStream)
	
	
	def test_maxLineLength(self):
		lineInputStream = self.__prepareLineInputStream()
		lineInputStream.setMaxLineLength(5)
		expectedLines = ['one l', 'ine\n', 'two l', 'ine\r\n', 'th\rel', 'ine']
		self.__checkLines(expectedLines, lineInputStream)
	
	
	def test_lineGenerator(self):
		lineInputStream = self.__prepareLineInputStream()
		lines = [line for line in lineInputStream]
		expectedLines = ['one line\n', 'two line\r\n', 'th\reline']
		self.assertEqual(expectedLines, lines)
		
	
	def __prepareLineInputStream(self):
		inputStream = FakeInputStream('one line\ntwo line\r\nth\reline')
		lineInputStream = LineInputStream(inputStream)
		return lineInputStream
	
	
	def __checkLines(self, expectedLines, lineInputStream):
		lines = []
		while True:
			line = lineInputStream.readLine()
			if line == '':
				break
			lines.append(line)
		self.assertEqual(expectedLines, lines)

