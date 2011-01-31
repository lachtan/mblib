import unittest
from mbl.rpc.jsonrpc import RpcContext, ToJsonConvertor, FromJsonConvertor, CreateObjectError

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class TypeWithoutJsonConvert(object):
	def __init__(self, value):
		self.__value = value


	def value(self):
		return self.__value


	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.__value == other.value()


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

class TypeWithJsonConvert(TypeWithoutJsonConvert):
	def __init__(self, value):
		TypeWithoutJsonConvert.__init__(self, value)


	def jsonArgs(self):
		return [self.value()]


# ------------------------------------------------------------------------------
# RpcContext
# ------------------------------------------------------------------------------

class RpcContextTest(unittest.TestCase):
	def setUp(self):
		self.__rpcContext = RpcContext()


	def test_registerBadType(self):
		self.assertRaises(AttributeError, self.__rpcContext.registerNamedType, 'int', 23)


	def test_registerTypeTwiceName(self):
		self.__rpcContext.registerNamedType('test', TypeWithJsonConvert)
		self.assertRaises(NameError, self.__rpcContext.registerNamedType, 'test', TypeWithJsonConvert)


	def test_registerTypeTwiceType(self):
		self.__rpcContext.registerNamedType('test', TypeWithJsonConvert)
		self.assertRaises(KeyError, self.__rpcContext.registerNamedType, 'other', TypeWithJsonConvert)


	def test_registerTypeBadClass(self):
		self.assertRaises(AttributeError, self.__rpcContext.registerNamedType, 'test', TypeWithoutJsonConvert)


	def test_binary(self):
		data = 10 * ''.join(map(chr, range(256)))
		jsonData = self.__rpcContext.dumps(data)
		decodedData = self.__rpcContext.loads(jsonData)
		self.assertEquals(data, decodedData)


# ------------------------------------------------------------------------------
# ToJsonConvertor
# ------------------------------------------------------------------------------

class ToJsonConvertorTest(unittest.TestCase):
	def setUp(self):
		self.__rpcContext = RpcContext()
		self.__toJsonConvertor = ToJsonConvertor(self.__rpcContext)


	def test_convert(self):
		self.__assertConvert('null', None)
		self.__assertConvert('false', False)
		self.__assertConvert('true', True)
		self.__assertConvert('123', 123)
		self.__assertConvert('-123', -123)
		self.__assertConvert('1.23', 1.23)
		self.__assertConvert('"some text"', 'some text')
		self.__assertConvert(r'"some unicode \u1234"', u'some unicode \u1234')
		self.__assertConvert('[1, 2, 3]', [1, 2, 3])
		self.__assertConvert('[1, 2, 3]', (1, 2, 3))
		self.__assertConvert('{"1": 2, "2": 3}', {1: 2, 2: 3})


	def __assertConvert(self, jsonData, value):
		self.assertEquals(jsonData, self.__toJsonConvertor.convert(value))


	def test_convertClassWithConvert(self):
		self.__rpcContext.registerType(TypeWithJsonConvert)
		value = TypeWithJsonConvert(123)
		expected = '{"~~class~~": {"args": [123], "class": "TypeWithJsonConvert"}}'
		self.assertEquals(expected, self.__toJsonConvertor.convert(value))


	def test_convertClassWithoutConvert(self):
		self.__rpcContext.registerType(TypeWithoutJsonConvert, self.__convert)
		value = TypeWithoutJsonConvert(123)
		expected = '{"~~class~~": {"args": [123], "class": "TypeWithoutJsonConvert"}}'
		self.assertEquals(expected, self.__toJsonConvertor.convert(value))


	def __convert(self, obj):
		return [obj.value()]


# ------------------------------------------------------------------------------
# FromJsonConvertor
# ------------------------------------------------------------------------------

class FromJsonConvertorTest(unittest.TestCase):
	def setUp(self):
		self.__rpcContext = RpcContext()
		self.__fromJsonConvertor = FromJsonConvertor(self.__rpcContext)


	def test_convert(self):
		self.__assertConvert(None, 'null')
		self.__assertConvert(False, 'false')
		self.__assertConvert(True, 'true')
		self.__assertConvert(123, '123')
		self.__assertConvert(-123, '-123')
		self.__assertConvert(1.23, '1.23')
		self.__assertConvert('some text', '"some text"', )
		self.__assertConvert(u'some unicode \u1234', r'"some unicode \u1234"')
		self.__assertConvert([1, 2, 3], '[1, 2, 3]')
		self.__assertConvert({'1': 2, '2': 3}, '{"1": 2, "2": 3}')


	def test_convertClass(self):
		self.__rpcContext.registerType(TypeWithJsonConvert)
		jsonData = '{"~~class~~": {"args": [123], "class": "TypeWithJsonConvert"}}'
		expectedValue = TypeWithJsonConvert(123)
		self.assertEquals(expectedValue, self.__fromJsonConvertor.convert(jsonData))


	def __assertConvert(self, expectedValue, jsonData):
		self.assertEquals(expectedValue, self.__fromJsonConvertor.convert(jsonData))


	def test_convertUnknownClass(self):
		jsonData = '{"~~class~~": {"args": [123], "class": "UnknownClass"}}'
		self.assertRaises(CreateObjectError, self.__fromJsonConvertor.convert, jsonData)


