#!/usr/bin/env python2.5

"""
wthread.py
Martin Blazik, WPI Ringier
28.4.2008

K behu vyzaduje minimalne python 2.5 a Linux OS.

Pro hodnotu timeout je zavedena konvence
timeout > 0   cekej dany cas
timeout == 0  necekej vubec
timeout < 0   blokujici volani
"""

import thread
from math import modf
from time import time
from collections import deque
from sys import stdout
from ctypes import *
from constants import BLOCK
from constants import NONBLOCK

__all__ = (
	'ThreadError',
	'Mutex',
	'Condition',
	'Lock',
	'Semaphore',
	'Event',
	'Queue'
)

pth = CDLL('libpthread.so.0', RTLD_GLOBAL)

NANO_SEC = 1000000000L
SIZEOF_PTHREAD_MUTEXATTR_T = 4
SIZEOF_PTHREAD_MUTEX_T	 = 40
SIZEOF_PTHREAD_COND_T	  = 48

PTHREAD_MUTEX_NORMAL	 = 0
PTHREAD_MUTEX_RECURSIVE  = 1
PTHREAD_MUTEX_ERRORCHECK = 2

OK		= 0
EPERM	 = 1
EBUSY	 = 16
EINVAL	= 22
EDEADLK   = 35
ETIMEDOUT = 110

errors = {}

pthread_mutexattr_t = c_char * SIZEOF_PTHREAD_MUTEXATTR_T
pthread_mutex_t = c_char * SIZEOF_PTHREAD_MUTEX_T
pthread_cond_t = c_char * SIZEOF_PTHREAD_COND_T

class struct_timespec(Structure):
	_fields_ = [
		('tv_sec', c_long),
		('tv_nsec', c_long)
	]

# int pthread_mutexattr_init(pthread_mutexattr_t *attr)
pth.pthread_mutexattr_init.argtypes = [pthread_mutexattr_t]

# int pthread_mutexattr_settype(pthread_mutexattr_t *attr, int kind)
pth.pthread_mutexattr_settype.argtypes = [pthread_mutexattr_t, c_int]

# int pthread_mutexattr_destroy(pthread_mutexattr_t *attr)
pth.pthread_mutexattr_destroy.argtypes = [pthread_mutexattr_t]

# int pthread_mutex_init(pthread_mutex_t *mutex, const pthread_mutexattr_t *mutexattr)
pth.pthread_mutex_init.argtypes = [pthread_mutex_t, c_void_p]

# int pthread_mutex_lock(pthread_mutex_t *mutex)
pth.pthread_mutex_lock.argtypes = [pthread_mutex_t]

# int pthread_mutex_trylock(pthread_mutex_t *mutex)
pth.pthread_mutex_trylock.argtypes = [pthread_mutex_t]

# int pthread_mutex_unlock(pthread_mutex_t *mutex)
pth.pthread_mutex_unlock.argtypes = [pthread_mutex_t]

# int pthread_mutex_destroy(pthread_mutex_t *mutex)
pth.pthread_mutex_destroy.argtypes = [pthread_mutex_t]

# int pthread_cond_init(pthread_cond_t *cond, pthread_condattr_t *cond_attr)
pth.pthread_cond_init.argtypes = [pthread_cond_t, c_void_p]

# int pthread_cond_signal(pthread_cond_t *cond)
pth.pthread_cond_signal.argtypes = [pthread_cond_t]

# int pthread_cond_broadcast(pthread_cond_t *cond)
pth.pthread_cond_broadcast.argtypes = [pthread_cond_t]

# int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex)
pth.pthread_cond_wait.argtypes = [pthread_cond_t, pthread_mutex_t]

# int pthread_cond_timedwait(pthread_cond_t *cond, pthread_mutex_t *mutex, const struct timespec *abstime)
pth.pthread_cond_timedwait.argtypes = [pthread_cond_t, pthread_mutex_t, POINTER(struct_timespec)]

# int pthread_cond_destroy(pthread_cond_t *cond)
pth.pthread_cond_destroy.argtypes = [pthread_cond_t]


