#!/usr/bin/python

import tornado.web

from handlers_base import *

class NewsIndexHandler(BaseHandler):
	rss_url = "/news.rss"

	"""
		This handler fetches the content that is show on the news portal.
	"""
	def get(self):
		news = self.news.get_latest(limit=5, locale=self.locale)

		return self.render("news.html", news=news)


class NewsYearHandler(NewsIndexHandler):
	def get(self, year):
		news = self.news.get_by_year(year, locale=self.locale)

		return self.render("news-year.html", news=news, selected_year=year)


class NewsItemHandler(BaseHandler):
	rss_url = "/news.rss"

	"""
		This handler displays a whole page full of a single news item.
	"""
	def get(self, slug):
		news = self.news.get_by_slug(slug)
		if not news:
			raise tornado.web.HTTPError(404)

		# Find the name of the author
		author = self.get_account(news.author_id)
		if author:
			news.author = author.cn
		else:
			_ = self.locale.translate
			news.author = _("Unknown author")

		return self.render("news-item.html", item=news)


class NewsAuthorHandler(BaseHandler):
	"""
		This page displays information about the news author.
	"""
	def get(self, author):
		author = self.get_account(author)
		if not author:
			raise tornado.web.HTTPError(404)

		latest_news = self.news.get_latest(author=author.uid,
			locale=self.locale, limit=10)

		self.render("news-author.html",
			author=author, latest_news=latest_news)
