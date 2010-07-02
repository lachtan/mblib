
class Timeout(object):
	BLOCK = -1.0
	NONBLOCK = 0.0
	

	def __init__(def, timeout):
		if timeout is True:
			self.__timeout = Timeout.BLOCK
		elif timeout is False:
			self.__timeout = Timeout.NONBLOCK
		elif timeout is None:
			self.__timeout = Timeout.BLOCK
		else:
			self.__timeout = float(timeout)
	
	
	def __float__(self):
		return self.__timeout
	
	
	def isBlock(self, timeout):
		return timeout < Timeout.NONBLOCK
	
	
	def isWait(self, timeout):
		return timeout > Timeout.NONBLOCK


	def isNonblock(self, timeout):
		return not (self.isBlock() or self.isWait())


