
def methodcaller(method, *args, **kwargs):
	"""
	narvi tomu instanci a on zavola metodu - prednastavene argumenty
	mozna by to chtelo jeste verzi, kde argumenty prichazeji s volanim
	"""
	def decorator(self):
		return getattr(self, method)(*args, **kwargs)	
	return decorator


def allcall(calls):
	"""
	all calls must return True
	example:
	
	def isInteger(number):
		return type(number) == TypeInteger
	
	def isPositive(number):
		return number >= 0
	
	def isDividableFour(number):
		return (number % 4) == 0
	
	calls = (isInteger, isPositive, isDividableFour)
	filter(allcall(calls), numbers)
	"""
	def decorator(item):
		for call in calls:
			if not call(item):
				return False
		return True
	return decorator
	

def anycall(calls):
	"""
	at least one call must return True
	example:
	
	def isDigit(text):
		return text.isdigit()
	
	def isLetter(text):
		returntext.isalpha()

	calls = (isDigit, isLetter)
	digitOrLetter = filter(anycall(calls), items)
	"""
	def decorator(item):
		for call in calls:
			if call(item):
				return True
		return False
	return decorator


