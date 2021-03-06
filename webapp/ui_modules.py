#!/usr/bin/python

from __future__ import division

import hashlib
import logging
import operator
import re
import socket
import textile
import tornado.escape
import tornado.locale
import tornado.web
import unicodedata

from tornado.database import Row

import backend
import backend.stasy

class UIModule(tornado.web.UIModule):
	@property
	def accounts(self):
		return self.handler.accounts

	@property
	def advertisements(self):
		return self.handler.advertisements

	@property
	def banners(self):
		return self.handler.banners

	@property
	def memcached(self):
		return self.handler.memcached

	@property
	def releases(self):
		return self.handler.releases

	@property
	def geoip(self):
		return self.handler.geoip

	@property
	def news(self):
		return self.handler.news


class AdvertisementModule(UIModule):
	def render(self, where):
		assert where in ("download-splash",), where

		ad = self.advertisements.get(where)
		if not ad:
			return ""

		# Mark that advert has been shown.
		ad.update_impressions()

		return self.render_string("modules/ads/%s.html" % where, ad=ad)


class MapModule(UIModule):
	def render(self, latitude, longitude):
		return self.render_string("modules/map.html", latitude=latitude, longitude=longitude)


class MenuModule(UIModule):
	def render(self):
		return self.render_string("modules/menu.html")


class MirrorItemModule(UIModule):
	def render(self, item):
		return self.render_string("modules/mirror-item.html", item=item)


class MirrorsTableModule(UIModule):
	def render(self, mirrors, preferred_mirrors=[]):
		return self.render_string("modules/mirrors-table.html",
			mirrors=mirrors, preferred_mirrors=preferred_mirrors)


class NetBootMenuConfigModule(UIModule):
	def render(self, release):
		return self.render_string("netboot/menu-config.cfg", release=release)


class NetBootMenuHeaderModule(UIModule):
	def render(self, title, releases):
		id = unicodedata.normalize("NFKD", unicode(title)).encode("ascii", "ignore")
		id = re.sub(r"[^\w]+", " ", id)
		id = "-".join(id.lower().strip().split())

		return self.render_string("netboot/menu-header.cfg", id=id,
			title=title, releases=releases)


class NetBootMenuSeparatorModule(UIModule):
	def render(self):
		return self.render_string("netboot/menu-separator.cfg")


class NewsItemModule(UIModule):
	def get_author(self, author):
		# Get name of author
		author = self.accounts.find(author)
		if author:
			return author.cn
		else:
			_ = self.locale.translate
			return _("Unknown author")

	def render(self, item, uncut=True, announcement=False, show_heading=True):
		# Get author
		item.author = self.get_author(item.author_id)

		if not uncut and len(item.text) >= 400:
			item.text = item.text[:400] + "..."

		# Render text
		item.text = textile.textile(item.text)

		return self.render_string("modules/news-item.html", item=item,
			uncut=uncut, announcement=announcement, show_heading=show_heading)


class NewsLineModule(UIModule):
	def render(self, item):
		return self.render_string("modules/news-line.html", item=item)


class NewsTableModule(UIModule):
	def render(self, news):
		return self.render_string("modules/news-table.html", news=news)


class NewsYearNavigationModule(UIModule):
	def render(self, active=None):
		try:
			active = int(active)
		except:
			active = None

		return self.render_string("modules/news-year-nav.html",
			active=active, years=self.news.years)


class SidebarItemModule(UIModule):
	def render(self):
		return self.render_string("modules/sidebar-item.html")


class SidebarReleaseModule(UIModule):
	def render(self):
		return self.render_string("modules/sidebar-release.html",
			latest=self.releases.get_latest())


class ReleaseItemModule(UIModule):
	def render(self, release, latest=False):
		files = {
			"i586" : [],
			"arm"  : [],
		}

		for file in release.files:
			try:
				files[file.arch].append(file)
			except KeyError:
				pass

		return self.render_string("modules/release-item.html",
			release=release, latest=latest, files=files)


class SidebarBannerModule(UIModule):
	def render(self, item=None):
		if not item:
			item = self.banners.get_random()

		return self.render_string("modules/sidebar-banner.html", item=item)