def debug(*args):
	stdout.write(' '.join(map(str, args)) + '\n')
	stdout.flush()


def registerError(name):
	errors[name] = globals()[name]


def errorToMessage(retcode):
	for name, value in errors.iteritems():
		if value == retcode:
			return name
	return str(retcode)


def checkError(retcode, function):
	if retcode != OK:
		raise ThreadError(function, errorToMessage(retcode))


# ------------------------------------------------------------------------------
# ThreadError
# ------------------------------------------------------------------------------

class ThreadError(thread.error):
	pass


# ------------------------------------------------------------------------------
# Mutex
# ------------------------------------------------------------------------------

class Mutex(object):
	def __init__(self):
		super(Mutex, self).__init__()
		self.__mutex = None
		attr = pthread_mutexattr_t()
		retcode = pth.pthread_mutexattr_init(attr)
		checkError(retcode, 'pthread_mutexattr_init')
		retcode = pth.pthread_mutexattr_settype(attr, PTHREAD_MUTEX_ERRORCHECK)
		checkError(retcode, 'pthread_mutexattr_settype')
		self.__mutex = pthread_mutex_t()
		retcode = pth.pthread_mutex_init(self.__mutex, attr)
		checkError(retcode, 'pthread_mutex_init')
		pth.pthread_mutexattr_destroy(attr)


	def __del__(self):
		if pth and self.__mutex:
			retcode = pth.pthread_mutex_destroy(self.__mutex)
			checkError(retcode, 'pthread_mutex_destroy')


	def acquire(self):
		retcode = pth.pthread_mutex_lock(self.__mutex)
		checkError(retcode, 'pthread_mutex_lock')


	def release(self):
		retcode = pth.pthread_mutex_unlock(self.__mutex)
		checkError(retcode, 'pthread_mutex_unlock')


	def getPthreadMutex(self):
		return self.__mutex


# ------------------------------------------------------------------------------
# Condition
# ------------------------------------------------------------------------------

class Condition(object):
	def __init__(self, mutex = None):
		super(Condition, self).__init__()
		self.__cond = None
		if mutex is None:
			self.__mutex = Mutex()
		else:
			self.__mutex = mutex
		self.__cond = pthread_cond_t()
		retcode = pth.pthread_cond_init(self.__cond, None)
		checkError(retcode, 'pthread_cond_init')


	def __del__(self):
		if pth and self.__cond:
			retcode = pth.pthread_cond_destroy(self.__cond)
			checkError(retcode, 'pthread_cond_destroy')


	def acquire(self):
		self.__mutex.acquire()


	def release(self):
		self.__mutex.release()


	def wait(self, timeout = BLOCK):
		if timeout < 0:
			retcode = pth.pthread_cond_wait(self.__cond, self.__mutex.getPthreadMutex())
			function = 'pthread_cond_wait'
		else:
			end = time() + timeout
			timespec = struct_timespec()
			timespec.tv_sec = int(end)
			timespec.tv_nsec = int(NANO_SEC * modf(end)[0])
			retcode = pth.pthread_cond_timedwait(self.__cond, self.__mutex.getPthreadMutex(), pointer(timespec))
			function = 'pthread_cond_timedwait'
		if retcode == ETIMEDOUT:
			return False
		else:
			checkError(retcode, function)
			return True


	def notify(self):
		retcode = pth.pthread_cond_signal(self.__cond)
		checkError(retcode, 'pthread_cond_signal')


	def notifyAll(self):
		retcode = pth.pthread_cond_broadcast(self.__cond)
		checkError(retcode, 'pthread_cond_broadcast')


# ------------------------------------------------------------------------------
# Lock
# ------------------------------------------------------------------------------

