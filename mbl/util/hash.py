import hashlib


def md5(data):
	return _hexdigest(hashlib.md5, data)
	

def sha1(data):
	return _hexdigest(hashlib.sha1, data)


def _hexdigest(hashFunction, data):
	return hashFunction(data).hexdigest().lower()

