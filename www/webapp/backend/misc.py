#!/usr/bin/python

class Singleton(type):
	"""
		A class for using the singleton pattern
	"""

	def __init__(cls, name, bases, dict):
		super(Singleton, cls).__init__(name, bases, dict)
		cls.instance = None
 
	def __call__(cls, *args, **kw):
		if cls.instance is None:
			cls.instance = super(Singleton, cls).__call__(*args, **kw)
 
		return cls.instance