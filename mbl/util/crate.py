"""
mbl/util/create.py
original from Petr Cervenka

Design Pattern Crate
"""

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
		requiredKeys = set(self.conversions().keys())
		realKeys = set(params.keys())
		missKeys = requiredKeys - realKeys		
		if missKeys:
			raise AttributeError('Missing keys: %s' % list(missKeys))

	
	def __setValues(self, params):
		self.__values = {}
		for key, conversion in self.conversions().items():
			value = params[key]
			if conversion is not None:
				value = conversion(value)
			self.__values[key] = value


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
		return hash(self.__values)
	
	
	def __eq__(self, other):
		return dict(self) == dict(other)


	@classmethod
	def conversions(cls):
		raise NotImplementedError()


	@classmethod
	def keys(cls):
		return cls.conversions().keys()
	
	
	@staticmethod
	def createClass(name, conversions):
		class TempCrate(Crate):
			__metaclass__ = CrateMeta
			
			@classmethod
			def conversions(cls):
				return conversions

		TempCrate.__name__ = name
		return TempCrate



# EOF
