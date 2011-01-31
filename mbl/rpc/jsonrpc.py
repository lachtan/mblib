"""
Za pouziti technologie JSON se snazi doresit veskere nedostatky XML-RPC, kde
nam predevsim chybi vyjimky, vlastni datove typy, datova narocnost prenosu
jakoz i casova narocnost parsovani XML. Binarni format se nam jevi jako
nevhodny, nebot je necitelny a spatne rozsiritelny. Naopak textova
reprzentace JSON dovoluje prenest libovolna data. Knihovna primarne nepracuje
s zadnym prenosovym mediem. Realizuje jen prevody RPC do textoveho ramce,
z textoveho ramce zavolat registrovanou metodu a pote zas vracena data nebo
vyjimku prenest do textu. V poslednim kroku je tento text prevedn do navratove
hodnoty puvodniho volani. Knihovna je urcena pro LEMI.

{"~~class~~": {"class": "MyType", "args": [1.627282, true, 2]}}

Pokud je trida serializovatelna do JSON musi implementovat metodu
jsonArgs

JSON-RPC ramec

version: 1.0
type: call
name: "method-name"
data: [args]

version: 1.0
type: response
name: "method-name"
data: return-value

version: 1.0
type: exception
name: "exception-name"
data: [args]

"""

import re
import string
import cjson as json
import weakref
from base64 import b64encode, b64decode
from types import *


__version__ = '1.0'
JSON_EXPORTER = 'jsonArgs'


class RpcError(StandardError):
	@staticmethod
	def create(exception):
		return RpcError(exception(*args))


class RpcProcessingError(RpcError):
	pass


class CreateObjectError(StandardError):
	pass


# ------------------------------------------------------------------------------
# ToJsonConvertor
# ------------------------------------------------------------------------------

class ToJsonConvertor(object):
	__baseTypes = (
		NoneType,
		DictType,
		ListType,
		TupleType,
		StringType,
		UnicodeType,
		IntType,
		LongType,
		FloatType,
		BooleanType
	)
	__printablePattern = re.compile('[%s]+' % re.escape(string.printable))
	__minStringLength = 20
	__base64Weight = 1.5
	__nonPrintableWeight = 5


	def __init__(self, rpcContext):
		self.__rpcContext = weakref.proxy(rpcContext)


	def __convertList(self, lst):
		return map(self.__convert, lst)


	def __convertDict(self, dct):
		data = {}
		for key, value in dct.iteritems():
			data[str(key)] = self.__convert(value)
		return data


	def __isBinary(self, data):
		totalLength = len(data)
		if totalLength < self.__minStringLength:
			return False
		notPrintableLength = len(self.__printablePattern.sub('', data))
		jsonLength = totalLength + self.__nonPrintableWeight * notPrintableLength
		base64Length = totalLength * self.__base64Weight
		return jsonLength > base64Length


	def __convertString(self, data):
		if self.__isBinary(data):
			base64Data = b64encode(data)
			value = {
				'~~class~~': {
					'class': '~~base64~~',
					'args': [base64Data]
				}
			}
			return value
		else:
			return data


	def __convertClass(self, obj):
		typeInfo = self.__rpcContext.getClassInfo(obj)
		convertor = typeInfo['convertor']
		if convertor:
			args = convertor(obj)
		else:
			args = getattr(obj, JSON_EXPORTER)()
		data = {
			'~~class~~': {
				'class': typeInfo['name'],
				'args': self.__convert(args)
			}
		}
		return data


	def __isConvertable(self, obj):
		return self.__rpcContext.getClassInfo(obj) is not None


	def __convert(self, value):
		valueType = type(value)
		if valueType in (ListType, TupleType):
			return self.__convertList(value)
		elif valueType == DictType:
			return self.__convertDict(value)
		elif valueType == StringType:
			return self.__convertString(value)
		elif valueType in self.__baseTypes:
			return value
		elif self.__isConvertable(value):
			return self.__convertClass(value)
		else:
			raise ValueError("Can't convert %s to JSON" % repr(value))


	def __prepareBase(self):
		params = {
			'version': __version__
		}
		return params


	def __encode(self, value):
		try:
			return json.encode(value)
		except json.EncodeError, e:
			raise RpcProcessingError(*e.args)


	def convert(self, value):
		return self.__encode(self.__convert(value))


	def prepareCall(self, method, args):
		params = self.__prepareBase()
		params['type'] = 'call'
		params['name'] = str(method)
		if type(args) not in (ListType, TupleType):
			raise AttributeError
		params['data'] = args
		return self.convert(params)


	def prepareResponse(self, method, value):
		params = self.__prepareBase()
		params['type'] = 'response'
		params['name'] = str(method)
		params['data'] = value
		return self.convert(params)


	def prepareException(self, name, args):
		params = self.__prepareBase()
		params['type'] = 'exception'
		params['name'] = str(name)
		if type(args) not in (ListType, TupleType):
			raise AttributeError
		params['data'] = args
		return self.convert(params)


