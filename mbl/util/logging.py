"""
wpilib/logging.py
Martin Blazik, WPI Ringier
23.11.2007

ABOUT
Snazil jsem se o maximalne pruhledny a vzdusny model logovani stim, ze za roky
co logovani pouzivame, uz celkem dobre vime co od nej chceme a jak by melo
fungovat. Model vychazi z log4j a ve vyhruznem slova smyslu je odstrasen
modulem logging v zakladnich knihovnach Pythonu, kde je kod totalne neprehledny
osklivy, slozity a tezce menitelny.
Knihovna je thread safe.

Cela konstrukce stoji na nekolika malo zakladnich tridach. Od shora dolu to jsou
Logger    - kontejner uchovavajici logovaci handlery
Handler   - bazova trida pro vsechny logovace (stdout, soubory, rotace nazvu, databze,
            sitove logovani a vlastne cokoliv co nekoho napadne)
Formatter - trida zodpovedna za zformatovani vsech pozadovanych informaci do ciloveho
            textoveho formatu
Event     - trida ktere nese informace ktere se maji zalogovat

Formatter (Layout v log4j)
Je zodpovedny za pripravu textu, ktery se nakonec zaloguje. Deli se na dve casti.
Formatovani casove znacky a formatovani vsech ostatnich informaci. V moudlu je
preddefinovano pomerne velke mnozstvi identifikatoru, ktere lze pouzit. Format
je pak tvoren beznym spusobem formatovani za pouziti slovniku. Napriklad jmeno
aktualniho vlakna do textu pridame jako %(threadName)s
Formatter nemuze myslet na vsechny eventuality, ktere mohou v budoucnu vzniknout,
a tak ma aplikace k dispozici metodu register(key, callback), diky ktere
si muze pridat libovolne dalsi identifikatory a priradit si k nim funkci, ktera
potrebnou informaci poskytne.

Handler (Appender v log4j)
Bazova trida. Handler je zodpovedny za doruceni logu do ciloveho umisteni at je
toto jakekoliv. Zakladni Handler je abstraktni trida, kterou je nutno dedit.
Trida ktera dedi je povinna implementovat metodu action() ktera se vola
pri pozadavku na zalogovani udalosti. Kazdy handler ma svuj formatter, takze
neni nejmensi problem do ruznych ulozist logovat zpravy v ruznem formatu. Ma
tez nastaven svuj level, podle ktereho se rozhoduje, zda informace vubec
zalogovana bude.

Logger
Je kontejner handleru. Kazdy handler ma v ramci kontejneru sve unikatni jmeno.
Zalogovana udalost na loggeru se prvne posoudi s levelem loggeru, zda ma vubec
smysl ji zpracovavat a pokud ano, je distribuovana vsem handlerum. Pokud
ma aplikace zajem, muze si tedy vytvorit libovolne mnzostvi techto kontejneru
a naklada s nimu podle vlastnich predstav. Pro logovani zcela typickych levelu
jsou predpripraveny metody debug(), info(), warning(), error() a critical().

logging
Nabizi sadu globalnich funkci pro zjednoduseni celeho konceptu logovani.
Hlavni aplikace tak muze nastavit potrebne parametry logovani i handlery
a formatovace a vsechny ostatni importovane moduly jiz toto nemusi resit a ani si
predavat logovaci instanci, ale volaji logovaci funkce primo na modulu.


TODO
jednoducha a rychla konfigurace pro bezne typy aplikaci (neco namisto oskliveho baseConfig)
"""

import thread
import threading
import sys
import errno
from random import randint
from time import time, strftime
from datetime import datetime
from math import modf
from os import getpid, fstat
from os.path import dirname, basename, splitext, normcase
from fcntl import flock, LOCK_EX, LOCK_UN


__all__ = (
	'Event',
	'Formatter',
	'Handler',
	'TerminalHandler',
	'FileRotateHandler',
	'Logger'
)

_time = time()
_levels = {}
_logger = None
_id = '%06d' % randint(1, 999999)


