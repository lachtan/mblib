"""
mbl/util/create.py
original from Petr Cervenka

Crate Design Pattern
"""

import re
from operator import itemgetter

__all__ = (
	'CrateMeta',
	'Crate'
)


class CrateMeta(type):
	def __init__(cls, name, bases, dict):
		super(CrateMeta, cls).__init__(name, bases, dict)
		for key in cls.keys():
			setattr(cls, key, property(itemgetter(key)))


class Crate(object):
	def __init__(self, params):
		super(Crate, self).__init__()
		self.__checkMissingKeys(params)
		self.__setValues(params)
	
	
	def __checkMissingKeys(self, params):
		requiredKeys = set(self.attributes().keys())
		realKeys = set(params.keys())
		missKeys = requiredKeys - realKeys		
		if missKeys:
			raise AttributeError('Missing keys: %s' % list(missKeys))

	
	def __keyChecker(self, key):
		if not re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', key):
			raise AttributeError('Bad key name %s' % key)


	def __setValues(self, params):
		self.__values = {}
		for key, requiredType in self.attributes().items():
			value = params[key]
			self.__checkType(requiredType, value)
			self.__values[key] = value
	
	
	def __checkType(self, requiredType, value):
		if (requiredType is not None) and (not isinstance(value, requiredType)):
			raise TypeError("Value %s isn't %s" % (repr(value), str(requiredType)))


	def __str__(self):
		return str(self.__values)


	def __repr__(self):
		return repr(self.__values)


	def __getitem__(self, key):
		return self.__values[key]


	def __iter__(self):
		for key, value in self.__values.items():
			yield key, value
		
	
	def __contains__(self, key):
		return key in self.keys()
	
	
	def __hash__(self):
		return hash(tuple(sorted(self.__values.items())))
	
	
	def __eq__(self, other):
		return dict(self) == dict(other)


	@classmethod
	def attributes(cls):
		raise NotImplementedError()


	@classmethod
	def keys(cls):
		return tuple(cls.attributes().keys())
	
	
	@staticmethod
	def createClass(name, attributes):
		_attributes = dict(attributes)
		
		class _Crate(Crate):
			__metaclass__ = CrateMeta
			
			@classmethod
			def attributes(cls):
				return _attributes
		
		_Crate.__name__ = name
		return _Crate



# EOF
