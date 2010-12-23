from __future__ import absolute_import

"""
import sys
print '\n'.join(sys.path)
"""

import socket
import select
import signal
import errno
from sys import exit, stdout
from threading import Thread
from mbl.io import Timeout
from mbl.net import SocketInputStream


def canWrite(stream, timeout = 0):
	print 'call canWrite'
	status = select.select([], [stream.fileno()], [], timeout)
	return len(status[1]) > 0


def canRead(stream, timeout = 0):
	print 'call canRead'
	status = select.select([stream.fileno()], [], [], timeout)
	return len(status[0]) > 0


class Reader(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.setDaemon(True)
	
	
	def run(self):
		while True:
			data = left.recv(1000000)
			print 'data', len(data)


def test():
	#reader = Reader()
	#reader.start()

	#right.send('1234567890')
	#left.settimeout(0.2)
	#data = left.recv(10)
	#print repr(data)
	#right.settimeout(0.1)
	buffer = '0' * 10000
	for i in xrange(100):
		status = canWrite(right)
		print 'can write', status
		#bytes = right.send(buffer, socket.MSG_DONTWAIT)
		bytes = right.send(buffer)
		print 'bytes', bytes
		stdout.flush()
	#stat = right.sendall(buffer)
	#print 'stat', stat


def handler(signum, frame):
	print 'prisel signal', signum, frame


signal.signal(signal.SIGHUP, handler)
left, right = socket.socketpair()
try:
	print 'recv', left.recv(100)
except Exception, e:
	print e
	print e.args
	print errno.errorcode[e.args[0]]
	raise
exit()

left.close()
try:
	left.send('123')
except socket.error, e:
	print errno.errorcode[e.args[0]]
	raise

stream = SocketInputStream(left, Timeout.BLOCK)
print stream.ready(Timeout.BLOCK)
print stream.ready(Timeout.BLOCK)
left.close()
right.close()
