import unittest
from mbl.util.crate import CrateMeta, Crate


class TestCrate(unittest.TestCase):	
	def setUp(self):
		self.__crate = self.__prepareBasicCrate()
	
	def tearDown(self):
		self.__crate = None
	

	def test_missingKey(self):
		_Crate = self.__prepareCrateClassByInheritance()
		params = {
			'key1': 10,
			'key2': 'anythink',
		}
		self.assertRaises(AttributeError, _Crate, params)
	
	
	def test_badValueType(self):
		_Crate = self.__prepareCrateClassByInheritance()
		params = {
			'key1': 'bad value',
			'key2': 'anythink',
			'key3': 1.23
		}
		self.assertRaises(TypeError, _Crate, params)
		
		
	def test_attributeAccess(self):
		self.assertEquals(10, self.__crate.key1)
		self.assertEquals('anythink', self.__crate.key2)
		self.assertEquals(1.23, self.__crate.key3)
	
	
	def test_dictAccess(self):
		self.assertEquals(10, self.__crate['key1'])
		self.assertEquals('anythink', self.__crate['key2'])
		self.assertEquals(1.23, self.__crate['key3'])
	
	
	def test_readOnlyAttributes(self):
		self.assertRaises(AttributeError, self.__executeCode, 'self.__crate.key1 = 1')
	
	
	def test_readOnlyDict(self):
		self.__crate = self.__prepareBasicCrate()
		self.assertRaises(AttributeError, self.__executeCode, "self.__crate['key1'] = 1")
	
	
	def test_containsKey(self):
		self.assertTrue('key1' in self.__crate)
		self.assertTrue('key2' in self.__crate)
		self.assertTrue('key3' in self.__crate)
		self.assertFalse('key4' in self.__crate)
	
	
	def test_keys(self):
		self.assertEquals(set(('key1', 'key2', 'key3')), set(self.__crate.keys()))
	
	
	def test_iter(self):
		params = {
			'key1': 10,
			'key2': 'anythink',
			'key3': 1.23
		}
		iterList = []
		for item in self.__crate:
			iterList.append(item)
		self.assertEquals(sorted(params.items()), sorted(iterList))
	
	
	def test_createClass(self):
		name = 'Crate1'
		attributes = {
			'key1': int,
			'key2': None,
			'key3': float
		}
		Crate1 = Crate.createClass(name, attributes)
		params = {
			'key1': 10,
			'key2': 'anythink',
			'key3': 1.23
		}		
		crate1 = Crate1(params)
	

	def __executeCode(self, code):
		eval(compile(code, '', 'single'))
	
	
	def __prepareCrateClassByInheritance(self):
		class _Crate(Crate):
			__metaclass__ = CrateMeta

			@classmethod
			def attributes(self):
				return {
					'key1': int,
					'key2': None,
					'key3': float
				}
		
		return _Crate
	
	
	def __prepareBasicCrate(self):
		_Crate = self.__prepareCrateClassByInheritance()
		params = {
			'key1': 10,
			'key2': 'anythink',
			'key3': 1.23
		}		
		return _Crate(params)
			