# ------------------------------------------------------------------------------
# Event
# ------------------------------------------------------------------------------

class Event(dict):
	def __init__(self, level, message):
		super(dict, self).__init__()
		filename, line, function = self.__backtrace()
		self['id'] = _id
		self['time'] = time()
		self['level'] = level
		self['message'] = message
		self['pathname'] = filename
		self['path'] = dirname(filename)
		self['filename'] = basename(filename)
		self['module'] = splitext(self['filename'])[0]
		self['line'] = line
		self['lineno'] = line
		self['funcName'] = function
		self['function'] = function
		self['levelno'] = self['level']
		self['levelname'] = getLevelName(self['level'])
		self['created'] = self['time']
		self['pid'] = getpid()
		self['process'] = getpid()
		self['thread'] = thread.get_ident()
		self['threadName'] = threading.currentThread().getName()


	def __backtrace(self):
		filename = '(unknown file)'
		line = 0
		function = '(unknown function)'
		f = sys._getframe(1).f_back
		module = f.f_code.co_filename
		while hasattr(f, 'f_code'):
			code = f.f_code
			filename = code.co_filename
			line = f.f_lineno
			function = code.co_name
			if filename != module:
				break
			f = f.f_back
		return normcase(filename), line, function


# ------------------------------------------------------------------------------
# Formatter
# ------------------------------------------------------------------------------

class Formatter(object):
	__defaultStampFormat = '%Y-%m-%d %H:%M:%S.%i'
	__defaultFormat = '%(stamp)s %(levelname)s %(message)s'


	def __init__(self):
		self.setStampFormat(self.__defaultStampFormat)
		self.setFormat(self.__defaultFormat)
		self.__callback = {}


	def setStampFormat(self, stampFormat):
		self.__stampFormat = stampFormat


	def setFormat(self, format):
		self.__messageFormat = format


	def register(self, key, callback):
		self.__callback[key] = callback


	def __stamp(self, now):
		format = self.__stampFormat
		stamp = datetime.fromtimestamp(now)
		mili = '%03d' % int(1000 * modf(now)[0])
		format = format.replace('%i', mili)
		return stamp.strftime(format)


	def format(self, event):
		_event = event.copy()
		for key, callback in self.__callback.items():
			_event[key] = callback()
		stamp = self.__stamp(_event['time'])
		_event['name'] = _event['logger']
		_event['stamp'] = stamp
		_event['asctime'] = stamp
		return self.__messageFormat % _event


# ------------------------------------------------------------------------------
# Handler
# ------------------------------------------------------------------------------

class Handler(object):
	def __init__(self, formatter = None):
		if formatter is None:
			self.setFormatter(Formatter())
		else:
			self.setFormatter(formatter)
		self.setLevel(NOSET)
		self.__lock = threading.RLock()


	def setFormatter(self, formatter):
		self.__formatter = formatter


	def getFormatter(self):
		return self.__formatter


	def setLevel(self, level):
		self.__level = level


	def action(self, message):
		raise NotImplementedError


	def emit(self, event):
		if event['level'] >= self.__level:
			message = self.__formatter.format(event)
			self.__lock.acquire()
			self.action(message)
			self.__lock.release()


# ------------------------------------------------------------------------------
# FileHandler
# ------------------------------------------------------------------------------

class StreamHandler(Handler):
	def __init__(self, stream, formatter = None):
		super(StreamHandler, self).__init__(formatter)
		self.__stream = stream


	def action(self, message):
		while True:
			try:
				self.__stream.write(message + '\n')
				self.__stream.flush()
				break
			except IOError, exc:
				if exc.errno != errno.EINTR:
					raise


# ------------------------------------------------------------------------------
# TerminalHandler
# ------------------------------------------------------------------------------

class TerminalHandler(StreamHandler):
	def __init__(self, formatter = None):
		super(TerminalHandler, self).__init__(sys.stderr, formatter)


