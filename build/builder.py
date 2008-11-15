#!/usr/bin/python
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2008  Michael Tremer & Christian Schmidt                      #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

import os
import sys
import time
import socket
import base64
import shutil
from pysqlite2 import dbapi2 as sqlite

sys.path.append(".")

from constants import config

class Database:
	def __init__(self, path):
		self.db = sqlite.connect(os.path.join(path, config["db_name"]))
		c = self.cursor()
		c.executescript("""
			create table if not exists config(key, value, date);
			create table if not exists durations(duration);
		""")
		c.close()
	
	def __call__(self):
		return self.cursor()
	
	def __del__(self):
		self.commit()
		self.db.close()

	def cursor(self):
		return self.db.cursor()
	
	def commit(self):
		self.db.commit()

class DatabaseConfig:
	def __init__(self, db, key):
		self.db = db
		self.key = key
		self.data = None
		self.date = None

	def get(self):
		if not self.data:
			c = self.db.cursor()
			c.execute("SELECT value FROM %(table)s WHERE key = '%(key)s'" \
						% { "table" : "config",
							"key"   : self.key, })
			try:
				self.data = c.fetchone()[0]
			except TypeError:
				self.data = None
			c.close()
		return self.data
	
	__call__ = get
	
	def time(self):
		if not self.date:
			c = self.db.cursor()
			c.execute("SELECT date FROM %(table)s WHERE key = '%(key)s'" \
						% { "table" : "config",
							"key"   : self.key, })
			try:
				self.date = float("%s" % c.fetchone()[0])
			except TypeError:
				self.date = None
			c.close()
		return self.date or float(0)

	def set(self, value):
		#value = (value,)
		c = self.db.cursor()
		if not self.get():
			sql = "INSERT INTO %(table)s(key, value, date) VALUES('%(key)s', '%(value)s', '%(date)s')" \
						% { "table" : "config",
							"key"   : self.key,
							"value" : value,
							"date"  : time.time(), }
			
		else:
			sql = "UPDATE %(table)s SET value='%(value)s', date='%(date)s' WHERE key='%(key)s'" \
						% { "table" : "config",
							"key"   : self.key,
							"value" : value,
							"date"  : time.time(), }
		c.execute(sql)
		c.close()
		self.data = value
		self.db.commit()

class DurationsConfig:
	def __init__(self, db):
		self.db = db
	
	def get(self, sort=0):
		c = self.db.cursor()
		c.execute("SELECT duration FROM durations")
		ret = []
		for value in c.fetchall():
			value = int("%s" % value)
			if value < 900: # 15min
				continue
			ret.append(value)
		c.close()
		if sort: ret.sort()
		return ret
	
	def set(self, value):
		#value = (value,)
		c = self.db.cursor()
		c.execute("INSERT INTO %(table)s(duration) VALUES('%(value)s')" \
					% { "table" : "durations",
						"value" : value, })
		c.close()
		self.db.commit()

	def get_avg(self):
		sum = 0
		durations = self.get()
		if not len(durations):
			return None
		for value in durations:
			sum += value
		avg = sum / len(durations)
		return avg
	
	def get_eta(self, timestamp):
		avg = self.get_avg()
		if not avg:
			return "N/A"
		eta = int(timestamp) + avg
		return time.ctime(eta)

class DistccConfig(DatabaseConfig):
	def __init__(self, db, key, hostname, jobs):
		DatabaseConfig.__init__(self, db, key)
		self.hostname = hostname
		self.jobs = jobs
	
	def __str__(self):
		if not self.ping() or self.get() == "0":
			return ""
		return "%s:%s/%s,lzo   \t# %s" % \
			(socket.gethostbyname(self.hostname), self.get(), self.jobs or "4", self.hostname)

	def ping(self):
		if not self.hostname:
			return False
		return not os.system("ping -c1 -w1 %s &>/dev/null" % self.hostname)

	def version(self):
		return os.popen("distcc --version").readlines()

class FileConfig:
	def __init__(self, path, filetype):
		self.filename = os.path.join(path, config["path"][filetype])

		# Create the file if not existant
		if not os.access(self.filename, os.R_OK):
			f = open(self.filename, "w")
			f.close()

	def get(self):
		ret = []
		try:
			f = open(self.filename)
			ret = f.readlines()
			f.close()
		except:
			pass
		return ret or ["Log is empty."]
	
	__call__ = get
	
	def set(self, lines):
		f = open(self.filename, "w")
		for line in base64.b64decode(lines).split("\n"):
			f.write("%s\n" % line.rstrip("\n"))
		f.close()

class Builder:
	def __init__(self, config, uuid):
		self.uuid = uuid
		self.config = config
		self.path = os.path.join(self.config['path']['db'], self.uuid)
		
		if not os.access(self.path, os.R_OK):
			try:
				os.mkdir(self.path)
			except:
				pass

		self.db = Database(self.path)

		self.hostname = DatabaseConfig(self.db, "hostname")
		self.state    = DatabaseConfig(self.db, "state")
		self.package  = DatabaseConfig(self.db, "package")
		self.target   = DatabaseConfig(self.db, "target")

		self.duration = DurationsConfig(self.db)
		self.jobs     = DatabaseConfig(self.db, "jobs")
		self.distcc   = DistccConfig(self.db, "distcc", self.hostname(), self.jobs())

		self.log      = FileConfig(self.path, "log")
		
		# If host was longer than 3 days in state compiling we set it as idle.
		if self.state() == "compiling" and \
				(time.time() - self.state.time()) > 3*24*60*60:
			self.state.set("idle")
		
		# If host is idle and distcc is not disabled we set it as distcc host.
		if self.state() == "idle" and self.distcc() != "0":
			self.state.set("distcc")

		# If host is longer than 24h in error state we set it as distcc host.
		if self.state() == "error" and \
				(time.time() - self.state.time()) > 24*60*60:
			self.state.set("distcc")
		
		# If host was longer than two weeks in distcc state we set it as unknown.
		if self.state() == "error" and \
				(time.time() - self.state.time()) > 2*7*24*60*60:
			self.state.set("unknown")

		# If host was longer than four weels in distcc state we delete it.
		if self.state() == "unknown" and \
				(time.time() - self.state.time()) > 4*7*24*60*60:
			del self.db
			shutil.rmtree(self.path)

	def set(self, key, value):
		eval("self.%s.set(\"%s\")" % (key, value,))

	def get(self, key):
		return eval("self.%s.get()" % (key,))

def getAllBuilders(age=0):
	builders = []
	for uuid in os.listdir(config["path"]["db"]):
		if uuid == "empty.txt":	continue
		builder = Builder(config, uuid)
		# If there was no activity since "age" days -> continue...
		if age and (time.time() - builder.state.time()) > age*24*60*60:
				continue
		builders.append(builder)
	return builders
