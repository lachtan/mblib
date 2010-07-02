import re

def split(pattern, text, itemsCount, emptyItem = ''):
	""" split text into itemCount items
	missing items fills with emtyItem """
	if itemsCount < 1:
		raise AttributeError('itemsCount must be greater or equal 1 (%d)' % itemsCount)
	array = re.split(pattern, text, itemsCount - 1)
	if len(array) < itemsCount:
		array += [emptyItem] * (itemsCount - len(array))
	return array


