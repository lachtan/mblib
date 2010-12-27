
class TimeoutError(StandardError):
	pass


class Timeout(object):
	BLOCK = None
	NONBLOCK = 0
	
	def __init__(self, timeout):
		if isinstance(timeout, Timeout):
			self.__timeout = timeout.timeout()
			return
		if timeout is None:
			self.__timeout = Timeout.BLOCK
			return
		elif timeout is 0 or timeout is 0.0:
			self.__timeout = Timeout.NONBLOCK
			return
		_timeout = float(timeout)
		if timeout < 0.0:
			self.__timeout = Timeout.BLOCK
		elif _timeout > 0.0:
			self.__timeout = _timeout
		else:
			self.__timeout = Timeout.NONBLOCK
	
	
	def isBlock(self):
		return self.__timeout == Timeout.BLOCK
	
	
	def isNonblock(self):
		return self.__timeout == Timeout.NONBLOCK
	
	
	def isWaiting(self):
		return self.__timeout > 0
	
	
	def timeout(self):
		return self.__timeout
	
	
	def __str__(self):
		if self.__timeout == Timeout.BLOCK:
			return 'Timeout(BLOCK)'
		elif self.__timeout == Timeout.NONBLOCK:
			return 'Timeout(NONBLOCK)'
		else:
			return 'Timeout(%0.6f)' % self.__timeout
	
	
	def __eq__(self, other):
		return self.timeout() == other.timeout()
	
	
	def hash(self):
		return hash(self.__timeout)


