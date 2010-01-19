#!/usr/bin/python

import httplib
import operator
import os
import simplejson
import sqlite3
import time
import urlparse

import tornado.httpclient
import tornado.locale
import tornado.web

from banners import banners
from helpers import size
from info import info
from news import news
from releases import releases

import builds
import cluster
import menu
import translations
#import uriel

class BaseHandler(tornado.web.RequestHandler):
	def get_user_locale(self):
		uri = self.request.uri.split("/")
		if len(uri) > 1:
			for lang in tornado.locale.get_supported_locales(None):
				if lang[:2] == uri[1]:
					return tornado.locale.get(lang)

	@property
	def render_args(self):
		return {
			"banner"    : banners.get(),
			"lang"      : self.locale.code[:2],
			"langs"     : [l[:2] for l in tornado.locale.get_supported_locales(None)],
			"lang_link" : self.lang_link,
			"link"      : self.link,
			"title"     : "no title given",
			"server"    : self.request.host.replace("ipfire", "<span>ipfire</span>"),
			"uri"       : self.request.uri,
			"year"      : time.strftime("%Y"),
		}

	def render(self, *args, **kwargs):
		nargs = self.render_args
		nargs.update(kwargs)
		nargs["title"] = "%s - %s" % (self.request.host, nargs["title"])
		tornado.web.RequestHandler.render(self, *args, **nargs)

	def link(self, s):
		return "/%s/%s" % (self.locale.code[:2], s)
	
	def lang_link(self, lang):
		return "/%s/%s" % (lang, self.request.uri[4:])
	
	def get_error_html(self, status_code, **kwargs):
		if status_code in (404, 500):
			render_args = self.render_args
			render_args.update({
				"code"      : status_code,
				"exception" : kwargs.get("exception", None),
				"message"   : httplib.responses[status_code],
			})
			return self.render_string("error-%s.html" % status_code, **render_args)
		else:
			return tornado.web.RequestHandler.get_error_html(self, status_code, **kwargs)


class MainHandler(BaseHandler):
	def get(self):
		lang = self.locale.code[:2]
		self.redirect("/%s/index" % (lang))


class DownloadHandler(BaseHandler):
	def get(self):
		self.render("downloads.html", release=releases.latest)


class DownloadAllHandler(BaseHandler):
	def get(self):
		self.render("downloads-all.html", releases=releases)


class DownloadDevelopmentHandler(BaseHandler):
	def get(self):
		self.render("downloads-development.html", releases=releases)


class DownloadTorrentHandler(BaseHandler):
	tracker_url = "http://tracker.ipfire.org:6969/stats?format=txt&mode=tpbs"

	@tornado.web.asynchronous
	def get(self):
		http = tornado.httpclient.AsyncHTTPClient()
		http.fetch(self.tracker_url, callback=self.async_callback(self.on_response))

	def on_response(self, response):
		torrents = releases.torrents
		hashes = {}
		if response.code == 200:
			for line in response.body.split("\n"):
				if not line: continue
				hash, seeds, peers = line.split(":")
				hash.lower()
				hashes[hash] = {
					"peers" : peers,
					"seeds" : seeds,
				}

		self.render("downloads-torrents.html",
			hashes=hashes,
			releases=torrents,
			request_time=response.request_time,
			tracker=urlparse.urlparse(response.request.url).netloc)


class StaticHandler(BaseHandler):
	@property
	def static_path(self):
		return os.path.join(self.application.settings["template_path"], "static")

	@property
	def static_files(self):
		ret = []
		for filename in os.listdir(self.static_path):
			if filename.endswith(".html"):
				ret.append(filename)
		return ret

	def get(self, name=None):
		name = "%s.html" % name

		if not name in self.static_files:
			raise tornado.web.HTTPError(404)

		self.render("static/%s" % name)


class IndexHandler(BaseHandler):
	def get(self):
		self.render("index.html", news=news)


class NewsHandler(BaseHandler):
	def get(self):
		self.render("news.html", news=news)


class BuildHandler(BaseHandler):
	def prepare(self):
		self.builds = {
			"<12h" : [],
			">12h" : [],
			">24h" : [],
		}

		for build in builds.find():
			if (time.time() - float(build.get("date"))) < 12*60:
				self.builds["<12h"].append(build)
			elif (time.time() - float(build.get("date"))) < 24*60:
				self.builds[">12h"].append(build)
			else:
				self.builds[">24h"].append(build)

		for l in self.builds.values():
			l.sort()

	def get(self):
		self.render("builds.html", builds=self.builds)


class UrielBaseHandler(BaseHandler):
	#db = uriel.Database()
	pass

class UrielHandler(UrielBaseHandler):
	def get(self):
		pass


class ApiClusterInfoHandler(BaseHandler):
	def get(self):
		id = self.get_argument("id", "null")

		c = cluster.Cluster(info["cluster"]["hostname"])

		self.write(simplejson.dumps({
			"version": "1.1",
			"id": id,
			"result" : c.json,
			"error" : "null", }))
		self.finish()


class TranslationHandler(BaseHandler):
	def get(self):
		self.render("translations.html", projects=translations.projects)


class SourceHandler(BaseHandler):
	def prepare(self):
		if not hasattr(self, "db"):
			self.db = sqlite3.connect("/srv/www/ipfire.org/source/hashes.db")
			c = self.db.cursor()
			c.execute("CREATE TABLE IF NOT EXISTS hashes(file, sha1)")
			c.close()

	def get(self):
		source_path = "/srv/sources"
		fileobjects = []

		for dir, subdirs, files in os.walk(source_path):
			if not files:
				continue
			for file in files:
				if file in [f["name"] for f in fileobjects]:
					continue

				c = self.db.cursor()
				c.execute("SELECT sha1 FROM hashes WHERE file = '%s'" % file)
				hash = "%s" % c.fetchone()

				if hash == "None":
					hash = "0000000000000000000000000000000000000000"

				fileobjects.append({
					"dir"  : dir[len(source_path)+1:],
					"name" : file,
					"hash" : hash,
					"size" : size(os.path.getsize(os.path.join(source_path, dir, file))),
				})

				c.close()

		fileobjects.sort(key=operator.itemgetter("name"))

		self.render("sources.html", files=fileobjects)
