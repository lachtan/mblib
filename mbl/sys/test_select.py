"""
Scenare
blokovani - to asi neotestujem -> nekonecno
po case navrat
prisel signal



#class Test(object):
simpleSelect = _SimpleSelect(None)
timeout = 123
simpleSelect.readReady(timeout)
simpleSelect.writeReady(timeout)

"""

import unittest
from mbl.sys.select import SimpleSelect
from mbl.io import Timeout


class TestableSimpleSelect(SimpleSelect):
	def __init__(self, stream):
		super(TestableSimpleSelect, self).__init__(stream)
	
	
	def setSelect(self, value):
		self.__selectValue = value
	
	
	def _select(self, *args):
		#print 'select%s' % str(args)
		return self.__selectValue
	
	
	def _time(self):
		return 112233


class SimpleSelectTest(unittest.TestCase):
	def setUp(self):
		self.__stream = None
		self.__simpleSelect = TestableSimpleSelect(self.__stream)
	
	
	def test_immediatelyReadReady(self):
		selectValue = [[self.__stream], [], []]
		self.__simpleSelect.setSelect(selectValue)
		self.assertTrue(self.__simpleSelect.readReady(Timeout.NONBLOCK))
	
	
	def xxx(self):
		mocks = MockRepository()
		simulatedSimpleSelect = mocks.StrictMock(SimpleSelect)
		stream = None
		
		mocks.record()
		simulatedSimpleSelect.init(stream)
		args = ([stream], [], [], Timeout.NONBLOCK)
		simulatedSimpleSelect._select(*args)
		selectValue = [[self.__stream], [], []]
		lastCall(selectValue)
		mocks.stopRecord()
		
		self.assertTrue(simulatedSimpleSelect.readReady(Timeout.NONBLOCK))
		mocks.verify(simulatedSimpleSelect)
		
			
	

