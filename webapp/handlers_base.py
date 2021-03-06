#!/usr/bin/python

from __future__ import division

import httplib
import datetime
import time
import tornado.locale
import tornado.web

def format_size(b):
	units = ["B", "k", "M", "G"]
	unit_pointer = 0

	while b >= 1024 and unit_pointer < len(units):
		b /= 1024
		unit_pointer += 1

	return "%.1f%s" % (b, units[unit_pointer])


class BaseHandler(tornado.web.RequestHandler):
	rss_url = None

	def get_account(self, uid):
		# Find the name of the author
		return self.accounts.find(uid)

	def get_query_locale(self):
		locale = self.get_argument("locale", None)

		if locale is None:
			return

		return tornado.locale.get(locale)

	def prepare(self):
		locale = self.get_query_locale()
		if locale:
			self.set_cookie("locale", locale.code)

	def get_user_locale(self):
		# The planet is always in english.
		if self.request.host == "planet.ipfire.org":
			return tornado.locale.get("en_US")

		# Get the locale from the query.
		locale = self.get_query_locale()
		if locale:
			return locale

		# Read the locale from the cookies.
		locale = self.get_cookie("locale", None)
		if locale:
			return tornado.locale.get(locale)

		# Otherwise take the browser locale.
		return self.get_browser_locale()

	@property
	def render_args(self):
		today = datetime.date.today()

		return {
			"format_size" : format_size,
			"hostname" : self.request.host,
			"lang" : self.locale.code[:2],
			"rss_url" : self.rss_url,
			"year" : today.year,
		}

	def render(self, *args, **_kwargs):
		kwargs = self.render_args
		kwargs.update(_kwargs)
		tornado.web.RequestHandler.render(self, *args, **kwargs)

	def render_string(self, *args, **_kwargs):
		kwargs = self.render_args
		kwargs.update(_kwargs)
		return tornado.web.RequestHandler.render_string(self, *args, **kwargs)

	def write_error(self, status_code, **kwargs):
		if status_code in (404, 500):
			render_args = ({
				"code"      : status_code,
				"exception" : kwargs.get("exception", None),
				"message"   : httplib.responses[status_code],
			})
			self.render("error-%s.html" % status_code, **render_args)
		else:
			return tornado.web.RequestHandler.write_error(self, status_code, **kwargs)

	def static_url(self, path, static=True):
		ret = tornado.web.RequestHandler.static_url(self, path)

		

		return ret

	def get_remote_ip(self):
		# Fix for clients behind a proxy that sends "X-Forwarded-For".
		ip_addr = self.request.remote_ip.split(", ")

		if ip_addr:
			ip_addr = ip_addr[-1]

		return ip_addr

	def get_remote_location(self):
		if not hasattr(self, "__remote_location"):
			remote_ip = self.get_remote_ip()

			self.__remote_location = self.geoip.get_location(remote_ip)

		return self.__remote_location

	@property
	def backend(self):
		return self.application.backend

	@property
	def db(self):
		return self.backend.db

	@property
	def advertisements(self):
		return self.backend.advertisements

	@property
	def accounts(self):
		return self.backend.accounts

	@property
	def downloads(self):
		return self.backend.downloads

	@property
	def iuse(self):
		return self.backend.iuse

	@property
	def memcached(self):
		return self.backend.memcache

	@property
	def mirrors(self):
		return self.backend.mirrors

	@property
	def netboot(self):
		return self.backend.netboot

	@property
	def news(self):
		return self.backend.news

	@property
	def config(self):
		return self.backend.settings

	@property
	def releases(self):
		return self.backend.releases

	@property
	def geoip(self):
		return self.backend.geoip

	@property
	def stasy(self):
		return self.backend.stasy

	@property
	def tracker(self):
		return self.backend.tracker

	@property
	def planet(self):
		return self.backend.planet

	@property
	def wishlist(self):
		return self.backend.wishlist