# ------------------------------------------------------------------------------
# FromJsonConvertor
# ------------------------------------------------------------------------------

class FromJsonConvertor(object):
	def __init__(self, rpcContext):
		self.__rpcContext = weakref.proxy(rpcContext)


	def loads(self, value):
		return json.decode(value)


	def __checkClassType(self, value):
		return type(value) == DictType and len(value) == 1 and '~~class~~' in value


	def __convertClass(self, value):
		# dalsi kontroly!
		info = value['~~class~~']
		typeName = info['class']
		if typeName == '~~base64~~':
			return b64decode(info['args'][0])
		else:
			args = self.__convert(info['args'])
			return self.__createObject(typeName, args)


	def __createObject(self, typeName, args):
		typeInfo = self.__rpcContext.getTypeInfo(typeName)
		if typeInfo is None:
			raise CreateObjectError('Unknown type %s' % str(typeName))
		cls = typeInfo['class']
		return cls(*args)


	def __convertList(self, lst):
		data = []
		for item in lst:
			data.append(self.__convert(item))
		return data


	def __convertDict(self, dct):
		data = {}
		for key, value in dct.iteritems():
			data[key] = self.__convert(value)
		return data


	def __convert(self, value):
		valueType = type(value)
		if self.__checkClassType(value):
			return self.__convertClass(value)
		elif valueType in (ListType, TupleType):
			return self.__convertList(value)
		elif valueType == DictType:
			return self.__convertDict(value)
		else:
			return value


	def convert(self, value):
		data = self.loads(value)
		return self.__convert(data)


# ------------------------------------------------------------------------------
# RpcContext
# ------------------------------------------------------------------------------

class RpcContext(object):
	def __init__(self):
		self.__toJsonConvertor = ToJsonConvertor(self)
		self.__fromJsonConvertor = FromJsonConvertor(self)
		self.__names = {}
		self.__types = {}


	def version(self):
		return __version__


	def registerType(self, cls, toJsonConvertor = None):
		self.registerNamedType(cls.__name__, cls, toJsonConvertor)


	def registerNamedType(self, typeName, cls, toJsonConvertor = None):
		if type(cls) not in (TypeType, ClassType):
			raise AttributeError('%s is not class' % str(cls))
		if typeName in self.__names:
			raise NameError('Type "%s" already registered' % typeName)
		if cls in self.__types:
			raise KeyError('Type "%s" already registered' % str(cls))
		if toJsonConvertor is None and not hasattr(cls, JSON_EXPORTER):
			raise AttributeError("Class hasn't method %s" % JSON_EXPORTER)
		self.__types[cls] = {
			'name': typeName,
			'class': cls,
			'convertor': toJsonConvertor
		}
		self.__names[typeName] = cls


	def getClassInfo(self, obj):
		cls = obj.__class__
		if cls in self.__types:
			return self.__types[cls].copy()
		else:
			return None


	def getTypeInfo(self, typeName):
		if typeName in self.__names:
			cls = self.__names[typeName]
			return self.__types[cls].copy()
		else:
			return None


	def dumps(self, value):
		return self.__toJsonConvertor.convert(value)


	def loads(self, value):
		return self.__fromJsonConvertor.convert(value)


	def call(self, method, args):
		return self.__toJsonConvertor.prepareCall(method, args)


	def response(self, method, value):
		return self.__toJsonConvertor.prepareResponse(method, value)


	def exception(self, name, args):
		return self.__toJsonConvertor.prepareException(name, args)


