#!/usr/bin/python

import logging
import time
import tornado.ioloop

import webapp.backend as backend

class Daemon(object):
	def __init__(self):
		self._managers = []
		
		self.ioloop.set_blocking_log_threshold(900)

		self.backend = backend.Backend("webapp.conf")

	@property
	def ioloop(self):
		return tornado.ioloop.IOLoop.instance()

	def add(self, manager_cls):
		manager = manager_cls(self)
		self._managers.append(manager)

	def run(self):
		"""
			Main loop.
		"""
		for manager in self._managers:
			manager.pc.start()

		self.ioloop.start()

	def shutdown(self):
		self.ioloop.stop()


class Manager(object):
	def __init__(self, daemon):
		self.daemon = daemon

		self.pc = tornado.ioloop.PeriodicCallback(self, self.timeout * 1000)
		
		logging.info("%s was initialized." % self.__class__.__name__)

		self()

	def __call__(self):
		logging.info("%s main method was called." % self.__class__.__name__)

		self.do()

		# Update callback_time.
		self.pc.callback_time = self.timeout * 1000
		logging.debug("Next call will be in %.2f seconds." % \
			(self.pc.callback_time / 1000))

	@property
	def backend(self):
		return self.daemon.backend

	@property
	def settings(self):
		return self.backend.settings

	@property
	def timeout(self):
		"""
			Return a new callback timeout in seconds.
		"""
		raise NotImplementedError

	def do(self):
		raise NotImplementedError



class MirrorManager(Manager):
	@property
	def mirrors(self):
		return self.backend.mirrors

	@property
	def timeout(self):
		return self.backend.settings.get_int("mirror_check_interval", 3600)

	def do(self):
		# Check status of all mirror servers.
		self.mirrors.check_all()


class ReleaseFilesManager(Manager):
	@property
	def releases(self):
		return self.backend.releases

	@property
	def timeout(self):
		return self.settings.get_int("releasefiles_check_interval", 3600)

	def do(self):
		for release in self.releases._get_all():
			release.scan_files()


if __name__ == "__main__":
	d = Daemon()
	d.add(MirrorManager)
	d.add(ReleaseFilesManager)

	d.run()
