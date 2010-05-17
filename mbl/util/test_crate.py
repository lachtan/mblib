from crate import CrateMeta, Crate


if __name__ == '__main__':
	class MyCrate(Crate):
		__metaclass__ = CrateMeta

		@classmethod
		def conversions(self):
			return {
				'key1': int,
				'key2': str,
			}

	params = {
		'key1': 123,
		'key2': 'ble',
		'ble': 1,
		'unknown': 34
	}
	c = MyCrate(params)
	print c.key1
	print c.key2
	print c['key1']
	print c['key2']

	Crate1 = Crate.createClass('Crate1', {'key11': int, 'key12': float, 'key13': None})
	print 'Crate1.conversions', Crate1.conversions()
	crate1 = Crate1({'key11': '1', 'key12': 1, 'key13': 1})
	print crate1
	for key, value in crate1:
		print 'KEY', key, value