class Lock(object):
	def __init__(self):
		super(Lock, self).__init__(self)
		self.__cond = Condition()
		self.__locked = False
		self.__owner = None
		self.__counter = 0


	def acquire(self, timeout = BLOCK):
		self.__cond.acquire()
		me = thread.get_ident()
		if self.__owner == me:
			self.__counter += 1
		else:
			if self.__locked:
				if timeout < 0:
					while self.__locked:
						self.__cond.wait()
				else:
					self.__cond.wait(timeout)
			if not self.__locked:
				self.__locked = True
				self.__owner = me
				self.__counter = 1
		status = (self.__owner == me)
		self.__cond.release()
		return status


	def release(self):
		self.__cond.acquire()
		try:
			if not self.__locked:
				raise ThreadError("can't release not locked lock")
			if self.__owner != thread.get_ident():
				raise ThreadError("caller isn't owner")
			self.__counter -= 1
			if self.__counter == 0:
				self.__locked = False
				self.__owner = None
				self.__cond.notify()
		finally:
			self.__cond.release()


	def locked(self):
		return self.__locked


# ------------------------------------------------------------------------------
# Semaphor
# ------------------------------------------------------------------------------

class Semaphore(object):
	def __init__(self, value = 1):
		super(Semaphore, self).__init__()
		if value < 0:
			raise AttributeError('Semaphore initial value must be >= 0')
		self.__cond = Condition()
		self.__value = int(value)


	def acquire(self, timeout = BLOCK):
		self.__cond.acquire()
		if self.__value == 0:
			self.__cond.wait(timeout)
		if self.__value == 0:
			ret = False
		else:
			self.__value -= 1
			ret = True
		self.__cond.release()
		return ret


	def release(self):
		self.__cond.acquire()
		self.__value += 1
		self.__cond.notify()
		self.__cond.release()


# ------------------------------------------------------------------------------
# Event
# ------------------------------------------------------------------------------

class Event(object):
	def __init__(self):
		super(Event, self).__init__()
		self.__cond = Condition()
		self.__flag = False


	def isSet(self):
		return self.__flag


	def set(self):
		self.__cond.acquire()
		self.__flag = True
		self.__cond.notifyAll()
		self.__cond.release()


	def clear(self):
		self.__cond.acquire()
		self.__flag = False
		self.__cond.release()


	def wait(self, timeout = BLOCK):
		self.__cond.acquire()
		if not self.__flag:
			self.__cond.wait(timeout)
		flag = self.__flag
		self.__cond.release()
		return flag


# ------------------------------------------------------------------------------
# Queue
# ------------------------------------------------------------------------------

class Queue(object):
	def __init__(self, maxsize = 0):
		super(Queue, self).__init__()
		self.__queue = deque()
		self.__maxsize = int(maxsize)
		self.__mutex = Mutex()
		self.__notEmpty = Condition(self.__mutex)
		self.__notFull = Condition(self.__mutex)


	def size(self):
		return len(self.__queue)


	def empty(self):
		return self.size() == 0


	def full(self):
		return self.__maxsize > 0 and self.size() == self.__maxsize


	def put(self, item, timeout = BLOCK):
		if item is None:
			raise AttributeError()
		self.__mutex.acquire()
		ret = True
		if timeout < 0:
			while self.full():
				self.__notFull.wait()
			self.__queue.append(item)
			self.__notEmpty.notify()
		else:
			if self.full():
				self.__notFull.wait(timeout)
			if self.full():
				ret = False
			else:
				self.__queue.append(item)
				self.__notEmpty.notify()
		self.__mutex.release()
		return ret


	def get(self, timeout = BLOCK):
		self.__mutex.acquire()
		if timeout < 0:
			while self.empty():
				self.__notEmpty.wait()
			item = self.__queue.popleft()
			self.__notFull.notify()
		else:
			if self.empty():
				self.__notEmpty.wait(timeout)
			if self.empty():
				item = None
			else:
				item = self.__queue.popleft()
				self.__notFull.notify()
		self.__mutex.release()
		return item


	def join(self):
		# vycka dokud nebudou odebrany vsechny prvky
		pass


# ------------------------------------------------------------------------------
# init
# ------------------------------------------------------------------------------

registerError('EPERM')
registerError('EBUSY')
registerError('EINVAL')
registerError('EDEADLK')
registerError('ETIMEDOUT')

if __name__ == '__main__':
	e = Event()
	e.set()
	r = e.wait()
	assert(r == True)


# EOF