class DownloadButtonModule(UIModule):
	def render(self, release, text="Download now!"):
		best_image = None

		for file in release.files:
			if file.type == "iso":
				best_image = file
				break

		# Show nothing when there was no image found.
		if not best_image:
			return ""

		return self.render_string("modules/download-button.html",
			release=release, image=best_image)


class PlanetEntryModule(UIModule):
	def render(self, entry, show_avatar=True):
		return self.render_string("modules/planet-entry.html",
			entry=entry, show_avatar=show_avatar)


class TrackerPeerListModule(UIModule):
	def render(self, peers, percentages=False):
		# Guess country code and hostname of the host
		for peer in peers:
			country_code = backend.GeoIP().get_country(peer["ip"])
			peer["country_code"] = country_code or "unknown"

			try:
				peer["hostname"] = socket.gethostbyaddr(peer["ip"])[0]
			except:
				peer["hostname"] = ""

		return self.render_string("modules/tracker-peerlist.html",
			peers=[Row(p) for p in peers], percentages=percentages)


class StasyTableModule(UIModule):
	def _make_percentages(self, items):
		total = sum(items.values())

		for k in items.keys():
			items[k] *= 100
			items[k] /= total

		return items

	def render(self, items, sortby="key", reverse=False, percentage=False, flags=False, locale=False):
		hundred_percent = 0
		for v in items.values():
			hundred_percent += v

		keys = []
		if sortby == "key":
			keys = sorted(items.keys(), reverse=reverse)
		elif sortby == "percentage":
			keys = [k for k,v in sorted(items.items(), key=operator.itemgetter(1))]
			if not reverse:
				keys = reversed(keys)
		else:
			raise Exception, "Unknown sortby parameter was provided"

		if hundred_percent:
			_items = []
			for k in keys:
				if not percentage:
					v = items[k] * 100 / hundred_percent
				else:
					v = items[k] * 100
				_items.append((k, v))
			items = _items

		if items and type(items[0][0]) == type(()) :
			_ = self.locale.translate
			_items = []
			for k, v in items:
				k = _("%s to %s") % k
				_items.append((k, v))
			items = _items

		if locale:
			flags = False
			locales = tornado.locale.LOCALE_NAMES
			_items = []
			for k, v in items:
				if k:
					for code, locale in locales.items():
						if code.startswith(k):
							k = locale["name"].split()[0]
				_items.append((k, v))
			items = _items

		return self.render_string("modules/stasy-table.html", items=items, flags=flags)


class StasyCPUCoreTableModule(StasyTableModule):
	def render(self, items):
		items = self._make_percentages(items)

		items = items.items()
		items.sort()

		return self.render_string("modules/stasy-table.html", items=items,
			flags=None #XXX
		)


class StasyDeviceTableModule(UIModule):
	def render(self, devices):
		groups = {}

		for device in devices:
			if not groups.has_key(device.cls):
				groups[device.cls] = []

			groups[device.cls].append(device)
		
		return self.render_string("modules/stasy-table-devices.html",
			groups=groups.items())


class StasyGeoTableModule(UIModule):
	def render(self, items):
		_ = self.locale.translate

		# Sort all items by value
		items = sorted(items.items(), key=operator.itemgetter(1), reverse=True)

		countries = []
		for code, value in items:
			country = tornado.database.Row({
				"code" : code.lower(),
				"name" : _(self.geoip.get_country_name(code)),
				"value" : value * 100,
			})
			countries.append(country)

		return self.render_string("modules/stasy-table-geo.html", countries=countries)


class WishlistModule(UIModule):
	def render(self, wishes, short=False):
		return self.render_string("wishlist/modules/wishlist.html",
			wishes=wishes, short=short)


class WishModule(UIModule):
	def render(self, wish, short=False):
		progress_bar = "progress-warning"

		if wish.percentage >= 100:
			progress_bar = "progress-success"

		return self.render_string("wishlist/modules/wish.html",
			wish=wish, short=short, progress_bar=progress_bar)


class DonationBoxModule(UIModule):
	def render(self, reason_for_transfer=None):
		if reason_for_transfer:
			reason_for_transfer = "IPFire.org - %s" % reason_for_transfer

		return self.render_string("modules/donation-box.html",
			reason_for_transfer=reason_for_transfer)
