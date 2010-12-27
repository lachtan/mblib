from __future__ import absolute_import
import select
import errno
from time import time
from mbl.io import Timeout


class SimpleSelect(object):
	__READ = 0
	__WRITE = 1
	
	
	def __init__(self, stream, timeout):
		self.__stream = stream
		self.__timeout = Timeout(timeout)
	
	
	def readReady(self):
		return self.__isReady(self.__READ)
	
	
	def writeReady(self):
		return self.__isReady(self.__WRITE)
		
	
	def __isReady(self, selectType):
		if self.__timeout.isBlock():
			return self.__isReadyBlock(selectType)
		else:
			return self.__isReadyWaiting(selectType)
	
	
	def __isReadyBlock(self, selectType):
		while True:
			try:
				return self.__select(selectType, self.__timeout.timeout())
			except SignalException:
				continue
			
	
	def __isReadyWaiting(self, selectType):
		startTime = time()
		timeout = self.__timeout.timeout()
		while timeout >= 0:
			try:
				return self.__select(selectType, timeout)
			except SignalException:
				duration = startTime - time()
				timeout = self.__timeout.timeout() - duration
		return False

	
	def __select(self, selectType, timeout):
		args = [[], [], [], timeout]
		args[selectType].append(self.__stream)
		status = self.__selectSignalSafe(args)
		return (len(status[selectType]) == 1)
	
	
	def __selectSignalSafe(self, args):
		try:
			return select.select(*args)
		except select.error, e:
			errorCode = e.args[0]
			if errorCode == errno.EINTR:
				raise SignalException
			else:
				raise
