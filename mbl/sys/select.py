from __future__ import absolute_import
import select
import errno
from time import time
from mbl.io import Timeout


class SignalException(IOError):
	pass


class SimpleSelect(object):
	__READ = 0
	__WRITE = 1
	
	
	def __init__(self, stream):
		self.__stream = stream
	
	
	def readReady(self, timeout):
		return self.__isReady(self.__READ, Timeout(timeout))
	
	
	def writeReady(self, timeout):
		return self.__isReady(self.__WRITE, Timeout(timeout))
		
	
	def __isReady(self, selectType, timeout):
		if timeout.isBlock():
			return self.__isReadyBlock(selectType)
		else:
			return self.__isReadyWaiting(selectType, timeout)
	
	
	def __isReadyBlock(self, selectType):
		while True:
			try:
				return self.__select(selectType, Timeout.BLOCK)
			except SignalException:
				continue
			
	
	def __isReadyWaiting(self, selectType, timeout):
		startTime = self._time()
		_timeout = timeout.timeout()
		while _timeout >= 0:
			try:
				return self.__select(selectType, _timeout)
			except SignalException:
				duration = startTime - self._time()
				_timeout = timeout.timeout() - duration
		return False

	
	def __select(self, selectType, timeout):
		args = [[], [], [], timeout]
		args[selectType].append(self.__stream)
		status = self.__selectSignalSafe(args)
		return (len(status[selectType]) == 1)
	
	
	def __selectSignalSafe(self, args):
		try:
			return self._select(*args)
		except select.error, e:
			if e.errno == errno.EINTR:
				raise SignalException
			else:
				raise
	
	
	def _select(self, *args):
		return select.select(*args)
	
	
	def _time(self):
		return time()

