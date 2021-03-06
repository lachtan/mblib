import unittest
from mbl.io import ByteArrayInputStream, ByteArrayOutputStream

TEST_DATA = 'some data in buffer'


# ------------------------------------------------------------------------------
# ByteArrayInputStream
# ------------------------------------------------------------------------------

class ByteArrayInputStreamTest(unittest.TestCase):
	def setUp(self):
		self.__inputStream = ByteArrayInputStream(TEST_DATA)


	def tearDown(self):
		self.__inputStream.close()
		self.__inputStream = None


	def test_ready(self):
		self.assertTrue(self.__inputStream.ready())
		data = self.__inputStream.read(100)
		self.assertTrue(self.__inputStream.ready())


	def test_readByteByByte(self):
		buffer = ''
		while True:
			byte = self.__inputStream.read(1)
			if byte == '':
				break
			buffer += byte
		self.assertEquals(TEST_DATA, buffer)


	def test_readMultiBytes(self):
		buffer = ''
		bytes = 0
		while True:
			bytes += 1
			byte = self.__inputStream.read(bytes)
			if byte == '':
				break
			buffer += byte
		self.assertEquals(TEST_DATA, buffer)


	def test_readOverload(self):
		data = self.__inputStream.read(1000)
		self.assertEquals(TEST_DATA, data)


	def test_endOfStream(self):
		self.__inputStream.read(1000)
		data = self.__inputStream.read(1000)
		self.assertEquals('', data)


	def test_skipAll(self):
		skipBytes = self.__inputStream.skip(1000)
		self.assertEquals(len(TEST_DATA), skipBytes)


	def test_skipPart(self):
		length = 0
		bytes = 0
		while True:
			bytes += 1
			skipBytes = self.__inputStream.skip(bytes)
			if skipBytes == 0:
				break
			length += skipBytes
		self.assertEquals(len(TEST_DATA), length)


	def test_doubleClose(self):
		inputStream = ByteArrayInputStream(TEST_DATA)
		inputStream.close()
		self.assertRaises(IOError, inputStream.close)


# ------------------------------------------------------------------------------
# ByteArrayOutputStream
# ------------------------------------------------------------------------------


class ByteArrayOutputStreamTest(unittest.TestCase):
	def setUp(self):
		self.__outputStream = ByteArrayOutputStream()


	def tearDown(self):
		self.__outputStream.close()
		self.__outputStream = None


	def test_write(self):
		parts = ('th', 'is is', ' some ', 't', 'ext')
		for part in parts:
			self.__outputStream.write(part)
		self.assertEquals(''.join(parts), self.__outputStream.buffer())