# ------------------------------------------------------------------------------
# RpcClient
# ------------------------------------------------------------------------------

class RpcClient(object):
	__headers = (
		'version',
		'type',
		'name',
		'data'
	)


	def __init__(self, rpcContext):
		self.__rpcContext = rpcContext


	def __checkEnvelope(self, answer):
		if type(answer) != DictType:
			raise RpcProcessingError("Answer is not Dict type (%s)" % str(type(answer)))
		for header in self.__headers:
			if header not in answer:
				raise RpcProcessingError('Missing header %s' % header)
		if answer['type'] not in ('response', 'exception'):
			raise RpcProcessingError('Unknown type %s' % str(answer['type']))


	def call(self, method, args):
		request = self.prepare(method, args)
		response = self.process(request)
		return self.evalute(response)


	def process(self, jsonData):
		raise NotImplemented


	def prepare(self, method, args):
		return self.__rpcContext.call(method, args)


	def evalute(self, response):
		answer = self.__rpcContext.loads(response)
		self.__checkEnvelope(answer)
		if answer['type'] == 'response':
			return answer['data']
		elif answer['type'] == 'exception':
			raise answer['data']
		else:
			raise RpcProcessingError('Unknown type %s' % answer['type'])


# ------------------------------------------------------------------------------
# RpcProxy
# ------------------------------------------------------------------------------

class RpcProxy(object):
	def __init__(self, rpcClient):
		self.__rpcClient = rpcClient
		self.__createInterface()


	def __createInterface(self):
		for method in self.__rpcClient.call('~~getInterface~~'):
			methodName = method['name']
			self.__createMethod(methodName)


	def __createMethod(self, methodName):
		def callWithName(*args):
			return self.__call(methodName, args)

		return callWithName


	def __call(self, methodName, args):
		return self.__rpcClient.call(methodName, args)


# ------------------------------------------------------------------------------
# RpcServer
# ------------------------------------------------------------------------------

class RpcServer(object):
	__headers = (
		'version',
		'type',
		'name',
		'data'
	)


	def __init__(self, rpcContext):
		self.__methods = {}
		self.__rpcContext = rpcContext


	def registerMethod(self, method, callback):
		self.__methods[method] = {
			'callback': callback
		}


	def registerInterface(self, obj):
		for name, method in obj.rpcMethods():
			self.registerMethod(name, method)


	def __checkEnvelope(self, request):
		if type(request) != DictType:
			raise RpcProcessingError('Bad envleope type (%s)' % str(type(request)))
		for header in self.__headers:
			if header not in request:
				raise RpcProcessingError("Mising envleope header '%s'" % header)
		if request['type'] != 'call':
			raise RpcProcessingError('Unknown type %s' % str(answer['type']))
		if type(request['data']) not in (ListType, TupleType):
			raise RpcProcessingError('Bad data type %s' % str(type(request['data'])))


	def __call(self, jsonData):
		try:
			request = self.__rpcContext.loads(jsonData)
		except CreateObjectError, e:
			raise RpcError(e)
		self.__checkEnvelope(request)
		method = request['name']
		args = request['data']
		if method not in self.__methods:
			raise RpcProcessingError('Bad method name %s' % str(method))
		callback = self.__methods[method]['callback']
		# TODO kontrola poctu argumentu
		answer = callback(*args)
		return self.__rpcContext.response(method, answer)


	def __exception(self, exception):
		return self.__rpcContext.exception(exception.__class__.__name__, exception.args)


	def call(self, jsonData):
		try:
			return self.__call(jsonData)
		except RpcProcessingError, e:
			return self.__exception(e)
		except RpcError, e:
			return self.__exception(e.args[0])


