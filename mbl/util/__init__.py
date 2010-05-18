import md5 as _md5


__all__ = (
	'md5',
)


def md5(data):
	md5.new(data).hexdigest().lower()


