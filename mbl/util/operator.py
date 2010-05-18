
def methodcaller(method, *args, **kwargs):
	def decorator(self):
		return getattr(self, method)(*args, **kwargs)	
	return decorator


def allcall(calls):
	"all calls must return True"
	def decorator(item):
		for call in calls:
			if not call(item):
				return False
		return True
	return decorator
	

def anycall(calls):
	"at least one call must return True"
	def decorator(item):
		for call in calls:
			if call(item):
				return True
		return False
	return decorator