# ------------------------------------------------------------------------------
# FileRotateHandler
# ------------------------------------------------------------------------------

class FileRotateHandler(Handler):
	def __init__(self, filename, formatter = None):
		super(FileRotateHandler, self).__init__(formatter)
		self.__format = filename
		self.__filename = None
		self.__file = None


	def open(self):
		filename = strftime(self.__format)
		if filename != self.__filename:
			self.close()
			self.__file = file(filename, 'a')
			self.__filename = filename
			self.__fileno = self.__file.fileno()


	def close(self):
		if self.__file:
			self.__file.close()
		self.__file = None
		self.__filename = None


	def action(self, message):
		self.open()
		fileno = self.__file.fileno()
		flock(fileno, LOCK_EX)
		self.__file.write(message + '\n')
		self.__file.flush()
		flock(fileno, LOCK_UN)


# ------------------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------------------

class Logger(object):
	def __init__(self):
		self.__handlers = {}
		self.setLevel(NOSET)


	def addHandler(self, name, handler):
		if name in self.__handlers:
			raise KeyError('Handler %s je jiz zaregistrovan' % repr(name))
		self.__handlers[name] = handler


	def getHandler(self, name):
		return self.__handlers[name]


	def removeHandler(self, name):
		del self.__handlers[name]


	def setLevel(self, level):
		self.__level = level


	def log(self, level, message):
		if level >= self.__level:
			event = Event(level, message)
			for name, handler in self.__handlers.iteritems():
				_event = event.copy()
				_event['logger'] = name
				handler.emit(_event)


	def debug(self, message):
		self.log(DEBUG, message)


	def info(self, message):
		self.log(INFO, message)


	def warning(self, message):
		self.log(WARNING, message)


	def error(self, message):
		self.log(ERROR, message)


	def critical(self, message):
		self.log(CRITICAL, message)


# ------------------------------------------------------------------------------
# logging
# ------------------------------------------------------------------------------

def addLevelName(name, value):
	global __all__

	_levels[value] = name
	setattr(sys.modules[addLevelName.__module__], name, value)
	__all__ += (name,)


def getLevelName(value):
	return str(_levels.get(value, value))


def addHandler(name, handler):
	_logger.addHandler(name, handler)


def removeHandler(name):
	_logger.removeHandler(name)


def getHandler(name):
	_logger.getHandler(name)


def getFormatter(name):
	return _logger.getHandler(name).getFormatter()


def setLevel(name, level):
	_logger.getHandler(name).setLevel(level)


def setFormat(name, format):
	handler = _logger.getHandler(name)
	formatter = handler.getFormatter()
	formatter.setFormat(format)


def setStampFormat(name, stampFormat):
	handler = _logger.getHandler(name)
	formatter = handler.getFormatter()
	formatter.setStampFormat(stampFormat)


def log(level, message):
	_logger.log(level, message)


def debug(message):
	log(DEBUG, message)


def info(message):
	log(INFO, message)


def warning(message):
	log(WARNING, message)


def error(message):
	log(ERROR, message)


def critical(message):
	log(CRITICAL, message)


def initTerminal():
	formatter = Formatter()
	handler = TerminalHandler(formatter)
	addHandler('root', handler)


def initStream(stream):
	formatter = Formatter()
	handler = StreamHandler(stream, formatter)
	addHandler('root', handler)


def initRotateFile(filename):
	formatter = Formatter()
	handler = FileRotateHandler(filename, formatter)
	addHandler('root', handler)


def initHandler(name, handlerClass, *args, **kwargs):
	handler = handlerClass(*args, **kwargs)
	formatter = getFormatter('root')
	handler.setFormatter(formatter)
	addHandler(name, handler)


if _logger is None:
	addLevelName('CRITICAL', 50)
	addLevelName('ERROR', 40)
	addLevelName('WARNING', 30)
	addLevelName('INFO', 20)
	addLevelName('DEBUG', 10)
	addLevelName('NOSET', 0)
	_logger = Logger()


# EOF

