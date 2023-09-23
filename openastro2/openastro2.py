#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This file is part of openastro.org.

    OpenAstro.org is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenAstro.org is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenAstro.org.  If not, see <http://www.gnu.org/licenses/>.
"""

#basics
import math, sys, os.path, socket, gettext, codecs, webbrowser, datetime

# from icalendar import Calendar, Event
import pytz
#from datetime import datetime


#copyfile
from shutil import copyfile

#pysqlite
import sqlite3
sqlite3.dbapi2.register_adapter(str, lambda s:s)

#template processing
from string import Template

#minidom parser
from xml.dom.minidom import parseString

#GTK, cairo to display svg
# from gi import require_version
# require_version('Rsvg', '2.0')
# require_version('Gtk', '3.0')
# from gi.repository import Gtk
# from gi.repository import Gdk, GObject, Rsvg, cairo

import json
from pathlib import Path

#internal openastro modules
sys.path.append("/usr/lib/python3.5/dist-packages") #trying to 'fix' some problems importing openastromod on some distros
sys.path.append("/usr/lib/python3.5/site-packages") #trying to 'fix' some problems importing openastromod on some distros
from openastromod import zonetab, geoname, importfile, dignities, swiss as ephemeris


from skyfield.api import N,S,E,W, wgs84, Topos, load
import pydeck as pdk
import pandas as pd

import ephem

import swisseph as swe

import numpy as np
from skyfield import api, framelib
from skyfield.positionlib import Apparent
from skyfield.api import utc

# from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
import copy

#debug
LOCAL=True
DEBUG=False
VERSION='2.0.0'

#directories
if LOCAL:
	DATADIR=os.path.dirname(__file__)
elif os.path.exists(os.path.join(sys.prefix,'share','openastro.org')):
	DATADIR=os.path.join(sys.prefix,'share','openastro.org')
elif os.path.exists(os.path.join('usr','local','share','openastro.org')):
	DATADIR=os.path.join('usr','local','share','openastro.org')
elif os.path.exists(os.path.join('usr','share','openastro.org')):
	DATADIR=os.path.join('usr','share','openastro.org')
else:
	print("Exiting... can't find data directory")
	sys.exit()

#Translations
LANGUAGES_LABEL={
			"ar":"الْعَرَبيّة",
			"pt_BR":"Português brasileiro",
			"bg":"български език",
			"ca":"català",
			"cs":"čeština",
			"da":"dansk",
			"nl":"Nederlands",
			"eo":"Esperanto",
			"en":"English",
			"fi":"suomi",
			"fr":"Français",
			"de":"Deutsch",
			"el":"ελληνικά",
			"hu":"magyar nyelv",
			"it":"Italiano",
			"ja":"日本",
			"nds":"Plattdüütsch",
			"nb":"Bokmål",
			"pl":"język polski",
			"rom":"rromani ćhib",
			"ru":"Русский",
			"es":"Español",
			"sv":"svenska",
            "uk":"українська мова",
            "zh_TW":"正體字"
		}

TDomain = os.path.join(DATADIR,'locale')
LANGUAGES=list(LANGUAGES_LABEL.keys())
TRANSLATION={}
for i in range(len(LANGUAGES)):
	try:
		TRANSLATION[LANGUAGES[i]] = gettext.translation("openastro",TDomain,languages=[LANGUAGES[i]])
	except IOError as err:
		print("IOError! Invalid languages specified (%s) in %s" %(LANGUAGES[i],TDomain))
		TRANSLATION[LANGUAGES[i]] = gettext.translation("openastro",TDomain,languages=['en'])
		
try:
	TRANSLATION["default"] = gettext.translation("openastro",TDomain)
except IOError as err:
	print("OpenAstro.org has not yet been translated in your language! Could not load translation...")
	TRANSLATION["default"] = gettext.translation("openastro",TDomain,languages=['en'])


class openAstroSettings:

	def __init__(self, settings=[]):
		self.version = VERSION
		dprint("-------------------------------")
		dprint('  OpenAstro2 ' + str(self.version))
		dprint("-------------------------------")
		self.homedir = os.path.expanduser("~")

		# check for astrodir
		self.astrodir = os.path.join(self.homedir, '.openastro.org')
		if os.path.isdir(self.astrodir) == False:
			os.mkdir(self.astrodir)

		# check for tmpdir
		self.tmpdir = os.path.join(self.astrodir, 'tmp')
		if os.path.isdir(self.tmpdir) == False:
			os.mkdir(self.tmpdir)

		# check for swiss local dir
		self.swissLocalDir = os.path.join(self.astrodir, 'swiss_ephemeris')
		if os.path.isdir(self.swissLocalDir) == False:
			os.mkdir(self.swissLocalDir)

		# directories
		if LOCAL:
			DATADIR = os.path.dirname(__file__)
		elif os.path.exists(os.path.join(sys.prefix, 'share', 'openastro.org')):
			DATADIR = os.path.join(sys.prefix, 'share', 'openastro.org')
		elif os.path.exists(os.path.join('usr', 'local', 'share', 'openastro.org')):
			DATADIR = os.path.join('usr', 'local', 'share', 'openastro.org')
		elif os.path.exists(os.path.join('usr', 'share', 'openastro.org')):
			DATADIR = os.path.join('usr', 'share', 'openastro.org')
		else:
			print("Exiting... can't find data directory")
			sys.exit()
		# icons
		icons = os.path.join(DATADIR, 'icons')
		self.iconWindow = os.path.join(icons, 'openastro.svg')
		self.iconAspects = os.path.join(icons, 'aspects')

		# basic files
		self.tempfilename = os.path.join(self.tmpdir, "openAstroChart.svg")
		self.tempfilenameprint = os.path.join(self.tmpdir, "openAstroChartPrint.svg")
		self.tempfilenametable = os.path.join(self.tmpdir, "openAstroChartTable.svg")
		self.tempfilenametableprint = os.path.join(self.tmpdir, "openAstroChartTablePrint.svg")
		self.xml_ui = os.path.join(DATADIR, 'xml/openastro-ui.xml')
		self.xml_svg = os.path.join(DATADIR, 'xml/openastro-svg.xml')
		self.xml_svg2 = os.path.join(DATADIR, 'xml/openastro2-svg.xml')
		self.xml_svg_table = os.path.join(DATADIR, 'xml/openastro-svg-table.xml')

		#------------------------------

		DATADIR = Path(__file__).parent
		json_path = DATADIR / 'settings/settings2.json'
		with open(json_path, 'r', encoding='utf-8') as f:
			settings0 = json.load(f)
		def merge_dicts(dict1, dict2):
			for key, value in dict2.items():
				if isinstance(value, dict):
					# Если значение является словарем, рекурсивно вызываем функцию merge_dicts
					merge_dicts(dict1.get(key, {}), value)
				else:
					# Иначе перезаписываем значение ключа в dict1 значением из dict2
					dict1[key] = value
			return dict1

		self.settings = merge_dicts(settings0, settings)


		self.astrocfg = self.settings["astrocfg"]
		# dprint(self.astrocfg)

		# #install language
		self.setLanguage(self.astrocfg['language'])
		self.lang_label = LANGUAGES_LABEL

		self.settings_svg = self.settings["settings_svg"]
		self.color_codes = self.settings["color_codes"]
		self.settings_planet = self.settings["settings_planet"]
		return
	def setLanguage(self, lang=None):
		if lang == None or lang == "default":
			TRANSLATION["default"].install()
			dprint("installing default language")
		else:
			TRANSLATION[lang].install()
			dprint("installing language (%s)" % (lang))
		return

	def getColors(self):
		out = self.settings["color_codes"]
		return out

	def getLabel(self):
		out = self.settings["label"]
		return out

	def getSettingsPlanet(self):
		dict = self.settings["settings_planet"]
		return dict

	def getSettingsAspect(self):
		dict = self.settings["settings_aspect"]
		return dict


	def checkSwissEphemeris(self, num):
		# 00 = -01-600
		# 06 = 600 - 1200
		# 12 = 1200 - 1800
		# 18 = 1800 - 2400
		# 24 = 2400 - 3000
		seas = 'ftp://ftp.astro.com/pub/swisseph/ephe/seas_12.se1'
		semo = 'ftp://ftp.astro.com/pub/swisseph/ephe/semo_12.se1'
		sepl = 'ftp://ftp.astro.com/pub/swisseph/ephe/sepl_12.se1'


class openAstro:

	@staticmethod
	def event(name="Now", year="", month="", day="", hour="", minute="", second="", timezone=None, location="London", countrycode="", geolat=None, geolon=None, altitude=25):
		event = {}
		if(timezone is None or geolat is None or geolon is None):
			geoname0 = geoname.search(location, countrycode)
			geo = geoname0[0]
		if(year=="" and month=="" and day=="" and hour=="" and minute=="" and second==""):
			now = datetime.datetime.now()
			year: int = now.year
			month: int = now.month
			day: int = now.day
			hour: int = now.hour
			minute: int = now.minute
			second: int = now.second

		event["name"] = name
		event["year"] = year
		event["month"] = month
		event["day"] = day
		event["hour"] = hour
		event["minute"] = minute
		event["second"] = second
		if(timezone is not None ):
			event["timezone"] = timezone
		else:
			# current datetime
			now = datetime.datetime.now()
			# aware datetime object
			dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
			dt = pytz.timezone(geo["timezonestr"]).localize(dt_input)
			# Datetime offset to float in hours
			dh = float(dt.utcoffset().days * 24)
			sh = float(dt.utcoffset().seconds / 3600.0)
			event["timezone"] = dh + sh
		if(timezone is None or geolat is None or geolon is None):
			event["geonameid"] = geo["geonameId"]
			event["location"] = geo["name"]
			event["geolat"] = geo["lat"]
			event["geolon"] = geo["lng"]
			event["countrycode"] = geo["countryCode"]
			event["timezonestr"] = geo["timezonestr"]
		else:
			event["location"] = location
			event["geolat"] = geolat
			event["geolon"] = geolon
		event["altitude"] = altitude
		return event

	@classmethod
	def event_dt_str(self, name="Now", dt_str="", dt_str_format="%Y-%m-%d %H:%M:%S",  timezone=False, location="London", countrycode="", geolat=False, geolon=False, altitude=25):
		# date_time_str = '2022-12-01 10:27:03.929149'
		dt = datetime.datetime.strptime(dt_str, dt_str_format)
		year: int = dt.year
		month: int = dt.month
		day: int = dt.day
		hour: int = dt.hour
		minute: int = dt.minute
		second: int = dt.second
		return self.event(name, year, month, day, hour, minute, second, timezone, location, countrycode, geolat, geolon, altitude)

	@classmethod
	def event_dt(self, name="Now", dt=None,  timezone=False, location="London", countrycode="", geolat=False, geolon=False, altitude=25):
		# date_time_str = '2022-12-01 10:27:03.929149'
		# dt = datetime.datetime.strptime(dt_str, dt_str_format)
		year: int = dt.year
		month: int = dt.month
		day: int = dt.day
		hour: int = dt.hour
		minute: int = dt.minute
		second: int = dt.second
		return self.event(name, year, month, day, hour, minute, second, timezone, location, countrycode, geolat, geolon, altitude)


	def __init__(self, event1, event2=[], type="Radix", settings={}):
		self.settings = openAstroSettings(settings=settings)

		self.event1 = event1
		self.event2 = event2
		self.type = type

		# self.screen_width = 1920
		# self.screen_height = 1080
		self.screen_width = 1024
		self.screen_height = 576

		self.name = self.event1["name"]
		self.charttype = self.type
		self.year = self.event1["year"]
		self.month = self.event1["month"]
		self.day = self.event1["day"]
		self.h = self.event1["hour"]
		self.m = self.event1["minute"]
		self.s = self.event1["second"]
		self.hour=self.decHourJoin(self.event1["hour"],self.event1["minute"], self.event1["second"])
		if ("timezone" in self.event1):
			self.timezone = self.event1["timezone"]
		self.altitude = self.event1["altitude"]
		# self.geonameid = self.event1["geonameid"]
		self.location = self.event1["location"]
		self.geolat = float(self.event1["geolat"])
		self.geolon = float(self.event1["geolon"])
		# self.countrycode = self.event1["countrycode"]
		# self.timezonestr = self.event1["timezonestr"]
		h, m, s = self.decHour(self.hour)
		utc = datetime.datetime(self.year, self.month, self.day, h, m, s)
		tz = datetime.timedelta(seconds=float(self.timezone) * float(3600))
		utc_loc = utc - tz
		# self.e1 =[]
		self.e1_dt_utc = utc_loc

		if (len(self.event2)):
			self.t_name = self.event2["name"]
			# self.t_charttype = self.event2["charttype"]
			self.t_year = self.event2["year"]
			self.t_month = self.event2["month"]
			self.t_day = self.event2["day"]
			self.t_h = self.event2["hour"]
			self.t_m = self.event2["minute"]
			self.t_s = self.event2["second"]
			self.t_hour = self.decHourJoin(self.event2["hour"], self.event2["minute"], self.event2["second"])
			self.t_timezone = self.event2["timezone"]
			self.t_altitude = self.event2["altitude"]
			# self.t_geonameid = self.event2["geonameid"]
			self.t_location = self.event2["location"]
			self.t_geolat = float(self.event2["geolat"])
			self.t_geolon = float(self.event2["geolon"])
			# self.t_countrycode = self.event2["countrycode"]
			# self.t_timezonestr = self.event2["timezonestr"]
			# OpenAstro1 used UTC time in database
			# make global UTC time variables from local
			h, m, s = self.decHour(self.t_hour)
			utc = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			tz = datetime.timedelta(seconds=float(self.t_timezone) * float(3600))
			utc_loc = utc - tz
			self.t_year = utc_loc.year
			self.t_month = utc_loc.month
			self.t_day = utc_loc.day
			self.t_hour = self.decHourJoin(utc_loc.hour, utc_loc.minute, utc_loc.second)
			self.t_utc_year = utc_loc.year
			self.t_utc_month = utc_loc.month
			self.t_utc_day = utc_loc.day
			self.t_utc_h = utc_loc.hour
			self.t_utc_m = utc_loc.minute
			self.t_utc_s = utc_loc.second
			self.dt2_utc = utc_loc


		# #current datetime
		# now = datetime.datetime.now()
		#
		# #aware datetime object
		# dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		# dt = pytz.timezone(self.timezonestr).localize(dt_input)
		
		#naive utc datetime object
		# dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()


		#Default
		# self.name=_("Here and Now")
		# self.charttype=self.label["radix"]
		# self.year=dt_utc.year
		# self.month=dt_utc.month
		# self.day=dt_utc.day
		# self.hour=self.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		# self.timezone=self.offsetToTz(dt.utcoffset())
		# self.altitude=25
		# self.geonameid=None

		# OpenAstro1 used UTC time in database
		self.localToUtc()
		#Make locals
		self.utcToLocal()
		
		#configuration
		#ZOOM 1 = 100%
		self.zoom=1
		# self.type="Radix"


		#12 zodiacs
		self.zodiac = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
		self.zodiac_short = ['Ari','Tau','Gem','Cnc','Leo','Vir','Lib','Sco','Sgr','Cap','Aqr','Psc']
		self.zodiac_color = ['#482900','#6b3d00','#5995e7','#2b4972','#c54100','#2b286f','#69acf1','#ffd237','#ff7200','#863c00','#4f0377','#6cbfff']
		self.zodiac_element = ['fire','earth','air','water','fire','earth','air','water','fire','earth','air','water']

		#get color configuration
		self.colors = self.settings.getColors()
		self.label = self.settings.getLabel()

		return



	def utcToLocal(self):
		#make local time variables from global UTC
		h, m, s = self.decHour(self.hour)
		utc = datetime.datetime(self.year, self.month, self.day, h, m, s)
		tz = datetime.timedelta(seconds=float(self.timezone)*float(3600))
		loc = utc + tz
		# loc = utc - tz
		self.year_loc = loc.year
		self.month_loc = loc.month
		self.day_loc = loc.day
		self.hour_loc = loc.hour
		self.minute_loc = loc.minute
		self.second_loc = loc.second
		#print some info
		dprint('utcToLocal: '+str(utc)+' => '+str(loc)+self.decTzStr(self.timezone))

	def localToUtc(self):
		# OpenAstro1 used UTC time in database
		# make global UTC time variables from local
		h, m, s = self.decHour(self.hour)
		utc = datetime.datetime(self.year, self.month, self.day, h, m, s)
		tz = datetime.timedelta(seconds=float(self.timezone) * float(3600))
		utc_loc = utc - tz
		self.year = utc_loc.year
		self.month = utc_loc.month
		self.day = utc_loc.day
		self.hour = self.decHourJoin(utc_loc.hour, utc_loc.minute, utc_loc.second)
		self.utc_year = utc_loc.year
		self.utc_month = utc_loc.month
		self.utc_day = utc_loc.day
		self.utc_h = utc_loc.hour
		self.utc_m = utc_loc.minute
		self.utc_s = utc_loc.second
		# dprint some info
		dprint('localToUtc: ' + str(utc) + ' => ' + str(utc_loc) + self.decTzStr(self.timezone))

	def localToDirection(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		dprint("localToSolar: from %s to %s" %(self.year,t_year))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		dt_direction = dt_new - dt_original

		dt_dir_seconds = dt_direction.total_seconds()
		gradus_delta = (dt_dir_seconds / solaryearsecs)

		dprint (self.planets_degree_ut)
		mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
		dprint (mdata.planets_degree_ut)
		for i in range(0,43):
			mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
			while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
			while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0

		for i in range(len(self.houses_degree_ut)):
			mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
			if mdata.houses_degree_ut[i] > 360.0:
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
			elif mdata.houses_degree_ut[i] < 0.0:
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0

		# adjust list index 32 and 33
		for i in range(0, 43):
			while (mdata.planets_degree_ut[i] < 0): mdata.planets_degree_ut[i] += 360.0
			while (mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i] -= 360.0

			# get zodiac sign
			for x in range(12):
				deg_low = float(x * 30.0)
				deg_high = float((x + 1.0) * 30.0)
				if mdata.planets_degree_ut[i] >= deg_low:
					if mdata.planets_degree_ut[i] <= deg_high:
						mdata.planets_sign[i] = x
						mdata.planets_degree[i] = mdata.planets_degree_ut[i] - deg_low
						mdata.planets_retrograde[i] = False
		for i in range(12):
			for x in range(len(self.zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if mdata.houses_degree_ut[i] >= deg_low:
					if mdata.houses_degree_ut[i] <= deg_high:
						mdata.houses_sign[i]=x
						mdata.houses_degree[i] = mdata.houses_degree_ut[i] - deg_low

		dprint (self.planets_degree_ut)
		dprint (mdata.planets_degree_ut)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		# self.type = "Transit"

		openAstro.transit=False
		dprint (dt_new)
		return mdata
	def localToDirectionPast(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		dprint("localToSolar: from %s to %s" %(self.year,t_year))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		dt_direction = dt_new - dt_original

		dt_dir_seconds = dt_direction.total_seconds()
		gradus_delta = - (dt_dir_seconds / solaryearsecs) # For past change + to -

		dprint (self.planets_degree_ut)
		mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
		dprint (mdata.planets_degree_ut)
		for i in range(0,43):
			mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
			while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
			while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0

		for i in range(len(self.houses_degree_ut)):
			mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
			if mdata.houses_degree_ut[i] > 360.0:
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
			elif mdata.houses_degree_ut[i] < 0.0:
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0

		# adjust list index 32 and 33
		for i in range(0, 43):
			while (mdata.planets_degree_ut[i] < 0): mdata.planets_degree_ut[i] += 360.0
			while (mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i] -= 360.0

			# get zodiac sign
			for x in range(12):
				deg_low = float(x * 30.0)
				deg_high = float((x + 1.0) * 30.0)
				if mdata.planets_degree_ut[i] >= deg_low:
					if mdata.planets_degree_ut[i] <= deg_high:
						mdata.planets_sign[i] = x
						mdata.planets_degree[i] = mdata.planets_degree_ut[i] - deg_low
						mdata.planets_retrograde[i] = False
		for i in range(12):
			for x in range(len(self.zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if mdata.houses_degree_ut[i] >= deg_low:
					if mdata.houses_degree_ut[i] <= deg_high:
						mdata.houses_sign[i]=x
						mdata.houses_degree[i] = mdata.houses_degree_ut[i] - deg_low

		dprint (self.planets_degree_ut)
		dprint (mdata.planets_degree_ut)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Direction"

		openAstro.transit=False
		dprint (dt_new)
		return mdata

	def localToDirectionRealPast(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# solaryearsecs = 31556925.51 *(1 + 20/360 ) # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# solaryearsecs = 31536000
		dprint("localToSolar: from %s to %s" %(self.year,t_year))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		print (dt_original)
		print (dt_new)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		dt_direction = dt_new - dt_original
		print ("dt_direction =  %s" % (dt_direction) )
		dt_dir_seconds = dt_direction.total_seconds()
		print ("dt_dir_seconds =  %s" % (dt_dir_seconds) )
		dt_direction_degree_year = dt_direction / solaryearsecs * (24*60*60)/360
		print ("dt_direction_degree_year =  %s" % (dt_direction_degree_year) )
		dt_new = dt_original - dt_direction_degree_year

		print (dt_original)
		print (dt_new)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Direction"

		openAstro.transit=False
		dprint (dt_new)
		return
	def localToDirectionRealFuture(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# solaryearsecs = 31556925.51 *(1 + 20/360 ) # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# solaryearsecs = 31536000
		dprint("localToSolar: from %s to %s" %(self.year,t_year))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		print (dt_original)
		print (dt_new)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		dt_direction = dt_new - dt_original
		print ("dt_direction =  %s" % (dt_direction) )
		dt_dir_seconds = dt_direction.total_seconds()
		print ("dt_dir_seconds =  %s" % (dt_dir_seconds) )
		dt_direction_degree_year = dt_direction / solaryearsecs * (24*60*60)/360
		print ("dt_direction_degree_year =  %s" % (dt_direction_degree_year) )
		dt_new = dt_original + dt_direction_degree_year

		print (dt_original)
		print (dt_new)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Direction"

		openAstro.transit=False
		dprint (dt_new)
		return

	def localToProgressionReal(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

		# # solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# solaryearsecs = 27.3215817 * 24 * 60 * 60  # 27,3215817 days
		# dprint("localToSolar: from %s to %s" % (self.year, newyear))
		# h, m, s = self.decHour(self.hour)
		# dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
		# t_h, t_m, t_s = self.decHour(t_hour)
		# # dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		# dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		# dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
		# # mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		# mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
		# 						  self.zodiac, self.settings.astrocfg)
		# dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
		# sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
		# dprint("localToSolar: sundiff %s" % (sundiff))
		# sundelta = (sundiff / 360.0) * solaryearsecs
		# dprint("localToSolar: sundelta %s" % (sundelta))
		# dt_delta = datetime.timedelta(seconds=int(sundelta))
		# dt_new = dt_new + dt_delta

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		dprint("localToSolar: from %s to %s" %(self.year,t_year))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		print (dt_original)
		print (dt_new)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		dt_direction = dt_new - dt_original
		print ("dt_direction =  %s" % (dt_direction) )
		dt_dir_seconds = dt_direction.total_seconds()
		print ("dt_dir_seconds =  %s" % (dt_dir_seconds) )
		dt_direction_degree_year = dt_direction / 360
		print ("dt_direction_degree_year =  %s" % (dt_direction_degree_year) )
		dt_new = dt_original + dt_direction_degree_year

		print (dt_original)
		print (dt_new)

		# dt_dir_seconds = dt_direction.total_seconds()
		# gradus_delta = (dt_dir_seconds / solaryearsecs)
		# # # mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		# # mdata = ephemeris.ephData(t_year,t_month,t_day,t_hour,t_geolon,t_geolat,t_altitude,self.planets,self.zodiac,self.settings.astrocfg)
		# # dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[0]) )
		# # sundiff = self.planets_degree_ut[0] - mdata.planets_degree_ut[0]
		# # dprint("localToSolar: sundiff %s" %(sundiff))
		# # sundelta = ( sundiff / 360.0 ) * solaryearsecs
		# # dprint("localToSolar: sundelta %s" % (sundelta))
		# # dt_delta = datetime.timedelta(seconds=int(sundelta))
		# # dt_delta = datetime.timedelta(seconds=int(sundelta))
		# # dt_new = dt_new + dt_delta
		# # mdata = ephemeris.ephData(dt_new.year,dt_new.month,dt_new.day,self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second),self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		# # dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[0]))
		# # dprint (dt_new)
		# dprint (self.planets_degree_ut)
		# mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
		# 									self.geolat, self.altitude, self.planets, self.zodiac,
		# 									self.settings.astrocfg)
		# dprint (mdata.planets_degree_ut)
		# for i in range(0,43):
		# 	mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
		# 	while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
		# 	while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0
		#
		# for i in range(len(self.houses_degree_ut)):
		# 	mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
		# 	if mdata.houses_degree_ut[i] > 360.0:
		# 		mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
		# 	elif mdata.houses_degree_ut[i] < 0.0:
		# 		mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0
		#
		# # adjust list index 32 and 33
		# for i in range(0, 43):
		# 	while (mdata.planets_degree_ut[i] < 0): mdata.planets_degree_ut[i] += 360.0
		# 	while (mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i] -= 360.0
		#
		# 	# get zodiac sign
		# 	for x in range(12):
		# 		deg_low = float(x * 30.0)
		# 		deg_high = float((x + 1.0) * 30.0)
		# 		if mdata.planets_degree_ut[i] >= deg_low:
		# 			if mdata.planets_degree_ut[i] <= deg_high:
		# 				mdata.planets_sign[i] = x
		# 				mdata.planets_degree[i] = mdata.planets_degree_ut[i] - deg_low
		# 				mdata.planets_retrograde[i] = False
		# for i in range(12):
		# 	for x in range(len(self.zodiac)):
		# 		deg_low=float(x*30)
		# 		deg_high=float((x+1)*30)
		# 		if mdata.houses_degree_ut[i] >= deg_low:
		# 			if mdata.houses_degree_ut[i] <= deg_high:
		# 				mdata.houses_sign[i]=x
		# 				mdata.houses_degree[i] = mdata.houses_degree_ut[i] - deg_low
		#
		# dprint (self.planets_degree_ut)
		# dprint (mdata.planets_degree_ut)
		# #
		# # self.t_year = dt_new.year
		# # self.t_month = dt_new.month
		# # self.t_day = dt_new.day
		# # self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		# # self.t_geolon = self.geolon
		# # self.t_geolat = self.geolat
		# # self.t_altitude = self.altitude
		# # self.type = "Transit"
		# # openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Direction"

		openAstro.transit=False
		dprint (dt_new)
		return


	def localToSolar(self, t_year, t_month, t_day, t_hour, t_geolon,
											t_geolat, t_altitude):
		# OpenAstro1 used UTC time in database
		# # make global UTC time variables from local
		# h, m, s = self.decHour(t_hour)
		# utc = datetime.datetime(t_year, t_month, t_day, h, m, s)
		# tz = datetime.timedelta(seconds=float(t_timezone) * float(3600))
		# utc_loc = utc - tz
		# t_year = utc_loc.year
		# t_month = utc_loc.month
		# t_day = utc_loc.day
		# t_hour = self.decHourJoin(utc_loc.hour, utc_loc.minute, utc_loc.second)

		# newyear = t_year
		solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		# dprint("localToSolar: from %s to %s" %(self.year,newyear))
		h,m,s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		t_h,t_m,t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
		dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
		# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		mdata = ephemeris.ephData(t_year,t_month,t_day,t_hour,t_geolon,t_geolat,t_altitude,self.planets,self.zodiac,self.settings.astrocfg)
		dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[0]) )
		sundiff = -360 + self.planets_degree_ut[0] - mdata.planets_degree_ut[0]
		dprint("localToSolar: sundiff %s" %(sundiff))
		sundelta = ( sundiff / 360.0 ) * solaryearsecs
		dprint("localToSolar: sundelta %s" % (sundelta))
		dt_delta = datetime.timedelta(seconds=int(sundelta))
		dt_new = dt_new + dt_delta
		mdata = ephemeris.ephData(dt_new.year,dt_new.month,dt_new.day,self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second),self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[0]))
		# dprint (dt_new)
		#get precise
		planet_id = 0
		for i in range(20):
			# get precise
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			step = 360 / solaryearsecs
			sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			sundelta = sundiff / step
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.astrocfg)
			# dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
			# print(dt_new)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit=False
		dprint (dt_new)
		return



	def localToNewMoonNext(self, t_year, t_month, t_day, t_hour, t_geolon,
											t_geolat, t_altitude):
		t_h, t_m, t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		# print (dt_new)
		# h,m,s = self.decHour(self.hour)
		# dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		new_moon = ephem.next_new_moon(dt_new)
		# local_dt = next_new_moon.datetime().localize(tz_tashkent)
		# print(next_new_moon.datetime())
		# Преобразуем время новолуния в объект datetime и добавляем информацию о часовом поясе
		# new_moon_local = pytz.utc.localize(ephem.Date(new_moon_utc).datetime()).astimezone(tz)
		new_moon_local = ephem.Date(new_moon).datetime()
		# print(new_moon_local)
		dt_new = new_moon_local
		# print(dt_new)
		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit=False
		# print (dt_new)
		return


	def localToNewMoonPrev(self, t_year, t_month, t_day, t_hour, t_geolon,
											t_geolat, t_altitude):
		t_h, t_m, t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)

		# h,m,s = self.decHour(self.hour)
		# dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
		new_moon = ephem.previous_new_moon(dt_new)
		# local_dt = next_new_moon.datetime().localize(tz_tashkent)
		# print(next_new_moon.datetime())
		# Преобразуем время новолуния в объект datetime и добавляем информацию о часовом поясе
		# new_moon_local = pytz.utc.localize(ephem.Date(new_moon_utc).datetime()).astimezone(tz)
		new_moon_local = ephem.Date(new_moon).datetime()
		# print(new_moon_local)
		dt_new = new_moon_local
		# print(dt_new)
		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit=False
		# dprint (dt_new)
		return

	def localToFullMoonNext(self, t_year, t_month, t_day, t_hour, t_geolon,
											t_geolat, t_altitude):
		t_h, t_m, t_s = self.decHour(t_hour)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		new_moon = ephem.next_full_moon(dt_new)
		new_moon_local = ephem.Date(new_moon).datetime()
		dt_new = new_moon_local
		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit=False
		# print (dt_new)
		return


	def localToFullMoonPrev(self, t_year, t_month, t_day, t_hour, t_geolon,
											t_geolat, t_altitude):
		t_h, t_m, t_s = self.decHour(t_hour)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		new_moon = ephem.previous_full_moon(dt_new)
		new_moon_local = ephem.Date(new_moon).datetime()
		dt_new = new_moon_local
		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit=False
		# dprint (dt_new)
		return


	def localToLunar(self, t_year, t_month, t_day, t_hour, t_geolon,
					 t_geolat, t_altitude):
		planet_id = 1
		newyear = t_year
		# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		solaryearsecs = 27.3215817 * 24 * 60 * 60  # 27,3215817 days
		# dprint("localToSolar: from %s to %s" % (self.year, newyear))
		h, m, s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
		t_h, t_m, t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		# dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
		# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
								  self.zodiac, self.settings.astrocfg)
		dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
		sundiff = -360 + self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
		# dprint("localToSolar: sundiff %s" % (sundiff))
		sundelta = (sundiff / 360.0) * solaryearsecs
		# dprint("localToSolar: sundelta %s" % (sundelta))
		dt_delta = datetime.timedelta(seconds=int(sundelta))
		dt_new = dt_new + dt_delta
		mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,
								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), t_geolon, t_geolat,
								  t_altitude, self.planets, self.zodiac, self.settings.astrocfg)
		# dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_id]))
		# print(dt_new)


		planet_id = 1
		for i in range(20):
			# get precise
			solaryearsecs = 27.3215817 * 24 * 60 * 60  # 27,3215817 days
			step = 360 / solaryearsecs
			sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			sundelta = sundiff / step
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.astrocfg)
			# dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
			# print(dt_new)

		self.e2_dt_utc = dt_new
		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit = False
		# print(dt_new)
		return


	def localToGeoZodiac(self):
		# geo_zodiak_start = -17.5833333
		geo_zodiak_start = self.settings.astrocfg["geo_zodiak_start"]
		planet_id = 0 #Earth = 0 Aries

		planet_names = {1: 'mercuriy', 2: 'venus', 3: 'earth', 4: 'mars', 5: 'jupiter', 6: 'saturn', 7: 'uran',
						8: 'neptun', 9: 'pluton', 10: 'sun', 301: 'moon'}
		data = load('de421.bsp')
		earth = data['earth']
		planet = data[10]
		print (planet_names[10])
		geocentric_planet = planet - earth  # vector from geocenter to sun
		ts = load.timescale()
		t = ts.utc(self.e1_dt_utc.year, self.e1_dt_utc.month, self.e1_dt_utc.day, self.e1_dt_utc.hour, self.e1_dt_utc.minute, self.e1_dt_utc.second)
		planet_subpoint = wgs84.subpoint(geocentric_planet.at(t))  # subpoint method requires a geocentric position
		# print('subpoint latitude: ', planet_subpoint.latitude.degrees)
		# print('subpoint longitude: ', planet_subpoint.longitude.degrees)
		lon_geo = planet_subpoint.longitude.degrees

		lon_astro = self.planets_degree_ut[planet_id]
		lon_geo_zodiak = lon_geo - lon_astro
		# lon_geo_zodiak = lon_geo
		if lon_geo_zodiak<0:
			lon_geo_zodiak = lon_geo_zodiak+360
		if lon_geo_zodiak>360:
			lon_geo_zodiak = lon_geo_zodiak-360
		if lon_geo_zodiak<-360:
			lon_geo_zodiak = lon_geo_zodiak+360

		# print ("lon_geo = ", lon_geo)
		# print ("lon_astro = ", lon_astro)
		# print ("lon_geo_zodiak = ", lon_geo_zodiak)

		dprint("localToGeoZodiac: second Earth %s" % (self.planets_degree_ut[planet_id]))
		# print (self.planets_degree_ut[planet_id])
		degree_diff = lon_geo_zodiak - geo_zodiak_start
		self.t_hour = self.hour + degree_diff/360*24
		if self.t_hour<0:
			self.t_hour = self.t_hour+24
		if self.t_hour>24:
			self.t_hour = self.t_hour-24
		# print ("self.planets_degree_ut[planet_id] = ", self.planets_degree_ut[planet_id])
		# print ("degree_diff = ", degree_diff)
		# print ("self.hour = ", self.hour)
		# print ("self.t_hour = ", self.t_hour)


		self.t_year = self.year
		self.t_month = self.month
		self.t_day = self.day
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.e2_dt_utc = datetime.datetime(self.t_year, self.t_month, self.t_day, self.t_h, self.t_m, self.t_s)
		print ("self.e2_dt_utc = ", self.e2_dt_utc)

		t = ts.utc(self.e2_dt_utc.year, self.e2_dt_utc.month, self.e2_dt_utc.day, self.e2_dt_utc.hour, self.e2_dt_utc.minute, self.e2_dt_utc.second)
		planet_subpoint = wgs84.subpoint(geocentric_planet.at(t))  # subpoint method requires a geocentric position
		# print('subpoint latitude: ', planet_subpoint.latitude.degrees)
		# print('subpoint longitude: ', planet_subpoint.longitude.degrees)
		lon_geo2 = planet_subpoint.longitude.degrees
		# print ("lon_geo2 = ", lon_geo2)


		self.t_name = self.name
		self.t_location = self.location
		self.t_timezone = self.timezone
		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit = False
		# print(dt_new)
		return



	def localToAscReturn(self, t_year, t_month, t_day, t_hour, t_geolon,
					 t_geolat, t_altitude):
		planet_id = 23 #ASC
		newyear = t_year
		# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		solaryearsecs = 1 * 24 * 60 * 60 / 4 # 27,3215817 days
		# dprint("localToSolar: from %s to %s" % (self.year, newyear))
		h, m, s = self.decHour(self.hour)
		dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
		t_h, t_m, t_s = self.decHour(t_hour)
		# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		# dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
		# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
								  self.zodiac, self.settings.astrocfg)
		dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
		sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
		# dprint("localToSolar: sundiff %s" % (sundiff))
		sundelta = (sundiff / 360.0) * solaryearsecs
		# dprint("localToSolar: sundelta %s" % (sundelta))
		dt_delta = datetime.timedelta(seconds=int(sundelta))
		dt_new = dt_new + dt_delta
		mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,
								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), t_geolon, t_geolat,
								  t_altitude, self.planets, self.zodiac, self.settings.astrocfg)
		# dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_id]))
		# print(dt_new)
		for i in range(100):
			# get precise
			moonyearsecs = 1 * 24 * 60 * 60 /3 # 27,3215817 days
			step = 360 / moonyearsecs
			sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			sundelta = sundiff / step
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.astrocfg)
			# dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
			# print(dt_new)
			# print(sundiff)


		self.t_year = dt_new.year
		self.t_month = dt_new.month
		self.t_day = dt_new.day
		self.t_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		self.t_h, self.t_m, self.t_s = self.decHour(self.t_hour)
		self.e2_dt_utc = dt_new

		self.t_geolon = self.geolon
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit = False
		# print(dt_new)
		return

	def localToEarthReturn(self, t_year, t_month, t_day, t_hour, t_geolon,
					 t_geolat, t_altitude):
		planet_id = 23 #ASC
		# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
		solaryearsecs = 1 * 24 * 60 * 60 / 4 #
		# dprint("localToSolar: from %s to %s" % (self.year, newyear))
		h, m, s = self.decHour(self.hour)
		# dt = datetime.datetime(self.year, self.month, self.day, h, m, s)
		t_h, t_m, t_s = self.decHour(t_hour)
		dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
		t_geolon_new = t_geolon
		# dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
		# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.astrocfg)
		mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
								  self.zodiac, self.settings.astrocfg)
		dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
		sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
		# dprint("localToSolar: sundiff %s" % (sundiff))
		# sundelta = (sundiff / 360.0) * solaryearsecs
		# dprint("localToSolar: sundelta %s" % (sundelta))
		# dt_delta = datetime.timedelta(seconds=int(sundelta))
		t_geolon_new = t_geolon_new + sundiff
		mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon_new, t_geolat, t_altitude, self.planets,
								  self.zodiac, self.settings.astrocfg)
		# print(sundiff)
		# dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_id]))
		# print(dt_new)
		for i in range(100):
			# get precise
			moonyearsecs = 1 * 24 * 60 * 60 /10 # 27,3215817 days
			step = 360 / moonyearsecs
			sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			sundelta = sundiff / 4
			# dt_delta = datetime.timedelta(seconds=int(sundelta))
			# dt_new = dt_new + dt_delta
			t_geolon_new = t_geolon_new + sundelta
			# mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.astrocfg)
			mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon_new, t_geolat, t_altitude, self.planets,
								  self.zodiac, self.settings.astrocfg)
			# dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
			# print(t_geolon_new)
			# print (self.planets_degree_ut[planet_id])
			# print (mdata.planets_degree_ut[planet_id])
			# print(sundiff)


		self.t_year = t_year
		self.t_month = t_month
		self.t_day = t_day
		self.t_hour = t_hour
		self.t_h, self.t_m, self.t_s = self.decHour(t_hour)
		self.e2_dt_utc = dt_new

		self.t_geolon = t_geolon_new
		self.t_geolat = self.geolat
		self.t_altitude = self.altitude
		self.type = "Transit"
		# openAstro.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (openAstro.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
		openAstro.transit = False
		# print(dt_new)
		return


	def localToSProgression(self,dt):
		
		#remove timezone
		dt_utc = dt - datetime.timedelta(seconds=float(self.timezone)*float(3600))
		h,m,s = self.decHour(self.hour)
		dt_new = ephemeris.years_diff(self.year,self.month,self.day,self.hour,
			dt_utc.year,dt_utc.month,dt_utc.day,self.decHourJoin(dt_utc.hour,
			dt_utc.minute,dt_utc.second))
		# print ("localToSProgression")
		# print(dt_new)
		self.sp_year = dt_new.year
		self.sp_month = dt_new.month
		self.sp_day = dt_new.day
		self.sp_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
		self.sp_geolon = self.geolon
		self.sp_geolat = self.geolat
		self.sp_altitude = self.altitude
		self.houses_override = [dt_new.year,dt_new.month,dt_new.day,self.hour]
		h,m,s = self.decHour(self.hour)
		self.e2_dt_utc = datetime.datetime(dt_new.year,dt_new.month,dt_new.day, h, m, s)
		self.e2_dt_utc_as_transit = dt_new
		self.e2_dt_utc_as_sprogression = self.e2_dt_utc

		dprint("localToSProgression: got UTC %s-%s-%s %s:%s:%s"%(
			dt_new.year,dt_new.month,dt_new.day,dt_new.hour,dt_new.minute,dt_new.second))
			
		# self.type = "SProgression"
		self.type = "Transit"
		openAstro.charttype="%s (%s-%02d-%02d %02d:%02d)" % ("SProgression",dt.year,dt.month,dt.day,dt.hour,dt.minute)
		openAstro.transit=False
		return

	def localToSProgressionPast(self, dt):
		#
		# # remove timezone
		# dt_utc = dt - datetime.timedelta(seconds=float(self.timezone) * float(3600))
		# h, m, s = self.decHour(self.hour)
		# dt_new = ephemeris.years_diff(dt_utc.year, dt_utc.month, dt_utc.day, self.decHourJoin(dt_utc.hour, dt_utc.minute, dt_utc.second), self.year, self.month, self.day, self.hour)
		# print ("localToSProgressionPast")
		# print(dt_new)
		# self.sp_year = dt_new.year
		# self.sp_month = dt_new.month
		# self.sp_day = dt_new.day
		# self.sp_hour = self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second)
		# self.sp_geolon = self.geolon
		# self.sp_geolat = self.geolat
		# self.sp_altitude = self.altitude
		# self.houses_override = [dt_new.year, dt_new.month, dt_new.day, self.hour]
		# h, m, s = self.decHour(self.hour)
		# self.e2_dt_utc = datetime.datetime(dt_new.year, dt_new.month, dt_new.day, h, m, s)
		# self.e2_dt_utc_as_transit = dt_new
		# self.e2_dt_utc_as_sprogression = self.e2_dt_utc
		#
		# dprint("localToSProgression: got UTC %s-%s-%s %s:%s:%s" % (
		# 	dt_new.year, dt_new.month, dt_new.day, dt_new.hour, dt_new.minute, dt_new.second))
		#
		# # self.type = "SProgression"
		# self.type = "Transit"
		# openAstro.charttype = "%s (%s-%02d-%02d %02d:%02d)" % (
		# "SProgression", dt.year, dt.month, dt.day, dt.hour, dt.minute)
		# openAstro.transit = False
		return
	def calcAstro( self ):
		# empty element points
		self.fire = 0.0
		self.earth = 0.0
		self.air = 0.0
		self.water = 0.0

		# get database planet settings
		self.planets = self.settings.getSettingsPlanet()

		# get database aspect settings
		self.aspects = self.settings.getSettingsAspect()

		# Combine module data
		if self.type == "Combine":
			# make calculations
			module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			h, m, s = self.decHour(self.t_hour)
			dt_new = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			self.e2_dt_utc = dt_new

		# Direction module data
		elif self.type == "Direction":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_sign = module_data.planets_sign
			self.planets_degree = module_data.planets_degree
			self.planets_degree_ut = module_data.planets_degree_ut
			self.planets_retrograde = module_data.planets_retrograde
			self.houses_degree = module_data.houses_degree
			self.houses_sign = module_data.houses_sign
			self.houses_degree_ut = module_data.houses_degree_ut
			self.lunar_phase = module_data.lunar_phase
			t_module_data = self.localToDirection(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon, self.t_geolat, self.t_altitude)
			# t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
			# 								  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
			# 								  self.settings.astrocfg)
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude

		elif self.type == "DirectionPast":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_sign = module_data.planets_sign
			self.planets_degree = module_data.planets_degree
			self.planets_degree_ut = module_data.planets_degree_ut
			self.planets_retrograde = module_data.planets_retrograde
			self.houses_degree = module_data.houses_degree
			self.houses_sign = module_data.houses_sign
			self.houses_degree_ut = module_data.houses_degree_ut
			self.lunar_phase = module_data.lunar_phase
			self.t_planet_azimuth = module_data.planet_azimuth
			self.t_planet_latitude = module_data.planet_latitude
			self.t_planet_longitude = module_data.planet_longitude
			t_module_data = self.localToDirectionPast(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon, self.t_geolat, self.t_altitude)
			# t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
			# 								  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
			# 								  self.settings.astrocfg)
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude

		# DirectionReal module data
		elif self.type == "DirectionRealPast":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToDirectionRealPast(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)
			# grab transiting module data
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude
		elif self.type == "DirectionRealFuture":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToDirectionRealFuture(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)
			# grab transiting module data
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude
		# Solar module data
		elif self.type == "Solar":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToSolar(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)
		elif self.type == "NewMoonNext":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToNewMoonNext(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)


		elif self.type == "NewMoonPrev":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToNewMoonPrev(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)


		elif self.type == "FullMoonNext":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToFullMoonNext(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)


		elif self.type == "FullMoonPrev":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToFullMoonPrev(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
							  self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)


		# Lunar module data
		elif self.type == "Lunar":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToLunar(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)
		elif self.type == "AscReturn":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToAscReturn(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)

		elif self.type == "EarthReturn":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToEarthReturn(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)

		elif self.type == "GeoZodiac":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToGeoZodiac()
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)


		elif self.type == "SProgression":
			dt	= datetime.datetime(self.t_year, self.t_month, self.t_day, self.t_h, self.t_m, self.t_s)
			print (dt)
			self.localToSProgression(dt)
			# module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
			# 								self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
			# 								self.settings.astrocfg, houses_override=self.houses_override)
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			t_module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
											  self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg, houses_override=self.houses_override)
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude
		elif self.type == "SProgressionPast":
			dt	= datetime.datetime(self.t_year, self.t_month, self.t_day, self.t_h, self.t_m, self.t_s)
			print (dt)
			self.localToSProgressionPast(dt)
			# module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
			# 								self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
			# 								self.settings.astrocfg, houses_override=self.houses_override)
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.astrocfg)
			t_module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
											  self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg, houses_override=self.houses_override)
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth
			self.t_planet_latitude = t_module_data.planet_latitude
			self.t_planet_longitude = t_module_data.planet_longitude

		elif self.type == "Transit" or self.type == "Composite":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.astrocfg)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.astrocfg)
			h, m, s = self.decHour(self.t_hour)
			dt_new = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			self.e2_dt_utc = dt_new
		else:
			# make calculations
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.astrocfg)

		# Transit module data
		if self.type == "Transit" or self.type == "Composite":
			# grab transiting module data
			self.t_planets_sign = t_module_data.planets_sign
			self.t_planets_degree = t_module_data.planets_degree
			self.t_planets_degree_ut = t_module_data.planets_degree_ut
			self.t_planets_retrograde = t_module_data.planets_retrograde
			self.t_houses_degree = t_module_data.houses_degree
			self.t_houses_sign = t_module_data.houses_sign
			self.t_houses_degree_ut = t_module_data.houses_degree_ut
			self.t_planet_azimuth = t_module_data.planet_azimuth

		# grab normal module data
		self.planets_sign = module_data.planets_sign
		self.planets_degree = module_data.planets_degree
		self.planets_degree_ut = module_data.planets_degree_ut
		self.planets_retrograde = module_data.planets_retrograde
		self.houses_degree = module_data.houses_degree
		self.houses_sign = module_data.houses_sign
		self.houses_degree_ut = module_data.houses_degree_ut
		self.lunar_phase = module_data.lunar_phase
		self.planet_longitude = module_data.planet_longitude
		self.planet_latitude = module_data.planet_latitude
		self.planet_hour_angle = module_data.planet_hour_angle
		self.planet_azimuth = module_data.planet_azimuth

		# make composite averages
		if self.type == "Composite":
			# new houses
			asc = self.houses_degree_ut[0]
			t_asc = self.t_houses_degree_ut[0]
			for i in range(12):
				# difference in distances measured from ASC
				diff = self.houses_degree_ut[i] - asc
				if diff < 0:
					diff = diff + 360.0
				t_diff = self.t_houses_degree_ut[i] - t_asc
				if t_diff < 0:
					t_diff = t_diff + 360.0
				newdiff = (diff + t_diff) / 2.0

				# new ascendant
				if asc > t_asc:
					diff = asc - t_asc
					if diff > 180:
						diff = 360.0 - diff
						nasc = asc + (diff / 2.0)
					else:
						nasc = t_asc + (diff / 2.0)
				else:
					diff = t_asc - asc
					if diff > 180:
						diff = 360.0 - diff
						nasc = t_asc + (diff / 2.0)
					else:
						nasc = asc + (diff / 2.0)

				# new house degrees
				self.houses_degree_ut[i] = nasc + newdiff
				if self.houses_degree_ut[i] > 360:
					self.houses_degree_ut[i] = self.houses_degree_ut[i] - 360.0

				# new house sign
				for x in range(len(self.zodiac)):
					deg_low = float(x * 30)
					deg_high = float((x + 1) * 30)
					if self.houses_degree_ut[i] >= deg_low:
						if self.houses_degree_ut[i] <= deg_high:
							self.houses_sign[i] = x
							self.houses_degree[i] = self.houses_degree_ut[i] - deg_low

			# new planets
			for i in range(23):
				# difference in degrees
				p1 = self.planets_degree_ut[i]
				p2 = self.t_planets_degree_ut[i]
				if p1 > p2:
					diff = p1 - p2
					if diff > 180:
						diff = 360.0 - diff
						self.planets_degree_ut[i] = (diff / 2.0) + p1
					else:
						self.planets_degree_ut[i] = (diff / 2.0) + p2
				else:
					diff = p2 - p1
					if diff > 180:
						diff = 360.0 - diff
						self.planets_degree_ut[i] = (diff / 2.0) + p2
					else:
						self.planets_degree_ut[i] = (diff / 2.0) + p1

				if self.planets_degree_ut[i] > 360:
					self.planets_degree_ut[i] = self.planets_degree_ut[i] - 360.0

			# list index 23 is asc, 26 is Mc, 29 is Dsc, 32 is Ic
			self.planets_degree_ut[23] = self.houses_degree_ut[0]
			self.planets_degree_ut[26] = self.houses_degree_ut[3]
			self.planets_degree_ut[29] = self.houses_degree_ut[6]
			self.planets_degree_ut[32] = self.houses_degree_ut[9]

			# new planet signs
			for i in range(27):
				for x in range(len(self.zodiac)):
					deg_low = float(x * 30)
					deg_high = float((x + 1) * 30)
					if self.planets_degree_ut[i] >= deg_low:
						if self.planets_degree_ut[i] <= deg_high:
							self.planets_sign[i] = x
							self.planets_degree[i] = self.planets_degree_ut[i] - deg_low
							self.planets_retrograde[i] = False


	def makePlanetNames(self):
		self.planets_name = []
		for i in range(len(self.settings.settings_planet)):
			self.planets_name.append(self.settings.settings_planet[i]['name'])

	def makeSVG2(self, printing=None):
		self.calcAstro()

		# width and height from screen
		# ratio = float(self.screen_width) / float(self.screen_height)
		# if ratio < 1.3:  # 1280x1024
		# 	wm_off = 0
		# else:  # 1024x768, 800x600, 1280x800, 1680x1050
		# 	wm_off = 0

		# check for printer
		if printing == None:
			svgHeight = self.screen_height
			svgWidth = self.screen_width
			# svgHeight=self.screen_height-wm_off
			# svgWidth=(770.0*svgHeight)/540.0
			# svgWidth=float(self.screen_width)-25.0
			rotate = "0"
			translate = "0"
			# viewbox = '0 0 772.2 546.0'  # 297mm * 2.6 + 210mm * 2.6
			viewbox = '0 0 970.7 546.0'  # 297mm * 2.6 + 210mm * 2.6
		else:
			sizeX = 546.0
			sizeY = 970.7
			svgWidth = printing['width']
			svgHeight = printing['height']
			rotate = "0"
			viewbox = '0 0 970.7 546.0'
			translate = "0"

		# template dictionary
		td = dict()
		r = self.settings.settings_svg["r"]
		if (self.settings.astrocfg['chartview'] == "european"):
			self.c1 = self.settings.settings_svg["c1"]
			self.c2 = self.settings.settings_svg['c2']
			self.c3 = self.settings.settings_svg['c3']
		else:
			self.c1 = 0
			self.c2 = 36
			self.c3 = 120

		# make chart
		# transit
		if self.type == "Transit" or self.type == "Direction":
			td['transitRing'] = self.transitRing(r)
			td['degreeRing'] = self.degreeTransitRing(r)
			# circles
			td['c1'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c1) + '"'
			td['c1style'] = 'fill: %s; stroke: %s;  fill-opacity:0.0; stroke-width: 0px; stroke-opacity:1.0;' % (
			self.colors['paper_1'], self.colors['zodiac_transit_ring_2'])
			td['c2'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c2) + '"'
			td['c2style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-opacity:.4; stroke-width: 0px' % (
			self.colors['paper_1'], self.colors['zodiac_transit_ring_1'])
			td['c3'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c3) + '"'
			td['c3style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px' % (
			self.colors['paper_1'], self.colors['zodiac_transit_ring_0'])
			td['makeAspects'] = self.makeAspectsTransit(r, (r - self.c3))
			# td['makeAspectGrid'] = self.makeAspectTransitGrid(r)
			td['makeAspectGrid'] = self.makeAspectGrid(r)
			td['makePatterns'] = ''
		else:
			td['transitRing'] = ""
			# td['degreeRing'] = self.degreeRing(r)
			td['degreeRing'] = ""
			# circles
			td['c1'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c1) + '"'
			td['c1style'] = 'fill: none; stroke: %s; stroke-width: 0.0px; ' % (self.colors['zodiac_radix_ring_2'])
			td['c2'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c2) + '"'
			td['c2style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-opacity:.3; stroke-width: 0.0px' % (
			self.colors['paper_1'], self.colors['zodiac_radix_ring_1'])
			td['c3'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c3) + '"'
			td['c3style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 0.5px' % (
			self.colors['paper_1'], self.colors['zodiac_radix_ring_0'])
			td['makeAspects'] = self.makeAspects(r, (r - self.c3))
			td['makeAspectGrid'] = self.makeAspectGrid(r)
			td['makePatterns'] = self.makePatterns()

		td['circleX'] = str(self.settings.settings_svg["circleX"])
		td['circleY'] = str(self.settings.settings_svg["circleY"])
		td['svgWidth'] = str(svgWidth)
		td['svgHeight'] = str(svgHeight)
		td['viewbox'] = viewbox
		td['stringTitle'] = self.name
		td['stringName'] = self.charttype
		td['t_stringTitle'] = ""

		if self.type == "Transit" or self.type == "Direction":
			td['stringName'] = self.charttype
			td['t_stringTitle'] = self.t_name

		# bottom left
		siderealmode_chartview = {
			"FAGAN_BRADLEY": _("Fagan Bradley"),
			"LAHIRI": _("Lahiri"),
			"DELUCE": _("Deluce"),
			"RAMAN": _("Ramanb"),
			"USHASHASHI": _("Ushashashi"),
			"KRISHNAMURTI": _("Krishnamurti"),
			"DJWHAL_KHUL": _("Djwhal Khul"),
			"YUKTESHWAR": _("Yukteshwar"),
			"JN_BHASIN": _("Jn Bhasin"),
			"BABYL_KUGLER1": _("Babyl Kugler 1"),
			"BABYL_KUGLER2": _("Babyl Kugler 2"),
			"BABYL_KUGLER3": _("Babyl Kugler 3"),
			"BABYL_HUBER": _("Babyl Huber"),
			"BABYL_ETPSC": _("Babyl Etpsc"),
			"ALDEBARAN_15TAU": _("Aldebaran 15Tau"),
			"HIPPARCHOS": _("Hipparchos"),
			"SASSANIAN": _("Sassanian"),
			"J2000": _("J2000"),
			"J1900": _("J1900"),
			"B1950": _("B1950")
		}

		if self.settings.astrocfg['zodiactype'] == 'sidereal':
			td['bottomLeft1'] = _("Sidereal")
			td['bottomLeft2'] = siderealmode_chartview[self.settings.astrocfg['siderealmode']]
		else:
			td['bottomLeft1'] = _("Tropical")
			td['bottomLeft2'] = '%s: %s (%s) %s (%s)' % (
			_("Lunar Phase"), self.lunar_phase['sun_phase'], _("Sun"), self.lunar_phase['moon_phase'], _("Moon"))

		td['bottomLeft3'] = '%s: %s' % (_("Lunar Phase"), self.dec2deg(self.lunar_phase['degrees']))
		td['bottomLeft4'] = ''

		# lunar phase
		deg = self.lunar_phase['degrees']

		if (deg < 90.0):
			maxr = deg
			if (deg > 80.0): maxr = maxr * maxr
			lfcx = 20.0 + (deg / 90.0) * (maxr + 10.0)
			lfr = 10.0 + (deg / 90.0) * maxr
			lffg, lfbg = self.colors["lunar_phase_0"], self.colors["lunar_phase_1"]

		elif (deg < 180.0):
			maxr = 180.0 - deg
			if (deg < 100.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 90.0) / 90.0 * (maxr + 10.0)) - (maxr + 10.0)
			lfr = 10.0 + maxr - ((deg - 90.0) / 90.0 * maxr)
			lffg, lfbg = self.colors["lunar_phase_1"], self.colors["lunar_phase_0"]

		elif (deg < 270.0):
			maxr = deg - 180.0
			if (deg > 260.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 180.0) / 90.0 * (maxr + 10.0))
			lfr = 10.0 + ((deg - 180.0) / 90.0 * maxr)
			lffg, lfbg = self.colors["lunar_phase_1"], self.colors["lunar_phase_0"]

		elif (deg < 361):
			maxr = 360.0 - deg
			if (deg < 280.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 270.0) / 90.0 * (maxr + 10.0)) - (maxr + 10.0)
			lfr = 10.0 + maxr - ((deg - 270.0) / 90.0 * maxr)
			lffg, lfbg = self.colors["lunar_phase_0"], self.colors["lunar_phase_1"]

		td['lunar_phase_fg'] = lffg
		td['lunar_phase_bg'] = lfbg
		td['lunar_phase_cx'] = '%s' % (lfcx)
		td['lunar_phase_r'] = '%s' % (lfr)
		td['lunar_phase_outline'] = self.colors["lunar_phase_2"]

		# rotation based on latitude
		td['lunar_phase_rotate'] = "%s" % (-90.0 - self.geolat)

		td['stringDateTime'] = str(self.year_loc) + '.%(#1)02d.%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {
			'#1': self.month_loc, '#2': self.day_loc, '#3': self.hour_loc, '#4': self.minute_loc,
			'#5': self.second_loc}
		td['t_stringDateTime'] = ""
		if self.type == "Transit" or self.type == "Direction":
			td['t_stringDateTime'] = str(self.t_year) + '.%(#1)02d.%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {
				'#1': self.t_month, '#2': self.t_day, '#3': self.t_h, '#4': self.t_m,
				'#5': self.t_s}

		# stringlocation
		if len(self.location) > 35:
			split = self.location.split(",")
			if len(split) > 1:
				td['stringLocation'] = split[0] + ", " + split[-1]
				if len(td['stringLocation']) > 35:
					td['stringLocation'] = td['stringLocation'][:35] + "..."
			else:
				td['stringLocation'] = self.location[:35] + "..."
		else:
			td['stringLocation'] = self.location
		td['stringLocation'] = td['stringLocation'] + " " + self.decTzStr(self.timezone)

		td['t_stringLocation'] = ""
		td['t_stringLat'] = ""
		td['t_stringLon'] = ""
		# stringlocation
		if self.type == "Transit" or self.type == "Direction":
			# td['stringLocation'] = td['stringLocation'] + " - " + self.t_location
			td['t_stringLocation'] = self.t_location + " " + self.decTzStr(self.t_timezone)
			# td['t_stringLat'] = "%s: %s" % (self.label['latitude'], self.lat2str(self.t_geolat))
			# td['t_stringLon'] = "%s: %s" % (self.label['longitude'], self.lon2str(self.t_geolon))
			td['t_stringLat'] = "%s" % (self.lat2str(self.t_geolat))
			td['t_stringLon'] = "%s" % (self.lon2str(self.t_geolon))

		# td['stringLat'] = "%s: %s" % (self.label['latitude'], self.lat2str(self.geolat))
		# td['stringLon'] = "%s: %s" % (self.label['longitude'], self.lon2str(self.geolon))
		td['stringLat'] = "%s" % ( self.lat2str(self.geolat))
		td['stringLon'] = "%s" % (self.lon2str(self.geolon))
		postype = {"geo": self.label["apparent_geocentric"], "truegeo": self.label["true_geocentric"],
				   "topo": self.label["topocentric"], "helio": self.label["heliocentric"]}
		# td['stringPosition'] = postype[self.settings.astrocfg['postype']]
		td['stringPosition'] = self.settings.astrocfg['postype']

		# paper_color_X
		td['paper_color_0'] = self.colors["paper_0"]
		td['paper_color_1'] = self.colors["paper_1"]



		for i in range(len(self.planets)):
			# td['planets_color_%s'%(i)]=self.colors["planet_%s"%(i)]
			td['planets_color_%s'%(i)]=self.colors["planet_all"]

		# zodiac_color_X
		for i in range(12):
			td['zodiac_color_%s' % (i)] = self.colors["zodiac_icon_%s" % (i)]

		# orb_color_X
		for i in range(len(self.aspects)):
			# td['orb_color_%s' % (self.aspects[i]['degree'])] = self.colors["aspect_%s" % (self.aspects[i]['degree'])]
			td['orb_color_%s' % (self.aspects[i]['degree'])] = self.aspects[i]['color']

		# config
		td['cfgZoom'] = str(self.zoom)
		td['cfgRotate'] = rotate
		td['cfgTranslate'] = translate

		# functions
		td['makeZodiac'] = self.makeZodiac(r)
		td['makeHouses'] = self.makeHouses(r)
		td['makePlanets'] = self.makePlanets(r)
		td['makeElements'] = self.makeElements(r)
		td['makePlanetGrid'] = self.makePlanetGrid()
		td['makeHousesGrid'] = self.makeHousesGrid()

		self.makePlanetNames()
		if self.type == "Transit" or self.type == "Direction":
			td['makePlanetGrid_t'] = self.makePlanetGrid_t()
			td['makeHousesGrid_t'] = self.makeHousesGrid_t()
		else:
			td['makePlanetGrid_t'] = ""
			td['makeHousesGrid_t'] = ""

		# read template
		# f=open(self.settings.xml_svg)
		f = open(self.settings.xml_svg2)
		template = Template(f.read()).substitute(td)
		f.close()

		# write template
		if printing:
			# f = open(cfg.tempfilenameprint, "w")
			f = open(os.path.join(self.settings.tmpdir, self.name + "-" + self.type + '.svg'), "w")
			dprint("Printing SVG: lat=" + str(self.geolat) + ' lon=' + str(self.geolon) + ' loc=' + self.location)
		else:
			# f = open(self.settings.tempfilename, "w")
			f = open(os.path.join(self.settings.tmpdir, self.name + "-" + self.type + '.svg'), "w")
			dprint("Creating SVG: lat=" + str(self.geolat) + ' lon=' + str(self.geolon) + ' loc=' + self.location)

		f.write(template)
		f.close()

		# #return filename
		# return self.settings.tempfilename
		# return SVG
		return template

	#draw transit ring
	def transitRing( self , r ):
		# out = '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:0.7; stroke: %s; stroke-width: 36px; stroke-opacity: 1.0;"/>' % (r,r,r-18,self.colors['paper_1'] ,self.colors['paper_1'])
		# out += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:0.7; stroke: %s; stroke-width: 1px; stroke-opacity: .6;"/>' % (r,r,r,self.colors['paper_1'] ,self.colors['zodiac_transit_ring_3'])
		# return out
		return
	
	#draw degree ring
	def degreeRing( self , r ):
		out=''
		for i in range(72):
			offset = float(i*5) - self.houses_degree_ut[6]
			if offset < 0:
				offset = offset + 360.0
			elif offset > 360:
				offset = offset - 360.0
			x1 = self.sliceToX( 0 , r-self.c1 , offset ) + self.c1
			y1 = self.sliceToY( 0 , r-self.c1 , offset ) + self.c1
			x2 = self.sliceToX( 0 , r+2-self.c1 , offset ) - 2 + self.c1
			y2 = self.sliceToY( 0 , r+2-self.c1 , offset ) - 2 + self.c1
			out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: 1px; stroke-opacity:.9;"/>\n' % (
				x1,y1,x2,y2,self.colors['paper_0'] )
		return out
		
	def degreeTransitRing( self , r ):
		out=''
		# for i in range(72):
		# 	offset = float(i*5) - self.houses_degree_ut[6]
		# 	if offset < 0:
		# 		offset = offset + 360.0
		# 	elif offset > 360:
		# 		offset = offset - 360.0
		# 	x1 = self.sliceToX( 0 , r , offset )
		# 	y1 = self.sliceToY( 0 , r , offset )
		# 	x2 = self.sliceToX( 0 , r+2 , offset ) - 2
		# 	y2 = self.sliceToY( 0 , r+2 , offset ) - 2
		# 	out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: #F00; stroke-width: 1px; stroke-opacity:.9;"/>\n' % (
		# 		x1,y1,x2,y2 )
		return out
	
	#floating latitude an longitude to string
	def lat2str( self, coord ):
		sign=self.label["north"]
		if coord < 0.0:
			sign=self.label["south"]
			coord = abs(coord)
		deg = int(coord)
		min = int( (float(coord) - deg) * 60 )
		sec = int( round( float( ( (float(coord) - deg) * 60 ) - min) * 60.0 ) )
		return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': min, '#3': sec, '#4': sign}
		# return "%s°%s'%s\" %s" % (deg,min,sec,sign)
		
	def lon2str( self, coord ):
		sign=self.label["east"]
		if coord < 0.0:
			sign=self.label["west"]
			coord = abs(coord)
		deg = int(coord)
		min = int( (float(coord) - deg) * 60 )
		sec = int( round( float( ( (float(coord) - deg) * 60 ) - min) * 60.0 ) )
		return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': min, '#3': sec, '#4': sign}
		# return "%s°%s'%s\" %s" % (deg,min,sec,sign)
	
	#decimal hour to minutes and seconds
	def decHour( self , input ):
		hours=int(input)
		mands=(input-hours)*60.0
		mands=round(mands,5)
		minutes=int(mands)
		seconds=int(round((mands-minutes)*60))
		return [hours,minutes,seconds]
		
	#join hour, minutes, seconds, timezone integere to hour float
	def decHourJoin( self , inH , inM , inS ):
		dh = float(inH)
		dm = float(inM)/60
		ds = float(inS)/3600
		output = dh + dm + ds
		return output

	#Datetime offset to float in hours	
	def offsetToTz( self, dtoffset ):
		dh = float(dtoffset.days * 24)
		sh = float(dtoffset.seconds / 3600.0)
		output = dh + sh
		return output
	
	
	#decimal timezone string
	def decTzStr( self, tz ):
		if tz > 0:
			h = int(tz)
			m = int((float(tz)-float(h))*float(60))
			return " +%(#1)02d:%(#2)02d" % {'#1':h,'#2':m}
		else:
			h = int(tz)
			m = int((float(tz)-float(h))*float(60))/-1
			return "-%(#1)02d:%(#2)02d" % {'#1':h/-1,'#2':m}

	#degree difference
	def degreeDiff( self , a , b ):
		if (self.settings.astrocfg["round_aspects"] == 1):
			a = int(a)
			b = int(b)
		out=float()
		if a > b:
			out=a-b
		if a < b:
			out=b-a
		if out > 180.0:
			out=360.0-out
		return out
	#degree difference
	def degreeDiff2( self , a , b ):
		if (self.settings.astrocfg["round_aspects"] == 1):
			a = int(a)
			b = int(b)
		out=float()
		if a > b:
			out=a-b
		if a < b:
			out=b-a
		if out > 360.0:
			out=360.0-out
		if out < -360.0:
			out=out+360
		return out

	#decimal to degrees (a°b'c")
	def dec2deg( self , dec , type="3"):
		dec=float(dec)
		a=int(dec)
		a_new=(dec-float(a)) * 60.0
		b_rounded = int(round(a_new))
		b=int(a_new)
		c=int(round((a_new-float(b))*60.0))
		if type=="3":
			out = '%(#1)02d&#176;%(#2)02d&#39;%(#3)02d&#34;' % {'#1':a,'#2':b, '#3':c}
		elif type=="2":
			out = '%(#1)02d&#176;%(#2)02d&#39;' % {'#1':a,'#2':b_rounded}
		elif type=="1":
			out = '%(#1)02d&#176;' % {'#1':a}
		elif type == "0":
			out = '%(#1)2d' % {'#1': a}
		return str(out)
	
	#draw svg aspects: ring, aspect ring, degreeA degreeB
	def drawAspect( self , r , ar , degA , degB , color):
			offset = (int(self.houses_degree_ut[6]) / -1) + int(degA)
			x1 = self.sliceToX( 0 , ar , offset ) + (r-ar)
			y1 = self.sliceToY( 0 , ar , offset ) + (r-ar)
			offset = (int(self.houses_degree_ut[6]) / -1) + int(degB)
			x2 = self.sliceToX( 0 , ar , offset ) + (r-ar)
			y2 = self.sliceToY( 0 , ar , offset ) + (r-ar)
			out = '			<line x1="'+str(x1)+'" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="'+str(y2)+'" style="stroke: '+color+'; stroke-width: 1.0; stroke-opacity: .5;"/>\n'
			return out
	
	def sliceToX( self , slice , r, offset):
		plus = (math.pi * offset) / 180
		radial = ((math.pi/6) * slice) + plus
		return r * (math.cos(radial)+1)
	
	def sliceToY( self , slice , r, offset):
		plus = (math.pi * offset) / 180
		radial = ((math.pi/6) * slice) + plus
		return r * ((math.sin(radial)/-1)+1)
	
	def zodiacSlice( self , num , r , style,  type):
		#pie slices
		if self.settings.astrocfg["houses_system"] == "G":
			offset = 360 - self.houses_degree_ut[18]
		else:
			offset = 360 - self.houses_degree_ut[6]
		#check transit
		if self.type == "Transit" or self.type == "Direction":
			dropin=0
		else:
			dropin=self.c1
		slice = '<path d="M' + str(r) + ',' + str(r) + ' L' + str(dropin + self.sliceToX(num,r-dropin,offset)) + ',' + str( dropin + self.sliceToY(num,r-dropin,offset)) + ' A' + str(r-dropin) + ',' + str(r-dropin) + ' 0 0,0 ' + str(dropin + self.sliceToX(num+1,r-dropin,offset)) + ',' + str(dropin + self.sliceToY(num+1,r-dropin,offset)) + ' z" style="' + style + '"/>'
		#symbols
		offset = offset + 15
		#check transit
		if self.type == "Transit" or self.type == "Direction":
			dropin=self.c2/2
		else:
			dropin=self.c2/2
		# sign = '<g transform="translate(-16,-16)"><use x="' + str(dropin + self.sliceToX(num,r-dropin,offset)) + '" y="' + str(dropin + self.sliceToY(num,r-dropin,offset)) + '" xlink:href="#' + type + '" /></g>\n'
		sign_x = dropin + self.sliceToX(num, r - dropin, offset)
		sign_y = dropin + self.sliceToY(num, r - dropin, offset)
		scale = 0.3
		sign = '<g transform="translate(-' + str(16 * scale) + ',-' + str(16 * scale) + ')"><g transform="scale(' + str(
			scale) + ')"><use x="' + str(sign_x * (1 / scale)) + '" y="' + str(
			sign_y * (1 / scale)) + '" xlink:href="#' + type + '" stroke="black" fill="black" /></g></g>\n'
		return slice + '\n' + sign
	
	def makeZodiac( self , r ):
		output = ""
		for i in range(len(self.zodiac)):
			output = output + self.zodiacSlice( i , r , "fill:" + self.colors["zodiac_bg_%s"%(i)] + "; fill-opacity: 0.5;" , self.zodiac[i]) + '\n'
		return output
		
	def makeHouses( self , r ):
		path = ""
		if self.settings.astrocfg["houses_system"] == "G":
			xr = 36
		else:
			xr = 12
		for i in range(xr):
			#check transit
			if self.type == "Transit" or self.type == "Direction":
				dropin=self.c3
				roff=self.c1 - self.settings.settings_svg['roff']
				t_roff=self.c1 - self.settings.settings_svg['t_roff']
			else:
				dropin=self.c3
				roff=self.c1-self.settings.settings_svg['roff']
				
			#offset is negative desc houses_degree_ut[6]
			offset = (int(self.houses_degree_ut[int(xr/2)]) / -1) + int(self.houses_degree_ut[i])
			x1 = self.sliceToX( 0 , (r-dropin) , offset ) + dropin
			y1 = self.sliceToY( 0 , (r-dropin) , offset ) + dropin
			x2 = self.sliceToX( 0 , r-roff , offset ) + roff
			y2 = self.sliceToY( 0 , r-roff , offset ) + roff
			
			if i < (xr-1):		
				text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[(i)], self.houses_degree_ut[i] ) / 1 )
			else:
				# text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[(xr-1)] ) / 2 )
				text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[0] ) / 1 )

			#mc, asc, dsc, ic
			if i == 0:
				linecolor=self.planets[23]['color']
			elif i == 9:
				linecolor=self.planets[26]['color']
			elif i == 6:
				linecolor=self.planets[29]['color']
			elif i == 3:
				linecolor=self.planets[32]['color']
			else:
				linecolor=self.colors['houses_radix_line']
			if self.type == "Transit" or self.type == "Direction":
				linecolor = self.colors['houses_transit_line_1']

			#transit houses lines
			if self.type == "Transit" or self.type == "Direction":
				#degrees for point zero
				zeropoint = 360 - self.houses_degree_ut[6]
				t_offset = zeropoint + self.t_houses_degree_ut[i]
				t_offset = zeropoint + self.t_houses_degree_ut[i]
				if t_offset > 360:
					t_offset = t_offset - 360
				t_x1 = self.sliceToX( 0 , (r-t_roff) , t_offset ) + t_roff
				t_y1 = self.sliceToY( 0 , (r-t_roff) , t_offset ) + t_roff
				t_x2 = self.sliceToX( 0 , r , t_offset )
				t_y2 = self.sliceToY( 0 , r , t_offset )
				if i < 11:		
					# t_text_offset = t_offset + int(self.degreeDiff( self.t_houses_degree_ut[(i+1)], self.t_houses_degree_ut[i] ) / 2 )
					t_text_offset = t_offset
				else:
					t_text_offset = t_offset
				#linecolor
				if i ==  0 or i ==  9 or i ==  6 or i ==  3:
					t_linecolor = self.colors['houses_transit_line_2']
				else:
					t_linecolor = self.colors['houses_transit_line_2']
				# xtext = self.sliceToX( 0 , (r-25) , t_text_offset ) + 25
				# ytext = self.sliceToY( 0 , (r-25) , t_text_offset ) + 25
				# path = path + '<text style="fill: #00f; fill-opacity: .4; font-size: 14px"><tspan x="'+str(xtext-3)+'" y="'+str(ytext+3)+'">'+str(i+1)+'</tspan></text>\n'
				# path = path + '<line x1="'+str(t_x1)+'" y1="'+str(t_y1)+'" x2="'+str(t_x2)+'" y2="'+str(t_y2)+'" style="stroke: '+t_linecolor+'; stroke-width: 2px; stroke-opacity:.3;"/>\n'
				dropin = self.c1 - self.settings.settings_svg['t_roff_deg']
				h_text = str(i + 1)
				xtext = self.sliceToX(
					0, (r - dropin), t_text_offset) + dropin  # was 132
				ytext = self.sliceToY(
					0, (r - dropin), t_text_offset) + dropin  # was 132
				# if i == 0:
				# 	xtext = xtext - 6
				path = path + '<line x1="' + str(t_x1) + '" y1="' + str(t_y1) + '" x2="' + str(t_x2) + '" y2="' + str(t_y2) + '" style="stroke: ' + t_linecolor + '; stroke-width: 1px; stroke-dasharray:0; stroke-opacity:.4;"/>\n'
				path = path + '<text style="fill: ' + t_linecolor + '; fill-opacity: .6; font-size: 9px"><tspan x="' + str(xtext - 3) + '" y="' + str(ytext + 3) + '">' + h_text + '</tspan></text>\n'
				path = path + '<text text-anchor="start" x="' + str(xtext + self.settings.settings_svg["offset_degree_planet_x"]) + '" y="' + str(ytext + self.settings.settings_svg["offset_degree_planet_y"]) + '"  style="fill:' + t_linecolor + '; font-size: 7px;">' + self.dec2deg(self.t_houses_degree[(i)]+1, type="0") + '</text>'

			#if transit			
			if self.type == "Transit" or self.type == "Direction":
				dropin = self.c1 - self.settings.settings_svg['roff_deg']
			elif self.settings.astrocfg["chartview"] == "european":
				dropin = self.c1 - self.settings.settings_svg['roff_deg']
			else:		
				dropin=48
				
			# xtext = self.sliceToX( 0 , (r-dropin) , text_offset ) + dropin #was 132
			# ytext = self.sliceToY( 0 , (r-dropin) , text_offset ) + dropin #was 132
			# path = path + '<line x1="'+str(x1)+'" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="'+str(y2)+'" style="stroke: '+linecolor+'; stroke-width: 2px; stroke-dasharray:0; stroke-opacity:.4;"/>\n'
			# path = path + '<text style="fill: #f00; fill-opacity: .6; font-size: 14px"><tspan x="'+str(xtext-3)+'" y="'+str(ytext+3)+'">'+str(i+1)+'</tspan></text>\n'
			# mc, asc, dsc, ic
			if i == 0:
				# h_text = self.settings.settings_planet[12]['label_short']
				h_text = str(i + 1)
			elif i == 9:
				# h_text = self.settings.settings_planet[13]['label_short']
				h_text = str(i + 1)
			elif i == 6:
				# h_text = self.settings.settings_planet[14]['label_short']
				h_text = str(i + 1)
			elif i == 3:
				# h_text = self.settings.settings_planet[15]['label_short']
				h_text = str(i + 1)
			else:
				h_text = str(i + 1)

			xtext = self.sliceToX(
				0, (r - dropin), text_offset) + dropin  # was 132
			ytext = self.sliceToY(
				0, (r - dropin), text_offset) + dropin  # was 132
			# if i == 0:
			# 	xtext = xtext - 6
			path = path + '<line x1="' + str(x1) + '" y1="' + str(y1) + '" x2="' + str(x2) + '" y2="' + str(y2) + '" style="stroke: ' + linecolor + '; stroke-width: 1px; stroke-dasharray:0; stroke-opacity:.4;"/>\n'
			path = path + '<text style="fill: ' + linecolor + '; fill-opacity: .6; font-size: 9px"><tspan x="' + str(xtext - 3) + '" y="' + str(ytext + 3) + '">' + h_text + '</tspan></text>\n'
			path = path + '<text text-anchor="start" x="' + str(xtext + self.settings.settings_svg["offset_degree_planet_x"]) + '" y="' + str(ytext + self.settings.settings_svg["offset_degree_planet_y"]) + '"  style="fill:' + linecolor + '; font-size: 7px;">' + self.dec2deg(self.houses_degree[(i)]+1, type="0") + '</text>'

		return path
	
	def makePlanets( self , r ):
		
		planets_degut={}

		diff=range(len(self.planets))
		for i in range(len(self.planets)):
			if self.planets[i]['visible'] == 1:
				#list of planets sorted by degree				
				planets_degut[self.planets_degree_ut[i]]=i
			
			#element: get extra points if planet is in own zodiac
			pz = self.planets[i]['zodiac_relation']
			cz = self.planets_sign[i]
			extrapoints = 0
			if pz != -1:
				for e in range(len(pz.split(','))):
					if int(pz.split(',')[e]) == int(cz):
						extrapoints = 10

			#calculate element points for all planets
			# dprint (i)
			# dprint(self.planets_sign[i])
			ele = self.zodiac_element[self.planets_sign[i]]			
			if ele == "fire":
				self.fire = self.fire + self.planets[i]['element_points'] + extrapoints
			elif ele == "earth":
				self.earth = self.earth + self.planets[i]['element_points'] + extrapoints
			elif ele == "air":
				self.air = self.air + self.planets[i]['element_points'] + extrapoints
			elif ele == "water":
				self.water = self.water + self.planets[i]['element_points'] + extrapoints
				
		output = ""	
		# keys = list(planets_degut.keys())
		# keys.sort()
		# switch=0
		#
		# planets_degrouped = {}
		# groups = []
		# planets_by_pos = list(range(len(planets_degut)))
		# planet_drange = 3.4
		# #get groups closely together
		# group_open=False
		# for e in range(len(keys)):
		# 	i=planets_degut[keys[e]]
		# 	#get distances between planets
		# 	if e == 0:
		# 		prev = self.planets_degree_ut[planets_degut[keys[-1]]]
		# 		next = self.planets_degree_ut[planets_degut[keys[1]]]
		# 	elif e == (len(keys)-1):
		# 		prev = self.planets_degree_ut[planets_degut[keys[e-1]]]
		# 		next = self.planets_degree_ut[planets_degut[keys[0]]]
		# 	else:
		# 		prev = self.planets_degree_ut[planets_degut[keys[e-1]]]
		# 		next = self.planets_degree_ut[planets_degut[keys[e+1]]]
		# 	diffa=self.degreeDiff(prev,self.planets_degree_ut[i])
		# 	diffb=self.degreeDiff(next,self.planets_degree_ut[i])
		# 	planets_by_pos[e]=[i,diffa,diffb]
		# 	#print "%s %s %s" % (self.planets[i]['label'],diffa,diffb)
		# 	if (diffb < planet_drange):
		# 		if group_open:
		# 			groups[-1].append([e,diffa,diffb,self.planets[planets_degut[keys[e]]]["label"]])
		# 		else:
		# 			group_open=True
		# 			groups.append([])
		# 			groups[-1].append([e,diffa,diffb,self.planets[planets_degut[keys[e]]]["label"]])
		# 	else:
		# 		if group_open:
		# 			groups[-1].append([e,diffa,diffb,self.planets[planets_degut[keys[e]]]["label"]])
		# 		group_open=False
		#
		# def zero(x): return 0
		# planets_delta = list(map(zero,range(len(self.planets))))
		#
		# # dprint (groups)
		# #print planets_by_pos
		# for a in range(len(groups)):
		# 	#Two grouped planets
		# 	if len(groups[a]) == 2:
		# 		next_to_a = groups[a][0][0]-1
		# 		if groups[a][1][0] == (len(planets_by_pos)-1):
		# 			next_to_b = 0
		# 		else:
		# 			next_to_b = groups[a][1][0]+1
		# 		#if both planets have room
		# 		if (groups[a][0][1] > (2*planet_drange))&(groups[a][1][2] > (2*planet_drange)):
		# 			planets_delta[groups[a][0][0]]=-(planet_drange-groups[a][0][2])/2
		# 			planets_delta[groups[a][1][0]]=+(planet_drange-groups[a][0][2])/2
		# 		#if planet a has room
		# 		elif (groups[a][0][1] > (2*planet_drange)):
		# 			planets_delta[groups[a][0][0]]=-planet_drange
		# 		#if planet b has room
		# 		elif (groups[a][1][2] > (2*planet_drange)):
		# 			planets_delta[groups[a][1][0]]=+planet_drange
		#
		# 		#if planets next to a and b have room move them
		# 		elif (planets_by_pos[next_to_a][1] > (2.4*planet_drange))&(planets_by_pos[next_to_b][2] > (2.4*planet_drange)):
		# 			planets_delta[(next_to_a)]=(groups[a][0][1]-planet_drange*2)
		# 			planets_delta[groups[a][0][0]]=-planet_drange*.5
		# 			planets_delta[next_to_b]=-(groups[a][1][2]-planet_drange*2)
		# 			planets_delta[groups[a][1][0]]=+planet_drange*.5
		#
		# 		#if planet next to a has room move them
		# 		elif (planets_by_pos[next_to_a][1] > (2*planet_drange)):
		# 			planets_delta[(next_to_a)]=(groups[a][0][1]-planet_drange*2.5)
		# 			planets_delta[groups[a][0][0]]=-planet_drange*1.2
		#
		# 		#if planet next to b has room move them
		# 		elif (planets_by_pos[next_to_b][2] > (2*planet_drange)):
		# 			planets_delta[next_to_b]=-(groups[a][1][2]-planet_drange*2.5)
		# 			planets_delta[groups[a][1][0]]=+planet_drange*1.2
		#
		# 	#Three grouped planets or more
		# 	xl=len(groups[a])
		# 	if xl >= 3:
		#
		# 		available = groups[a][0][1]
		# 		for f in range(xl):
		# 			available += groups[a][f][2]
		# 		need = (3*planet_drange)+(1.2*(xl-1)*planet_drange)
		# 		leftover = available - need
		# 		xa=groups[a][0][1]
		# 		xb=groups[a][(xl-1)][2]
		#
		# 		#center
		# 		if (xa > (need*.5)) & (xb > (need*.5)):
		# 			startA = xa - (need*.5)
		# 		#position relative to next planets
		# 		else:
		# 			startA=(leftover/(xa+xb))*xa
		# 			startB=(leftover/(xa+xb))*xb
		#
		# 		if available > need:
		# 			planets_delta[groups[a][0][0]]=startA-groups[a][0][1]+(1.5*planet_drange)
		# 			for f in range(xl-1):
		# 				planets_delta[groups[a][(f+1)][0]]=1.2*planet_drange+planets_delta[groups[a][f][0]]-groups[a][f][2]
		# planets_degut={}
		#
		# diff=range(len(self.planets))
		# for i in range(len(self.planets)):
		# 	if self.planets[i]['visible'] == 1:
		# 		#list of planets sorted by degree
		# 		planets_degut[self.planets_degree_ut[i]]=i
		# keys = list(planets_degut.keys())
		# keys.sort()
		# switch = 0

		planets_delta = self.getPlanetsDelta(self.planets_degree_ut)
		keys = list(planets_degut.keys())
		keys.sort()
		switch = 0
		for e in range(len(keys)):
			i=planets_degut[keys[e]]

			#coordinates			
			if self.type == "Transit" or self.type == "Direction":
				if 22 < i < 27:
					rplanet = self.c2 - (self.c2-self.c3)/2
				elif switch == 1:
					rplanet = self.c2 - (self.c2-self.c3)/2
					switch = 0
				else:
					rplanet = self.c2 - (self.c2-self.c3)/2
					switch = 1				
			else:
				#if 22 < i < 27 it is asc,mc,dsc,ic (angles of chart)
				#put on special line (rplanet is range from outer ring)
				amin,bmin,cmin=0,0,0				
				if self.settings.astrocfg["chartview"] == "european":
					amin=74-30
					bmin=94-30
					cmin=40-30
				
				if 22 < i < 27:
					rplanet = 50-cmin
				elif switch == 1:
					rplanet=84-amin
					switch = 0
				else:
					rplanet=104-bmin
					switch = 1			
				
			# rtext=45
			if self.settings.astrocfg['houses_system'] == "G":
				offset = (int(self.houses_degree_ut[18]) / -1) + int(self.planets_degree_ut[i])
				trueoffset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i])
			else:
				offset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i]+planets_delta[e])
				trueoffset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i])
			planet_x = self.sliceToX( 0 , (r-rplanet) , offset ) + rplanet
			planet_y = self.sliceToY( 0 , (r-rplanet) , offset ) + rplanet


			if self.type == "Transit" or self.type == "Direction":
				1
				scale=0.6
				scale=0.6
				#line1
				x1=self.sliceToX( 0 , (r-self.c3) , trueoffset ) + self.c3
				y1=self.sliceToY( 0 , (r-self.c3) , trueoffset ) + self.c3
				x2=self.sliceToX( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				y2=self.sliceToY( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				# color=self.planets[i]["color"]
				color=self.colors["color_transit_1"]
				# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
				#line2
				x1=self.sliceToX( 0 , (r-rplanet-20) , trueoffset ) + rplanet + 20
				y1=self.sliceToY( 0 , (r-rplanet-20) , trueoffset ) + rplanet + 20
				x2=self.sliceToX( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				y2=self.sliceToY( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:0.5;"/>\n' % (x1,y1,x2,y2,color)

				x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.colors['paper_1'], self.colors['color_transit_1'])

			elif self.settings.astrocfg["chartview"] == "european":
				scale=0.6
				#line1
				x1=self.sliceToX( 0 , (r-self.c3) , trueoffset ) + self.c3
				y1=self.sliceToY( 0 , (r-self.c3) , trueoffset ) + self.c3
				x2=self.sliceToX( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				y2=self.sliceToY( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				# color=self.planets[i]["color"]
				color=self.colors["color_radix"]
				# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
				#line2
				x1=self.sliceToX( 0 , (r-rplanet-20) , trueoffset ) + rplanet + 20
				y1=self.sliceToY( 0 , (r-rplanet-20) , trueoffset ) + rplanet + 20
				x2=self.sliceToX( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				y2=self.sliceToY( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				if (not (23 <= i and i <= 34)):
					output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.5;"/>\n' % (x1,y1,x2,y2,color)
					output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
						x1, y1, 1.5, self.colors['paper_1'], self.colors['color_radix'])
			else:
				scale=1

			if (not (23 <= i and i <= 34)):
				#output planet
				output = output + '<g transform="translate(-'+str(12*scale)+',-'+str(12*scale)+')"><g transform="scale('+str(scale)+')"><use x="' + str(planet_x*(1/scale)) + '" y="' + str(planet_y*(1/scale)) + '" xlink:href="#' + self.planets[i]['name'] + '" /></g></g>\n'

				# if i < (xr-1):
				# 	text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[(i)], self.houses_degree_ut[i] ) / 1 )
				# else:
				# 	# text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[(xr-1)] ) / 2 )
				# 	text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[0] ) / 1 )
				text_offset = offset
				# text_offset = 10
				dropin = rplanet
				xtext = self.sliceToX(0, (r - dropin), text_offset) + dropin  + self.settings.settings_svg["offset_degree_planet_x"]
				ytext = self.sliceToY(0, (r - dropin), text_offset) + dropin  + self.settings.settings_svg["offset_degree_planet_y"]
				output = output + '<text text-anchor="start" x="' + str(xtext + 0) + '" y="' + str(ytext - 0) + '"  style="fill:' + self.colors['paper_0'] + '; font-size: 7px;">' + self.dec2deg(self.planets_degree[(i)]+1, type="0") + '</text>'
				output = output + ''

		#make transit degut and display planets
		if self.type == "Transit" or self.type == "Direction":

			scale = 0.6
			scale = 0.6
			# line1
			x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
			y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
			x2 = self.sliceToX(0, (r - rplanet - 30), trueoffset) + rplanet + 30
			y2 = self.sliceToY(0, (r - rplanet - 30), trueoffset) + rplanet + 30
			# color=self.planets[i]["color"]
			color = self.colors["color_transit_1"]
			# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
			# line2
			x1 = self.sliceToX(0, (r - rplanet - 20), trueoffset) + rplanet + 20
			y1 = self.sliceToY(0, (r - rplanet - 20), trueoffset) + rplanet + 20
			x2 = self.sliceToX(0, (r - rplanet - 10), offset) + rplanet + 10
			y2 = self.sliceToY(0, (r - rplanet - 10), offset) + rplanet + 10
			output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:0.2;"/>\n' % (
			x1, y1, x2, y2, color)

			x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
			y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
			output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
				x1, y1, 1.5, self.colors['paper_1'], self.colors['color_transit_1'])

			group_offset={}
			t_planets_degut={}
			for i in range(len(self.planets)):
				group_offset[i]=0
				if self.planets[i]['visible'] == 1:
					t_planets_degut[self.t_planets_degree_ut[i]]=i
			# t_keys = list(t_planets_degut.keys())
			# t_keys.sort()
			t_planets_delta = self.getPlanetsDelta(self.t_planets_degree_ut)
			t_keys = list(t_planets_degut.keys())
			t_keys.sort()

			#grab closely grouped planets
			# groups=[]
			# in_group=False
			# for e in range(len(t_keys)):
			# 	i_a=t_planets_degut[t_keys[e]]
			# 	if e == (len(t_keys)-1):
			# 		i_b=t_planets_degut[t_keys[0]]
			# 	else:
			# 		i_b=t_planets_degut[t_keys[e+1]]
			#
			# 	a=self.t_planets_degree_ut[i_a]
			# 	b=self.t_planets_degree_ut[i_b]
			# 	diff = self.degreeDiff(a,b)
			# 	if diff <= 2.5:
			# 		if in_group:
			# 			groups[-1].append(i_b)
			# 		else:
			# 			groups.append([i_a])
			# 			groups[-1].append(i_b)
			# 			in_group=True
			# 	else:
			# 		in_group=False
			# #loop groups and set degrees display adjustment
			# for i in range(len(groups)):
			# 	if len(groups[i]) == 2:
			# 		group_offset[groups[i][0]]=-1.0
			# 		group_offset[groups[i][1]]=1.0
			# 	elif len(groups[i]) == 3:
			# 		group_offset[groups[i][0]]=-1.5
			# 		group_offset[groups[i][1]]=0
			# 		group_offset[groups[i][2]]=1.5
			# 	elif len(groups[i]) == 4:
			# 		group_offset[groups[i][0]]=-2.0
			# 		group_offset[groups[i][1]]=-1.0
			# 		group_offset[groups[i][2]]=1.0
			# 		group_offset[groups[i][3]]=2.0
			
			switch=0
			for e in range(len(t_keys)):
				i=t_planets_degut[t_keys[e]]

				if 22 < i < 27:
					rplanet = self.c1 - 15
				elif switch == 1:
					rplanet=self.c1 - 15
					switch = 0
				else:
					rplanet=self.c1 - 15
					switch = 1

				zeropoint = 360 - self.houses_degree_ut[6]
				t_offset = zeropoint + self.t_planets_degree_ut[i]
				# if t_offset > 360:
				# 	t_offset = t_offset - 360
				# planet_x = self.sliceToX( 0 , (r-rplanet) , t_offset ) + rplanet
				# planet_y = self.sliceToY( 0 , (r-rplanet) , t_offset ) + rplanet
				if self.settings.astrocfg['houses_system'] == "G":
					t_offset = (int(self.t_houses_degree_ut[18]) / -1) + int(self.t_planets_degree_ut[i])
					trueoffset = (int(self.t_houses_degree_ut[6]) / -1) + int(self.t_planets_degree_ut[i])
				else:
					offset = zeropoint + self.t_planets_degree_ut[i] + t_planets_delta[e]
					trueoffset = (int(self.t_houses_degree_ut[6]) / -1) + int(self.t_planets_degree_ut[i])

				x1 = self.sliceToX(0, (r - self.c3), t_offset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), t_offset) + self.c3
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.colors['paper_1'], self.colors["color_transit_2"])

				x1 = self.sliceToX(0, (r - self.c1), t_offset) + self.c1
				y1 = self.sliceToY(0, (r - self.c1), t_offset) + self.c1
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.colors['paper_1'], self.colors["color_transit_2"])


				if (not (23 <= i and i <= 34)):

					planet_x = self.sliceToX(0, (r - rplanet), offset) + rplanet
					planet_y = self.sliceToY(0, (r - rplanet), offset) + rplanet
					output = output + '<g transform="translate(-6,-6)"><g transform="scale(0.5)"><use x="' + str(planet_x*2) + '" y="' + str(planet_y*2) + '" xlink:href="#' + self.planets[i]['name'] + '" /></g></g>\n'

					text_offset = offset
					# text_offset = 10
					dropin = rplanet
					xtext = self.sliceToX(0, (r - dropin), text_offset) + dropin + self.settings.settings_svg[
						"offset_degree_planet_x"]
					ytext = self.sliceToY(0, (r - dropin), text_offset) + dropin + self.settings.settings_svg[
						"offset_degree_planet_y"]
					output = output + '<text text-anchor="start" x="' + str(xtext + 0) + '" y="' + str(
						ytext - 0) + '"  style="fill:' + self.colors["color_transit_2"] + '; font-size: 7px;">' + self.dec2deg(
						self.t_planets_degree[(i)]+1, type="0") + '</text>'
					output = output + ''

					# #transit planet line
					# x1 = self.sliceToX( 0 , r+3 , t_offset ) - 3
					# y1 = self.sliceToY( 0 , r+3 , t_offset ) - 3
					# x2 = self.sliceToX( 0 , r-3 , t_offset ) + 3
					# y2 = self.sliceToY( 0 , r-3 , t_offset ) + 3
					# output = output + '<line x1="'+str(x1)+'" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="'+str(y2)+'" style="stroke: '+self.planets[i]['color']+'; stroke-width: 1px; stroke-opacity:.8;"/>\n'
					# # transit planet line
					# # dropin = rplanet
					# delta = 2
					#
					# x1 = self.sliceToX(0, r + delta - self.c3, t_offset) - delta + self.c3
					# y1 = self.sliceToY(0, r + delta - self.c3, t_offset) - delta + self.c3
					# x2 = self.sliceToX(0, r - delta - self.c3, t_offset) + delta + self.c3
					# y2 = self.sliceToY(0, r - delta - self.c3, t_offset) + delta + self.c3
					# output = output + '<line x1="' + str(x1) + '" y1="' + str(y1) + '" x2="' + str(x2) + '" y2="' + str(
					# 	y2) + '" style="stroke: ' + self.planets[i]['color'] + '; stroke-width: 1px; stroke-opacity:.8;"/>\n'


				# #transit planet degree text
					# rotate = self.houses_degree_ut[0] - self.t_planets_degree_ut[i]
					# textanchor="end"
					# t_offset += group_offset[i]
					# rtext=-3.0
					#
					# if -90 > rotate > -270:
					# 	rotate = rotate + 180.0
					# 	textanchor="start"
					# if 270 > rotate > 90:
					# 	rotate = rotate - 180.0
					# 	textanchor="start"
					#
					#
					# if textanchor == "end":
					# 	xo=1
					# else:
					# 	xo=-1
					# deg_x = self.sliceToX( 0 , (r-rtext) , t_offset + xo ) + rtext
					# deg_y = self.sliceToY( 0 , (r-rtext) , t_offset + xo ) + rtext
					# degree=int(t_offset)
					# output += '<g transform="translate(%s,%s)">' % (deg_x,deg_y)
					# output += '<text transform="rotate(%s)" text-anchor="%s' % (rotate,textanchor)
					# output += '" style="fill: '+self.planets[i]['color']+'; font-size: 10px;">'+self.dec2deg(self.t_planets_degree[i],type="1")
					# output += '</text></g>\n'

					#check transit
					# dropin=0
					# #planet line
					# x1 = self.sliceToX( 0 , r-(dropin+3) , offset ) + (dropin+3)
					# y1 = self.sliceToY( 0 , r-(dropin+3) , offset ) + (dropin+3)
					# x2 = self.sliceToX( 0 , (r-(dropin-3)) , offset ) + (dropin-3)
					# y2 = self.sliceToY( 0 , (r-(dropin-3)) , offset ) + (dropin-3)
					# # output = output + '<line x1="'+str(x1)+'" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="'+str(y2)+'" style="stroke: '+self.planets[i]['color']+'; stroke-width: 2px; stroke-opacity:.6;"/>\n'
					#
					#
					# dropin=160
					# x1 = self.sliceToX( 0 , r-dropin , offset ) + dropin
					# y1 = self.sliceToY( 0 , r-dropin , offset ) + dropin
					# x2 = self.sliceToX( 0 , (r-(dropin-3)) , offset ) + (dropin-3)
					# y2 = self.sliceToY( 0 , (r-(dropin-3)) , offset ) + (dropin-3)
					# # output = output + '<line x1="'+str(x1)+'" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="'+str(y2)+'" style="stroke: '+self.planets[i]['color']+'; stroke-width: 2px; stroke-opacity:.6;"/>\n'

					#line2
					x1=self.sliceToX( 0 , (r-rplanet-14) , t_offset ) + rplanet + 14
					y1=self.sliceToY( 0 , (r-rplanet-14) , t_offset ) + rplanet + 14
					x2=self.sliceToX( 0 , (r-rplanet-8) , offset ) + rplanet + 8
					y2=self.sliceToY( 0 , (r-rplanet-8) , offset ) + rplanet + 8
					output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.2;"/>\n' % (x1,y1,x2,y2,self.colors["color_transit_2"])


		return output

	def getPlanetsDelta(self, temp_planets_degree_ut):
		planets_degut={}

		diff=range(len(self.planets))
		for i in range(len(self.planets)):
			if self.planets[i]['visible'] == 1:
				#list of planets sorted by degree
				planets_degut[temp_planets_degree_ut[i]]=i
		keys = list(planets_degut.keys())
		keys.sort()
		switch = 0

		planets_degrouped = {}
		groups = []
		planets_by_pos = list(range(len(planets_degut)))
		planet_drange = 3.4
		# get groups closely together
		group_open = False
		for e in range(len(keys)):
			i = planets_degut[keys[e]]
			# get distances between planets
			if e == 0:
				prev = temp_planets_degree_ut[planets_degut[keys[-1]]]
				next = temp_planets_degree_ut[planets_degut[keys[1]]]
			elif e == (len(keys) - 1):
				prev = temp_planets_degree_ut[planets_degut[keys[e - 1]]]
				next = temp_planets_degree_ut[planets_degut[keys[0]]]
			else:
				prev = temp_planets_degree_ut[planets_degut[keys[e - 1]]]
				next = temp_planets_degree_ut[planets_degut[keys[e + 1]]]
			diffa = self.degreeDiff(prev, temp_planets_degree_ut[i])
			diffb = self.degreeDiff(next, temp_planets_degree_ut[i])
			planets_by_pos[e] = [i, diffa, diffb]
			# dprint "%s %s %s" % (self.planets[i]['label'],diffa,diffb)
			if (diffb < planet_drange):
				if group_open:
					groups[-1].append([e, diffa, diffb, self.planets[planets_degut[keys[e]]]["label"]])
				else:
					group_open = True
					groups.append([])
					groups[-1].append([e, diffa, diffb, self.planets[planets_degut[keys[e]]]["label"]])
			else:
				if group_open:
					groups[-1].append([e, diffa, diffb, self.planets[planets_degut[keys[e]]]["label"]])
				group_open = False

		def zero(x):
			return 0

		planets_delta = list(map(zero, range(len(self.planets))))

		# dprint (groups)
		# dprint planets_by_pos
		for a in range(len(groups)):
			# Two grouped planets
			if len(groups[a]) == 2:
				next_to_a = groups[a][0][0] - 1
				if groups[a][1][0] == (len(planets_by_pos) - 1):
					next_to_b = 0
				else:
					next_to_b = groups[a][1][0] + 1
				# if both planets have room
				if (groups[a][0][1] > (2 * planet_drange)) & (groups[a][1][2] > (2 * planet_drange)):
					planets_delta[groups[a][0][0]] = -(planet_drange - groups[a][0][2]) / 2
					planets_delta[groups[a][1][0]] = +(planet_drange - groups[a][0][2]) / 2
				# if planet a has room
				elif (groups[a][0][1] > (2 * planet_drange)):
					planets_delta[groups[a][0][0]] = -planet_drange
				# if planet b has room
				elif (groups[a][1][2] > (2 * planet_drange)):
					planets_delta[groups[a][1][0]] = +planet_drange

				# if planets next to a and b have room move them
				elif (planets_by_pos[next_to_a][1] > (2.4 * planet_drange)) & (
						planets_by_pos[next_to_b][2] > (2.4 * planet_drange)):
					planets_delta[(next_to_a)] = (groups[a][0][1] - planet_drange * 2)
					planets_delta[groups[a][0][0]] = -planet_drange * .5
					planets_delta[next_to_b] = -(groups[a][1][2] - planet_drange * 2)
					planets_delta[groups[a][1][0]] = +planet_drange * .5

				# if planet next to a has room move them
				elif (planets_by_pos[next_to_a][1] > (2 * planet_drange)):
					planets_delta[(next_to_a)] = (groups[a][0][1] - planet_drange * 2.5)
					planets_delta[groups[a][0][0]] = -planet_drange * 1.2

				# if planet next to b has room move them
				elif (planets_by_pos[next_to_b][2] > (2 * planet_drange)):
					planets_delta[next_to_b] = -(groups[a][1][2] - planet_drange * 2.5)
					planets_delta[groups[a][1][0]] = +planet_drange * 1.2

			# Three grouped planets or more
			xl = len(groups[a])
			if xl >= 3:

				available = groups[a][0][1]
				for f in range(xl):
					available += groups[a][f][2]
				need = (3 * planet_drange) + (1.2 * (xl - 1) * planet_drange)
				leftover = available - need
				xa = groups[a][0][1]
				xb = groups[a][(xl - 1)][2]

				# center
				if (xa > (need * .5)) & (xb > (need * .5)):
					startA = xa - (need * .5)
				# position relative to next planets
				else:
					startA = (leftover / (xa + xb)) * xa
					startB = (leftover / (xa + xb)) * xb

				if available > need:
					planets_delta[groups[a][0][0]] = startA - groups[a][0][1] + (1.5 * planet_drange)
					for f in range(xl - 1):
						planets_delta[groups[a][(f + 1)][0]] = 1.2 * planet_drange + planets_delta[groups[a][f][0]] - \
															   groups[a][f][2]
		return planets_delta

	def makePatterns( self ):
		"""
		* Stellium: At least four planets linked together in a series of continuous conjunctions.
    	* Grand trine: Three trine aspects together.
		* Grand cross: Two pairs of opposing planets squared to each other.
		* T-Square: Two planets in opposition squared to a third. 
		* Yod: Two qunicunxes together joined by a sextile. 
		"""
		conj = {} #0
		opp = {} #10
		sq = {} #5
		tr = {} #6
		qc = {} #9
		sext = {} #3
		for i in range(len(self.planets)):
			a=self.planets_degree_ut[i]
			qc[i]={}
			sext[i]={}
			opp[i]={}
			sq[i]={}
			tr[i]={}
			conj[i]={}
			#skip some points
			n = self.planets[i]['name']
			if n == 'earth' or n == 'true node' or n == 'osc. apogee' or n == 'intp. apogee' or n == 'intp. perigee':
				continue
			if n == 'Dsc' or n == 'Ic':
				continue
			for j in range(len(self.planets)):
				#skip some points
				n = self.planets[j]['name']
				if n == 'earth' or n == 'true node' or n == 'osc. apogee' or n == 'intp. apogee' or n == 'intp. perigee':
					continue	
				if n == 'Dsc' or n == 'Ic':
					continue
				b=self.planets_degree_ut[j]
				delta=float(self.degreeDiff(a,b))
				#check for opposition
				xa = float(self.aspects[10]['degree']) - float(self.aspects[10]['orb'])
				xb = float(self.aspects[10]['degree']) + float(self.aspects[10]['orb'])
				if( xa <= delta <= xb ):
					opp[i][j]=True	
				#check for conjunction
				xa = float(self.aspects[0]['degree']) - float(self.aspects[0]['orb'])
				xb = float(self.aspects[0]['degree']) + float(self.aspects[0]['orb'])
				if( xa <= delta <= xb ):
					conj[i][j]=True					
				#check for squares
				xa = float(self.aspects[5]['degree']) - float(self.aspects[5]['orb'])
				xb = float(self.aspects[5]['degree']) + float(self.aspects[5]['orb'])
				if( xa <= delta <= xb ):
					sq[i][j]=True			
				#check for qunicunxes
				xa = float(self.aspects[9]['degree']) - float(self.aspects[9]['orb'])
				xb = float(self.aspects[9]['degree']) + float(self.aspects[9]['orb'])
				if( xa <= delta <= xb ):
					qc[i][j]=True
				#check for sextiles
				xa = float(self.aspects[3]['degree']) - float(self.aspects[3]['orb'])
				xb = float(self.aspects[3]['degree']) + float(self.aspects[3]['orb'])
				if( xa <= delta <= xb ):
					sext[i][j]=True
							
		yot={}
		#check for double qunicunxes
		for k,v in qc.items():
			if len(qc[k]) >= 2:
				#check for sextile
				for l,w in qc[k].items():
					for m,x in qc[k].items():
						if m in sext[l]:
							if l > m:
								yot['%s,%s,%s' % (k,m,l)] = [k,m,l]
							else:
								yot['%s,%s,%s' % (k,l,m)] = [k,l,m]
		tsquare={}
		#check for opposition
		for k,v in opp.items():
			if len(opp[k]) >= 1:
				#check for square
				for l,w in opp[k].items():
						for a,b in sq.items():
							if k in sq[a] and l in sq[a]:
								#print 'got tsquare %s %s %s' % (a,k,l)
								if k > l:
									tsquare['%s,%s,%s' % (a,l,k)] = '%s => %s, %s' % (
										self.planets[a]['label'],self.planets[l]['label'],self.planets[k]['label'])
								else:
									tsquare['%s,%s,%s' % (a,k,l)] = '%s => %s, %s' % (
										self.planets[a]['label'],self.planets[k]['label'],self.planets[l]['label'])
		stellium={}
		#check for 4 continuous conjunctions	
		for k,v in conj.items():
			if len(conj[k]) >= 1:
				#first conjunction
				for l,m in conj[k].items():
					if len(conj[l]) >= 1:
						for n,o in conj[l].items():
							#skip 1st conj
							if n == k:
								continue
							if len(conj[n]) >= 1:
								#third conjunction
								for p,q in conj[n].items():
									#skip first and second conj
									if p == k or p == n:
										continue
									if len(conj[p]) >= 1:										
										#fourth conjunction
										for r,s in conj[p].items():
											#skip conj 1,2,3
											if r == k or r == n or r == p:
												continue
											
											l=[k,n,p,r]
											l.sort()
											stellium['%s %s %s %s' % (l[0],l[1],l[2],l[3])]='%s %s %s %s' % (
												self.planets[l[0]]['label'],self.planets[l[1]]['label'],
												self.planets[l[2]]['label'],self.planets[l[3]]['label'])
		#print yots
		out='<g transform="translate(-30,380)">'
		if len(yot) >= 1:
			y=0
			for k,v in yot.items():
				out += '<text y="%s" style="fill:%s; font-size: 12px;">%s</text>\n' % (y,self.colors['paper_0'],_("Yot"))
				
				#first planet symbol
				out += '<g transform="translate(20,%s)">' % (y)
				out += '<use transform="scale(0.4)" x="0" y="-20" xlink:href="#%s" /></g>\n' % (
					self.planets[yot[k][0]]['name'])
				
				#second planet symbol
				out += '<g transform="translate(30,%s)">'  % (y)
				out += '<use transform="scale(0.4)" x="0" y="-20" xlink:href="#%s" /></g>\n' % (
					self.planets[yot[k][1]]['name'])

				#third planet symbol
				out += '<g transform="translate(40,%s)">'  % (y)
				out += '<use transform="scale(0.4)" x="0" y="-20" xlink:href="#%s" /></g>\n' % (
					self.planets[yot[k][2]]['name'])
				
				y=y+14
		#finalize
		out += '</g>'		
		#return out
		return ''
	
	def makeAspects( self , r , ar ):
		out=""
		self.planets_aspects= {}
		self.planets_aspects_arr = [[[0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.aspects))]
		self.planets_aspects_arr_diff = [[[0.0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.aspects))]
		for i in range(len(self.planets)):
			self.planets_aspects[i] = {}
			start=self.planets_degree_ut[i]
			# for x in range(i):
			for x in range(len(self.planets)):
				self.planets_aspects[i][x] = {}
				end=self.planets_degree_ut[x]
				diff=float(self.degreeDiff(start,end))
				#loop orbs
				if (self.planets[i]['visible_aspect_line'] == 1) & (self.planets[x]['visible_aspect_line'] == 1):
					for z in range(len(self.aspects)):

						# orb = self.aspects[z]['orb']
						# orb1 = self.aspects[z]['orb']
						# orb2 = self.aspects[z]['orb']
						# if ('planet_orb' in self.planets[i]):
						# 	if (self.type in self.planets[i]['planet_orb']):
						# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
						# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
						# 		aspect = str(self.aspects[z]['degree'])
						# 		# dprint (aspect)
						# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
						# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
						# if ('planet_orb' in self.planets[x]):
						# 	if (self.type in self.planets[x]['planet_orb']):
						# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
						# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
						# 		aspect = str(self.aspects[z]['degree'])
						# 		# dprint (aspect)
						# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
						# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
						# orb = max([orb1, orb2])
						# # orb = (orb1 + orb2)/2
						#
						#
						#
						# if	( float(self.aspects[z]['degree']) - float(orb) ) <= diff <= ( float(self.aspects[z]['degree']) + float(orb) ):
						if (self.planetsInAspect(diff, z, i, x)):
							#check if we want to display this aspect
							if self.aspects[z]['visible'] == 1:
								# self.planets_aspects[z][i][x] = 1
								# self.planets_aspects_arr[z][i][x] = 1

								aspect = str(self.aspects[z]['degree'])
								if ('planet_orb' in self.planets[i] and 'planet_orb' in self.planets[x] ):
									orb1 = self.planets[i]['planet_orb'][self.type][aspect]
									orb2 = self.planets[x]['planet_orb'][self.type][aspect]
									orb = max([orb1, orb2])
								else:
									orb = self.aspects[z]['orb']

								self.planets_aspects_arr[z][i][x] = orb-abs(float(self.aspects[z]['degree']) - abs(float(diff)))
								# out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.planets_degree_ut[x] , self.colors["aspect_%s" %(self.aspects[z]['degree'])] )
								out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.planets_degree_ut[x] , self.aspects[z]['color'] )

		return out
	
	def makeAspectsTransit( self , r , ar ):
		out = ""
		self.atgrid=[]
		self.t_planets_aspects_arr = [[[0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.aspects))]
		self.t_planets_aspects_arr_diff = [[[0.0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.aspects))]
		for i in range(len(self.planets)):
			start=self.planets_degree_ut[i]
			for x in range(len(self.planets)):
				end=self.t_planets_degree_ut[x]
				diff=float(self.degreeDiff(start,end))
				#loop orbs
				if (self.planets[i]['visible'] == 1) & (self.planets[x]['visible'] == 1):
					if ('planet_orb' in self.planets[x]):
						if (self.type in self.planets[x]['planet_orb']):
							if (not("visible2" in self.planets[x]['planet_orb'][self.type] and self.planets[x]['planet_orb'][self.type]["visible2"] == 0)):
								if (1):
									for z in range(len(self.aspects)):
										#check for personal planets and determine orb
										# if 0 <= i <= 4 or 0 <= x <= 4:
										# 	orb_before = 1.0
										# else:
										# 	orb_before = 2.0
										#
										#
										# orb = self.aspects[z]['orb']
										# orb1 = self.aspects[z]['orb']
										# orb2 = self.aspects[z]['orb']
										# if ('planet_orb' in self.planets[i]):
										# 	if (self.type in self.planets[i]['planet_orb']):
										# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
										# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
										# 		aspect = str(self.aspects[z]['degree'])
										# 		# dprint (aspect)
										# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
										# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
										# if ('planet_orb' in self.planets[x]):
										# 	if (self.type in self.planets[x]['planet_orb']):
										# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
										# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
										# 		aspect = str(self.aspects[z]['degree'])
										# 		# dprint (aspect)
										# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
										# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
										# orb = max([orb1, orb2])
										# # orb = (orb1 + orb2)/2
										#
										# #check if we want to display this aspect
										# # if	( float(self.aspects[z]['degree']) - orb_before ) <= diff <= ( float(self.aspects[z]['degree']) + 1.0 ):
										# if	( float(self.aspects[z]['degree']) - orb ) <= diff <= ( float(self.aspects[z]['degree']) + orb ):
										if (self.planetsInAspect(diff, z, i, x)):
											if self.aspects[z]['visible'] == 1:
												# self.planets_aspects[z][i][x] = 1
												# self.planets_aspects_arr[z][i][x] = 1

												aspect = str(self.aspects[z]['degree'])
												if ('planet_orb' in self.planets[i] and 'planet_orb' in self.planets[x]):
													orb1 = self.planets[i]['planet_orb'][self.type][aspect]
													orb2 = self.planets[x]['planet_orb'][self.type][aspect]
													orb = max([orb1, orb2])
												else:
													orb = self.aspects[z]['orb']

												self.t_planets_aspects_arr[z][i][x] = orb - abs(
													float(self.aspects[z]['degree']) - abs(float(diff)))
												# out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.t_planets_degree_ut[x] , self.colors["aspect_%s" %(self.aspects[z]['degree'])] )
												out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.t_planets_degree_ut[x] , self.aspects[z]['color'] )

											#aspect grid dictionary
											if self.aspects[z]['visible_grid'] == 1:
												self.atgrid.append({})
												self.atgrid[-1]['p1']=i
												self.atgrid[-1]['p2']=x
												self.atgrid[-1]['aid']=z
												self.atgrid[-1]['diff']=diff
		return out
	
	def makeAspectTransitGrid( self , r ):
		out = ''
		out += '<text y="-15" x="0" style="fill:%s; font-size: 12px;">%s</text>\n' % (self.colors['paper_0'],_("Planets in Transit"))
		line = 0
		nl = 0
		for i in range(len(self.atgrid)):
			if i == 12:
				nl = 100
				if len(self.atgrid) > 24:
					line = -1 * ( len(self.atgrid) - 24) * 14
				else:
					line = 0
			out += '<g transform="translate(%s,%s)">' % (nl,line)
			#first planet symbol
			out += '<use transform="scale(0.4)" x="0" y="3" xlink:href="#%s" />\n' % (
				self.planets[self.atgrid[i]['p2']]['name'])
			#aspect symbol
			out += '<use  x="15" y="0" xlink:href="#orb%s" />\n' % (
				self.aspects[self.atgrid[i]['aid']]['degree'])
			#second planet symbol
			out += '<g transform="translate(30,0)">'
			out += '<use transform="scale(0.4)" x="0" y="3" xlink:href="#%s" />\n' % (
				self.planets[self.atgrid[i]['p1']]['name'])
			out += '</g>'
			#difference in degrees
			out += '<text y="8" x="45" style="fill:%s; font-size: 10px;">%s</text>' % (
				self.colors['paper_0'],
				self.dec2deg(self.atgrid[i]['diff']) )
			#line
			out += '</g>'
			line = line + 14		
		out += ''
		return out
	
	def makeAspectGrid( self , r ):
		out=""
		style='stroke:%s; stroke-width: 0.25px; stroke-opacity:.6; fill:none' % (self.colors['paper_0'])

		box=14
		if self.type == "Radix":
			xindent = 380
			yindent = 468
			revr=list(range(len(self.planets)))
			revr.reverse()
			for a in revr:
				if self.planets[a]['visible_aspect_grid'] == 1:
					start=self.planets_degree_ut[a]
					#first planet
					out = out + '<rect x="'+str(xindent)+'" y="'+str(yindent)+'" width="'+str(box)+'" height="'+str(box)+'" style="'+style+'"/>\n'
					out = out + '<use transform="scale(0.4)" x="'+str((xindent+2)*2.5)+'" y="'+str((yindent+1)*2.5)+'" xlink:href="#'+self.planets[a]['name']+'" />\n'
					xindent = xindent + box
					yindent = yindent - box
					revr2=list(range(a))
					revr2=list(range(a))
					revr2.reverse()
					xorb=xindent
					yorb=yindent + box
					for b in revr2:
						if self.planets[b]['visible_aspect_grid'] == 1:
							end=self.planets_degree_ut[b]
							diff=self.degreeDiff(start,end)
							out = out + '<rect x="'+str(xorb)+'" y="'+str(yorb)+'" width="'+str(box)+'" height="'+str(box)+'" style="'+style+'"/>\n'
							xorb=xorb+box
							for z in range(len(self.aspects)):
								#
								# orb = self.aspects[z]['orb']
								# orb1 = self.aspects[z]['orb']
								# orb2 = self.aspects[z]['orb']
								# i=a
								# x=b
								# if ('planet_orb' in self.planets[i]):
								# 	if (self.type in self.planets[i]['planet_orb']):
								# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
								# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
								# 		aspect = str(self.aspects[z]['degree'])
								# 		# dprint (aspect)
								# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
								# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
								# if ('planet_orb' in self.planets[x]):
								# 	if (self.type in self.planets[x]['planet_orb']):
								# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
								# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
								# 		aspect = str(self.aspects[z]['degree'])
								# 		# dprint (aspect)
								# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
								# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
								# orb = max([orb1, orb2])
								# # orb = (orb1 + orb2)/2
								#
								# # check if we want to display this aspect
								# # if	( float(self.aspects[z]['degree']) - orb_before ) <= diff <= ( float(self.aspects[z]['degree']) + 1.0 ):
								# if (float(self.aspects[z]['degree']) - orb) <= diff <= (
								# 		float(self.aspects[z]['degree']) + orb):
								if(self.planetsInAspect(diff, z, a, b)):
								# if	( float(self.aspects[z]['degree']) - float(self.aspects[z]['orb']) ) <= diff <= ( float(self.aspects[z]['degree']) + float(self.aspects[z]['orb']) ) and self.aspects[z]['visible_grid'] == 1:
										out = out + '<use  x="'+str(xorb-box+1)+'" y="'+str(yorb+1)+'" xlink:href="#orb'+str(self.aspects[z]['degree'])+'" />\n'
		if self.type == "Transit" or self.type == "Direction":
			box = 12
			xstart = 500
			ystart = 280
			xindent = xstart
			yindent = ystart
			revr = list(range(len(self.planets)))
			# revr.reverse()
			ii=0
			for a in revr:
				if self.planets[a]['visible_aspect_grid'] == 1:
					ii=ii+1
					start = self.planets_degree_ut[a]
					# first planet
					# out = out + '<rect x="' + str(xindent-box) + '" y="' + str(yindent) + '" width="' + str(
					# 	box) + '" height="' + str(box) + '" style="' + style + '"/>\n'
					out = out + '<use transform="scale(0.4)" x="' + str((xindent-box + 2) * 2.5) + '" y="' + str(
						ystart*2.5 + (ii*box+ 1) * 2.5) + '" xlink:href="#' + self.planets[a]['name'] + '" />\n'
					# out = out + '<rect x="' + str(xstart+i*box) + '" y="' + str(ystart-168) + '" width="' + str(
					# 	box) + '" height="' + str(box) + '" style="' + style + '"/>\n'
					out = out + '<use transform="scale(0.4)" x="' + str(xstart*2.5 + (ii*box - box) * 2.5) + '" y="' + str(
						ystart*2.5 ) + '" xlink:href="#' + self.planets[a]['name'] + '" />\n'
					xindent = xindent
					yindent = yindent + box
					revr2 = list(range(a))
					revr2 = list(range(a))
					# revr2.reverse()
					xorb = xindent
					yorb = yindent
					for b in list(range(len(self.planets))):
						if self.planets[b]['visible_aspect_grid'] == 1:
							end = self.t_planets_degree_ut[b]
							diff = self.degreeDiff(start, end)
							out = out + '<rect x="' + str(xorb) + '" y="' + str(yorb) + '" width="' + str(
								box) + '" height="' + str(box) + '" style="' + style + '"/>\n'
							xorb = xorb + box
							for z in range(len(self.aspects)):
								#
								# orb = self.aspects[z]['orb']
								# orb1 = self.aspects[z]['orb']
								# orb2 = self.aspects[z]['orb']
								# i = a
								# x = b
								# if ('planet_orb' in self.planets[i]):
								# 	if (self.type in self.planets[i]['planet_orb']):
								# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
								# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
								# 		aspect = str(self.aspects[z]['degree'])
								# 		# dprint (aspect)
								# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
								# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
								# if ('planet_orb' in self.planets[x]):
								# 	if (self.type in self.planets[x]['planet_orb']):
								# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
								# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
								# 		aspect = str(self.aspects[z]['degree'])
								# 		# dprint (aspect)
								# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
								# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
								# orb = max([orb1, orb2])
								# # orb = (orb1 + orb2)/2
								#
								# # check if we want to display this aspect
								# # if	( float(self.aspects[z]['degree']) - orb_before ) <= diff <= ( float(self.aspects[z]['degree']) + 1.0 ):
								# if (float(self.aspects[z]['degree']) - orb) <= diff <= (
								# 		float(self.aspects[z]['degree']) + orb):
								# 	# if	( float(self.aspects[z]['degree']) - float(self.aspects[z]['orb']) ) <= diff <= ( float(self.aspects[z]['degree']) + float(self.aspects[z]['orb']) ) and self.aspects[z]['visible_grid'] == 1:
								if(self.planetsInAspect(diff, z, a, b)):
									out = out + '<use  x="' + str(xorb - box + 1) + '" y="' + str(
										yorb + 1) + '" xlink:href="#orb' + str(self.aspects[z]['degree']) + '" />\n'

		return out

	def planetsInAspect( self , diff, aspect_id, p1_id, p2_id ):
		if(p1_id==2 and p2_id==3 and self.aspects[aspect_id]['degree']==108 ):
			1
		z = aspect_id
		i = p1_id
		x = p2_id
		orb = self.aspects[z]['orb']
		orb1 = self.aspects[z]['orb']
		orb2 = self.aspects[z]['orb']
		if ('planet_orb' in self.planets[i]):
			if (self.type in self.planets[i]['planet_orb']):
				if ("default" in self.planets[i]['planet_orb'][self.type]):
					orb1 = self.planets[i]['planet_orb'][self.type]["default"]
				aspect = str(self.aspects[z]['degree'])
				# dprint (aspect)
				if (aspect in self.planets[i]['planet_orb'][self.type]):
					orb1 = self.planets[i]['planet_orb'][self.type][aspect]
		if ('planet_orb' in self.planets[x]):
			if (self.type in self.planets[x]['planet_orb']):
				if ("default" in self.planets[x]['planet_orb'][self.type]):
					orb2 = self.planets[x]['planet_orb'][self.type]["default"]
				aspect = str(self.aspects[z]['degree'])
				# dprint (aspect)
				if (aspect in self.planets[x]['planet_orb'][self.type]):
					orb2 = self.planets[x]['planet_orb'][self.type][aspect]
		orb = max([orb1, orb2])
		# orb = max([orb1, orb2]) + min([orb1, orb2])/2
		# orb = (orb1 + orb2)/2

		# check if we want to display this aspect
		# if	( float(self.aspects[z]['degree']) - orb_before ) <= diff <= ( float(self.aspects[z]['degree']) + 1.0 ):
		if (float(self.aspects[z]['degree']) - orb) <= diff <= (float(self.aspects[z]['degree']) + orb):
			return True
		else:
			return False

	def makeElements( self , r ):
		total = self.fire + self.earth + self.air + self.water
		pf = int(round(100*self.fire/total))
		pe = int(round(100*self.earth/total))
		pa = int(round(100*self.air/total))
		pw = int(round(100*self.water/total))
		out = '<g transform="translate(-30,79)">\n'
		out = out + '<text y="0" style="fill:#ff6600; font-size: 10px;">'+self.label['fire']+'  '+str(pf)+'%</text>\n'
		out = out + '<text y="12" style="fill:#6a2d04; font-size: 10px;">'+self.label['earth']+' '+str(pe)+'%</text>\n'
		out = out + '<text y="24" style="fill:#6f76d1; font-size: 10px;">'+self.label['air']+'   '+str(pa)+'%</text>\n'
		out = out + '<text y="36" style="fill:#630e73; font-size: 10px;">'+self.label['water']+' '+str(pw)+'%</text>\n'		
		out = out + '</g>\n'
		return out

	def makePlanetGrid(self):
		out = ''
		# loop over all planets
		li = 10
		offset = 0
		for i in range(len(self.planets)):
			# if i == 27:
			# 	li = 10
			# 	offset = -120
			if  not(23 <= i and i <= 34):
				if self.planets[i]['visible'] == 1:
					# start of line
					out = out + '<g transform="translate(%s,%s)">' % (offset, li)
					# planet text
					# out = out + '<text text-anchor="end" style="fill:%s; font-size: 10px;">%s</text>' % (self.colors['paper_0'],self.planets[i]['label'])
					# planet symbol
					out = out + '<g transform="translate(5,-8)"><use transform="scale(0.4)" xlink:href="#' + \
						  self.planets[i]['name'] + '" /></g>'
					# planet degree
					out = out + '<text text-anchor="start" x="16" style="fill:%s; font-size: 10px;">%s</text>' % (
					self.colors['paper_0'], self.dec2deg(self.planets_degree[i]))
					# zodiac
					out = out + '<g transform="translate(64,-8)"><use transform="scale(0.3)" xlink:href="#' + self.zodiac[
						self.planets_sign[i]] + '" /></g>'
					# planet retrograde
					if self.planets_retrograde[i]:
						out = out + '<g transform="translate(76,-6)"><use transform="scale(.5)" xlink:href="#retrograde" /></g>'

					# end of line
					out = out + '</g>\n'
					# offset between lines
					li = li + 14

		out = out + '\n'
		return out

	def makePlanetGrid_t(self):
		out = ''
		# loop over all planets
		li = 10
		offset = 0
		for i in range(len(self.planets)):
			# if i == 27:
			# 	li = 10
			# 	offset = -120
			if  not(23 <= i and i <= 34):
				if self.planets[i]['visible'] == 1:
					# start of line
					out = out + '<g transform="translate(%s,%s)">' % (offset, li)
					# planet text
					# out = out + '<text text-anchor="end" style="fill:%s; font-size: 10px;">%s</text>' % (self.colors['paper_0'],self.planets[i]['label'])
					# planet symbol
					out = out + '<g transform="translate(5,-8)"><use transform="scale(0.4)" xlink:href="#' + \
						  self.planets[i]['name'] + '" /></g>'
					# planet degree
					out = out + '<text text-anchor="start" x="16" style="fill:%s; font-size: 10px;">%s</text>' % (
					self.colors['paper_0'], self.dec2deg(self.t_planets_degree[i]))
					# zodiac
					out = out + '<g transform="translate(64,-8)"><use transform="scale(0.3)" xlink:href="#' + self.zodiac[
						self.t_planets_sign[i]] + '" /></g>'
					# planet retrograde
					if self.t_planets_retrograde[i]:
						out = out + '<g transform="translate(76,-6)"><use transform="scale(.5)" xlink:href="#retrograde" /></g>'

					# end of line
					out = out + '</g>\n'
					# offset between lines
					li = li + 14

		out = out + '\n'
		return out

	def makeHousesGrid( self ):
		out = ''
		li=10
		for i in range(12):
			if i < 9:
				cusp = '&#160;&#160;'+str(i+1)
			else:
				cusp = str(i+1)
			out += '<g transform="translate(0,'+str(li)+')">'
			# out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s %s:</text>' % (self.colors['paper_0'],self.label['cusp'],cusp)
			out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s:</text>' % (self.colors['paper_0'],cusp)
			out += '<g transform="translate(40,-8)"><use transform="scale(0.3)" xlink:href="#'+self.zodiac[self.houses_sign[i]]+'" /></g>'
			out += '<text x="53" style="fill:%s; font-size: 10px;"> %s</text>' % (self.colors['paper_0'],self.dec2deg(self.houses_degree[i]))
			out += '</g>\n'
			li = li + 14
		out += '\n'
		return out
	def makeHousesGrid_t( self ):
		out = ''
		li=10
		for i in range(12):
			if i < 9:
				cusp = '&#160;&#160;'+str(i+1)
			else:
				cusp = str(i+1)
			out += '<g transform="translate(0,'+str(li)+')">'
			# out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s %s:</text>' % (self.colors['paper_0'],self.label['cusp'],cusp)
			out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s:</text>' % (self.colors['paper_0'],cusp)
			out += '<g transform="translate(40,-8)"><use transform="scale(0.3)" xlink:href="#'+self.zodiac[self.t_houses_sign[i]]+'" /></g>'
			out += '<text x="53" style="fill:%s; font-size: 10px;"> %s</text>' % (self.colors['paper_0'],self.dec2deg(self.t_houses_degree[i]))
			out += '</g>\n'
			li = li + 14
		out += '\n'
		return out

	"""Export/Import Functions related to openastro.org

	def exportOAC(filename)
	def importOAC(filename)
	def importOroboros(filename)
	
	"""
	
	def exportOAC(self,filename):
		template="""<?xml version='1.0' encoding='UTF-8'?>
<openastrochart>
	<name>$name</name>
	<datetime>$datetime</datetime>
	<location>$location</location>
	<altitude>$altitude</altitude>
	<latitude>$latitude</latitude>
	<longitude>$longitude</longitude>
	<countrycode>$countrycode</countrycode>
	<timezone>$timezone</timezone>
	<geonameid>$geonameid</geonameid>
	<timezonestr>$timezonestr</timezonestr>
	<extra>$extra</extra>
</openastrochart>"""
		h,m,s = self.decHour(openAstro.hour)
		dt=datetime.datetime(openAstro.year,openAstro.month,openAstro.day,h,m,s)
		substitute={}
		substitute['name']=self.name
		substitute['datetime']=dt.strftime("%Y-%m-%d %H:%M:%S")
		substitute['location']=self.location
		substitute['altitude']=self.altitude
		substitute['latitude']=self.geolat
		substitute['longitude']=self.geolon
		substitute['countrycode']=self.countrycode
		substitute['timezone']=self.timezone
		substitute['timezonestr']=self.timezonestr
		substitute['geonameid']=self.geonameid
		substitute['extra']=''
		#write the results to the template
		output=Template(template).substitute(substitute)
		f=open(filename,"w")
		f.write(output)
		f.close()
		dprint("exporting OAC: %s" % filename)
		return
	
	def importOAC(self, filename):
		r=importfile.getOAC(filename)[0]
		dt = datetime.datetime.strptime(r['datetime'],"%Y-%m-%d %H:%M:%S")
		self.name=r['name']
		self.countrycode=r['countrycode']
		self.altitude=int(r['altitude'])
		self.geolat=float(r['latitude'])
		self.geolon=float(r['longitude'])
		self.timezone=float(r['timezone'])
		self.geonameid=r['geonameid']
		if "timezonestr" in r:
			self.timezonestr=r['timezonestr']
		else:
			self.timezonestr=db.gnearest(self.geolat,self.geolon)['timezonestr']
		self.location=r['location']
		self.year=dt.year
		self.month=dt.month
		self.day=dt.day
		self.hour=self.decHourJoin(dt.hour,dt.minute,dt.second)
		#Make locals
		self.utcToLocal()
		#debug dprint
		dprint('importOAC: %s' % filename)
		return
	
	def importOroboros(self, filename):
		r=importfile.getOroboros(filename)[0]
		#naive local datetime
		naive = datetime.datetime.strptime(r['datetime'],"%Y-%m-%d %H:%M:%S")
		#aware datetime object
		dt_input = datetime.datetime(naive.year, naive.month, naive.day, naive.hour, naive.minute, naive.second)
		dt = pytz.timezone(r['zoneinfo']).localize(dt_input)
		#naive utc datetime object
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()
		
		#process latitude/longitude
		deg,type,min,sec = r['latitude'].split(":")
		lat = float(deg)+( float(min) / 60.0 )+( float(sec) / 3600.0 )
		if type == "S":
			lat = decimal / -1.0
		deg,type,min,sec = r['longitude'].split(":")
		lon = float(deg)+( float(min) / 60.0 )+( float(sec) / 3600.0 )
		if type == "W":
			lon = decimal / -1.0			
		
		geon = db.gnearest(float(lat),float(lon))
		self.timezonestr=geon['timezonestr']
		self.geonameid=geon['geonameid']		
		self.name=r['name']
		self.countrycode=''
		self.altitude=int(r['altitude'])
		self.geolat=lat
		self.geolon=lon
		self.timezone=self.offsetToTz(dt.utcoffset())
		self.location='%s, %s' % (r['location'],r['countryname'])
		self.year=dt_utc.year
		self.month=dt_utc.month
		self.day=dt_utc.day
		self.hour=self.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		#Make locals
		self.utcToLocal()
		#debug dprint
		dprint('importOroboros: UTC: %s file: %s' % (dt_utc,filename))
		return
	
	def importSkylendar(self, filename):
		r = importfile.getSkylendar(filename)[0]
		
		#naive local datetime
		naive = datetime.datetime(int(r['year']),int(r['month']),int(r['day']),int(r['hour']),int(r['minute']))
		#aware datetime object
		dt_input = datetime.datetime(naive.year, naive.month, naive.day, naive.hour, naive.minute, naive.second)
		dt = pytz.timezone(r['zoneinfofile']).localize(dt_input)
		#naive utc datetime object
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()

		geon = db.gnearest(float(r['latitude']),float(r['longitude']))
		self.timezonestr=geon['timezonestr']
		self.geonameid=geon['geonameid']				
		self.name=r['name']
		self.countrycode=''
		self.altitude=25
		self.geolat=float(r['latitude'])
		self.geolon=float(r['longitude'])
		self.timezone=float(r['timezone'])
		self.location='%s, %s' % (r['location'],r['countryname'])
		self.year=dt_utc.year
		self.month=dt_utc.month
		self.day=dt_utc.day
		self.hour=self.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		#Make locals
		self.utcToLocal()		
		return	

	def importAstrolog32(self, filename):
		r = importfile.getAstrolog32(filename)[0]

		#timezone string
		timezone_str = zonetab.nearest_tz(float(r['latitude']),float(r['longitude']),zonetab.timezones())[2]
		#naive local datetime
		naive = datetime.datetime(int(r['year']),int(r['month']),int(r['day']),int(r['hour']),int(r['minute']),int(r['second']))
		#aware datetime object
		dt_input = datetime.datetime(naive.year, naive.month, naive.day, naive.hour, naive.minute, naive.second)
		dt = pytz.timezone(timezone_str).localize(dt_input)
		#naive utc datetime object
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()

		geon = db.gnearest(float(r['latitude']),float(r['longitude']))
		self.timezonestr=geon['timezonestr']
		self.geonameid=geon['geonameid']		
		self.name=r['name']
		self.countrycode=''
		self.altitude=25
		self.geolat=float(r['latitude'])
		self.geolon=float(r['longitude'])
		self.timezone=self.offsetToTz(dt.utcoffset())
		self.location=r['location']
		self.year=dt_utc.year
		self.month=dt_utc.month
		self.day=dt_utc.day
		self.hour=self.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		#Make locals
		self.utcToLocal()		
		return
	
	def importZet8(self, filename):
		h=open(filename)
		f=codecs.EncodedFile(h,"utf-8","latin-1")
		data=[]
		for line in f.readlines():
			s=line.split(";")
			if s[0] == line:
				continue
			
			data.append({})
			data[-1]['name']=s[0].strip()
			day=int( s[1].strip().split('.')[0] )
			month=int( s[1].strip().split('.')[1] )
			year=int( s[1].strip().split('.')[2] )
			hour=int(  s[2].strip().split(':')[0] )
			minute=int( s[2].strip().split(':')[1] )
			if len(s[3].strip()) > 3:
				data[-1]['timezone']=float( s[3].strip().split(":")[0] )
				if data[-1]['timezone'] < 0:
					data[-1]['timezone']-= float( s[3].strip().split(":")[1] ) / 60.0
				else:
					data[-1]['timezone']+= float( s[3].strip().split(":")[1] ) / 60.0
			elif len(s[3].strip()) > 0:
				data[-1]['timezone']=int(s[3].strip())
			else:
				data[-1]['timezone']=0
				
			#substract timezone from date
			dt = datetime.datetime(year,month,day,hour,minute)
			dt = dt - datetime.timedelta(seconds=float(data[-1]['timezone'])*float(3600))
			data[-1]['year'] = dt.year
			data[-1]['month'] = dt.month
			data[-1]['day'] = dt.day
			data[-1]['hour'] =  float(dt.hour) + float(dt.minute/60.0)
			data[-1]['location']=s[4].strip()

			#latitude
			p=s[5].strip()
			if p.find("°") != -1:
				#later version of zet8
				if p.find("S") == -1:
					deg=p.split("°")[0] #\xc2
					min=p[p.find("°")+2:p.find("'")]
					sec=p[p.find("'")+1:p.find('"')]
					data[-1]['latitude']=float(deg)+(float(min)/60.0)
				else:
					deg=p.split("°")[0] #\xc2
					min=p[p.find("°")+2:p.find("'")]
					sec=p[p.find("'")+1:p.find('"')]
					data[-1]['latitude']=( float(deg)+(float(min)/60.0) ) / -1.0				
			else:
				#earlier version of zet8
				if p.find("s") == -1:
					i=p.find("n")
					data[-1]['latitude']=float(p[:i])+(float(p[i+1:])/60.0)
				else:
					i=p.find("s")
					data[-1]['latitude']=( float(p[:i])+(float(p[i+1:])/60.0) ) / -1.0
			#longitude
			p=s[6].strip()
			if p.find("°") != -1:
				#later version of zet8
				if p.find("W") == -1:
					deg=p.split("°")[0] #\xc2
					min=p[p.find("°")+2:p.find("'")]
					sec=p[p.find("'")+1:p.find('"')]
					data[-1]['longitude']=float(deg)+(float(min)/60.0)
				else:
					deg=p.split("°")[0] #\xc2
					min=p[p.find("°")+2:p.find("'")]
					sec=p[p.find("'")+1:p.find('"')]
					data[-1]['longitude']=( float(deg)+(float(min)/60.0) ) / -1.0				
			else:
				#earlier version of zet8
				if p.find("w") == -1:
					i=p.find("e")
					data[-1]['longitude']=float(p[:i])+(float(p[i+1:])/60.0)
				else:
					i=p.find("w")
					data[-1]['longitude']=( float(p[:i])+(float(p[i+1:])/60.0) ) / -1.0
		
		db.importZet8( cfg.peopledb , data )
		dprint('importZet8: database with %s entries: %s' % (len(data),filename))
		f.close()
		return



	def compute_destination_point(self, latitude, longitude, azimuth, distance):
		R = 6371  # Радиус Земли в километрах

		# Преобразование градусов в радианы
		lat1 = math.radians(latitude)
		lon1 = math.radians(longitude)
		azimuth_rad = math.radians(azimuth)

		# Вычисление географических координат конечной точки
		lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) +
						 math.cos(lat1) * math.sin(distance / R) * math.cos(azimuth_rad))
		lon2 = lon1 + math.atan2(math.sin(azimuth_rad) * math.sin(distance / R) * math.cos(lat1),
								 math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

		# Преобразование радианов в градусы
		lat2 = math.degrees(lat2)
		lon2 = math.degrees(lon2)

		return lat2, lon2

	def deg_180(self, deg):
		if (deg>180):
			return 180-deg
		else:
			return -(180+deg)

	def generate_degrees_steps(self, degrees_list):
		result = []
		for degrees in degrees_list:
			current_degree = 0.0
			while current_degree < 360.0:
				result.append(current_degree)
				current_degree += degrees
		return result

	def merge_and_remove_duplicates(self, *arrays):
		merged = []
		for array in arrays:
			merged.extend(array)

		unique_values = list(set(merged))
		return unique_values

	def make_aspect_degrees_list(self, degrees_list):
		degrees_steps = self.generate_degrees_steps(degrees_list)
		unique_degrees = self.merge_and_remove_duplicates(degrees_steps)
		# exclude_values = [0.0, 180.0, 360.0]
		# if exclude_values is not None:
		# 	unique_degrees = [d for d in unique_degrees if d not in exclude_values]

		sorted_degrees = sorted(unique_degrees)  # Сортируем по возрастанию
		return sorted_degrees


	def makeLocalSpaceLayer(self, dt, lat, lon, color1 =[64, 255, 0], color2=[64, 255, 0]):
		df = self.makeLocalSpaceDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceDataFrame(self, dt, lat, lon):

		planet_names = { 1: 'mercuriy', 2: 'venus', 3: 'earth', 4: 'mars', 5: 'jupiter', 6: 'saturn', 7: 'uran', 8: 'neptun', 9: 'pluton', 10: 'sun', 301: 'moon'}
		data = load('de421.bsp')

		earth = data['earth']
		ts = load.timescale()
		place = earth + wgs84.latlon(lat * N, lon * E, elevation_m=287)

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []

		for ip in range(11):
			# print(ip)
			if (ip == 0):
				i=301 # kernel 'de421.bsp' is missing 'JUPITER' - the targets it supports are: 0 SOLAR SYSTEM BARYCENTER, 1 MERCURY BARYCENTER, 2 VENUS BARYCENTER, 3 EARTH BARYCENTER, 4 MARS BARYCENTER, 5 JUPITER BARYCENTER, 6 SATURN BARYCENTER, 7 URANUS BARYCENTER, 8 NEPTUNE BARYCENTER, 9 PLUTO BARYCENTER, 10 SUN, 199 MERCURY, 399 EARTH, 299 VENUS, 301 MOON, 499 MARS
			else:
				i=ip
			if (i != 3):
				planet = data[i]
				# print(i)
				# print(planet)
				# astro = place.at(ts.utc(oa1.t_year, oa1.t_month, oa1.t_day, oa1.t_h, oa1.t_m, oa1.t_s)).observe(planet)
				# astro = place.at(ts.utc(oa1.utc_year, oa1.utc_month, oa1.utc_day, oa1.utc_h, oa1.utc_m, oa1.utc_s)).observe(planet)
				astro = place.at(ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)).observe(planet)
				# astro = place.at(ts.utc(1980, 3, 18, 23, 47, 00)).observe(planet)
				app = astro.apparent()
				alt, az, distance = app.altaz()
				azimuth = az.degrees


				# ts = load.timescale()
				# t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
				# print (t)
				# geocentric_planet = planet - earth  # vector from geocenter to sun
				# planet_subpoint = wgs84.subpoint(geocentric_planet.at(t))  # subpoint method requires a geocentric position
				# # print('subpoint latitude: ', planet_subpoint.latitude.degrees)
				# # print('subpoint longitude: ', planet_subpoint.longitude.degrees)
				# print(planet_names[i], planet_subpoint.latitude.degrees, planet_subpoint.longitude.degrees)

				# print(planet_names[i], az.degrees, alt, distance)


				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				# lons, lats = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# lons2, lats2 = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) +  ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/" + "-"  +planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"coordinates": [
					  new_longitude,
					  new_latitude
					]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					# "name": self.name + "/ " + "+" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/ " + "+" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [
					  new_longitude2,
					  new_latitude2
					]
				  }
				}
				dfd.append(dfdata)
			# print (azimuth)
		df = pd.DataFrame(dfd)
		# Use pandas to prepare data for tooltip
		df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df


	def makeLocalSpaceEarthLayer(self, dt, lat, lon, color1 =[64, 255, 0], color2=[64, 255, 0]):
		df = self.makeLocalSpaceEarthDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceEarthDataFrame(self, dt, lat, lon):

		planet_names = { 1: 'mercuriy', 2: 'venus', 3: 'earth', 4: 'mars', 5: 'jupiter', 6: 'saturn', 7: 'uran', 8: 'neptun', 9: 'pluton', 10: 'sun', 301: 'moon'}
		data = load('de421.bsp')

		earth = data['earth']
		ts = load.timescale()
		place = earth + wgs84.latlon(lat * N, self.t_geolon * E, elevation_m=287)

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []

		for ip in range(11):
			# print(ip)
			if (ip == 0):
				i=301 # kernel 'de421.bsp' is missing 'JUPITER' - the targets it supports are: 0 SOLAR SYSTEM BARYCENTER, 1 MERCURY BARYCENTER, 2 VENUS BARYCENTER, 3 EARTH BARYCENTER, 4 MARS BARYCENTER, 5 JUPITER BARYCENTER, 6 SATURN BARYCENTER, 7 URANUS BARYCENTER, 8 NEPTUNE BARYCENTER, 9 PLUTO BARYCENTER, 10 SUN, 199 MERCURY, 399 EARTH, 299 VENUS, 301 MOON, 499 MARS
			else:
				i=ip
			if (i != 3):
				planet = data[i]
				# print(i)
				# print(planet)
				# astro = place.at(ts.utc(oa1.t_year, oa1.t_month, oa1.t_day, oa1.t_h, oa1.t_m, oa1.t_s)).observe(planet)
				# astro = place.at(ts.utc(oa1.utc_year, oa1.utc_month, oa1.utc_day, oa1.utc_h, oa1.utc_m, oa1.utc_s)).observe(planet)
				astro = place.at(ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)).observe(planet)
				# astro = place.at(ts.utc(1980, 3, 18, 23, 47, 00)).observe(planet)
				app = astro.apparent()
				alt, az, distance = app.altaz()
				azimuth = az.degrees


				# ts = load.timescale()
				# t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
				# print (t)
				# geocentric_planet = planet - earth  # vector from geocenter to sun
				# planet_subpoint = wgs84.subpoint(geocentric_planet.at(t))  # subpoint method requires a geocentric position
				# # print('subpoint latitude: ', planet_subpoint.latitude.degrees)
				# # print('subpoint longitude: ', planet_subpoint.longitude.degrees)
				# print(planet_names[i], planet_subpoint.latitude.degrees, planet_subpoint.longitude.degrees)

				# print(planet_names[i], az.degrees, alt, distance)


				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				# lons, lats = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# lons2, lats2 = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" +  ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/" + "-"  +planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"coordinates": [
					  new_longitude,
					  new_latitude
					]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					# "name": self.name + "/ " + "+" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/ " + "+" + planet_names[i] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"coordinates": [
					  new_longitude2,
					  new_latitude2
					]
				  }
				}
				dfd.append(dfdata)
			# print (azimuth)
		df = pd.DataFrame(dfd)
		# Use pandas to prepare data for tooltip
		df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df




	def makeLocalSpaceSweLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150], num_planet=11):
		df = self.makeLocalSpaceSweDataFrame(dt, lat, lon, num_planet)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceSweDataFrame(self, dt, lat, lon, num_planet=11):

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)
		# swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)
		dfd= []
		# for i in range(len(self.planets)):
		for i in range(num_planet):
			# if self.planets[i]['visible'] == 1:
			if 1:
				planet_code = i
				# print (jul_day_UT)
				planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				# print (planet_pos)
				# lat = planet_pos[0][0]
				# lon = planet_pos[0][1]
				# planet_pos[0][0] = 0
				# print(self.settings.settings_planet[i]['name'] , lat, lon)
				# Вычисление азимута планеты
				azimuth, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	  [lon, lat, 287], 0, 0,
																	  planet_pos[0])
																	  # [0,0,0,0,0,0])
				# azimuth = azimuth -180
				# azimuth = self.deg_180(azimuth)
				azimuth = azimuth + 180
				if(azimuth>360):
					azimuth = azimuth-360
				# print(self.settings.settings_planet[i]['name'] , azimuth, true_altitude, apparent_altitude)
				# print (self.settings.settings_planet[i]['name'])
				# print("Азимут планеты:", azimuth)
				# print("Истинная высота:", true_altitude)
				# print("Видимая высота:", apparent_altitude)

				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				# lons, lats = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# lons2, lats2 = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) +  ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth)  + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth)  + ")",
					"coordinates": [
					  new_longitude,
					  new_latitude
					]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [
					  new_longitude2,
					  new_latitude2
					]
				  }
				}
				dfd.append(dfdata)
			# print (azimuth)
		df = pd.DataFrame(dfd)
		# Use pandas to prepare data for tooltip
		df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df


	def makeLocalSpaceAspectSweLayer(self, dt, lat, lon, color1 =[200, 200, 0], color2=[200, 200, 0], num_planet=11, aspects = [60, 90, 120]):
		df = self.makeLocalSpaceAspectSweDataFrame(dt, lat, lon, num_planet, aspects)
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer

	def makeLocalSpaceAspectSweDataFrame(self, dt, lat, lon, num_planet=11, aspects = [60, 90, 120]):

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)
		dfd= []
		for i in range(num_planet):
			if 1:
				planet_code = i
				planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				azimuth0, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	  [lon, lat, 287], 0, 0,
																	  planet_pos[0])
				# azimuth = azimuth -180
				# print(self.settings.settings_planet[i]['name'] , azimuth, true_altitude, apparent_altitude)
				# print (self.settings.settings_planet[i]['name'])
				# print("Азимут планеты:", azimuth)
				# print("Истинная высота:", true_altitude)
				# print("Видимая высота:", apparent_altitude)
				# aspects = [60, 90, 120]

				for aspect in aspects:
					azimuth = azimuth0 + aspect
					if (azimuth > 360):
						azimuth = azimuth - 360
					new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
					new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
					dfdata= {
					  "from": {
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeLocalSpaceAntisZodiacDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [+1, -1]):
		# aspects = [+1, -1]

		𝜏 = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		zero = angle * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.sin(angle), np.cos(angle), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = bluffton
		alt0, az0, distance0 = p.altaz()
		cancer_az = az0.degrees[3]


		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)
		dfd= []
		for i in range(num_planet):
			if 1:
				planet_code = i
				if (type_tr == "Radix"):
					lat_angle0 = self.planet_latitude[i]
					lon_angle0 = self.planets_degree_ut[i]
				elif (type_tr == "Transit"):
					lat_angle0 = self.t_planet_latitude[i]
					lon_angle0 = self.t_planets_degree_ut[i]

				aries_planet_pos = swe.calc_ut(jul_day_UT, 14)
				aries_azimuth0, aries_true_altitude, aries_apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR, [lon, lat, 287], 0, 0, aries_planet_pos[0])

				planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				azimuth0, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,  [lon, lat, 287], 0, 0, planet_pos[0])
				for aspect in aspects:
					# azimuth = aspect * (azimuth0 - (aries_azimuth0+90) ) + (aries_azimuth0+90)
					azimuth = aspect * (azimuth0 - (cancer_az+90) ) + (cancer_az+90)
					if (azimuth > 360):
						azimuth = azimuth - 360

					# if (aspect <= 180):
					# 	lat_angle = lat_angle0 * (90 - aspect) / 90.0
					# if (aspect > 180):
					# 	lat_angle = lat_angle0 * (aspect - 90 - 180) / 90.0
					# true_altitude = lat_angle
					# lon_angle = lon_angle0 + aspect

					# [h_lat, h_lon] = self.eclips_to_geo([lon_angle], [lat_angle], t)
					# [h_lat, h_lon] = self.eclips_to_geo0_house([lon_angle], [lat_angle], t)
					# alt0, az0, distance0 = self.eclips_to_gorizont([lon_angle], [lat_angle], dt, lat, lon)

					new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
					new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
					dfdata= {
					  "from": {
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df
	def makeLocalSpaceAntisHouseDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [+1, -1]):

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)
		dfd= []
		for i in range(num_planet):
			if 1:
				planet_code = i
				if (type_tr == "Radix"):
					lat_angle0 = self.planet_latitude[i]
					lon_angle0 = self.planets_degree_ut[i]
				elif (type_tr == "Transit"):
					lat_angle0 = self.t_planet_latitude[i]
					lon_angle0 = self.t_planets_degree_ut[i]

				planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				azimuth0, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	  [lon, lat, 287], 0, 0,
																	  planet_pos[0])
				for aspect in aspects:
					azimuth = aspect * (azimuth0 - 90) + 90
					if (azimuth > 360):
						azimuth = azimuth - 360

					# if (aspect <= 180):
					# 	lat_angle = lat_angle0 * (90 - aspect) / 90.0
					# if (aspect > 180):
					# 	lat_angle = lat_angle0 * (aspect - 90 - 180) / 90.0
					# true_altitude = lat_angle
					# lon_angle = lon_angle0 + aspect

					# [h_lat, h_lon] = self.eclips_to_geo([lon_angle], [lat_angle], t)
					# [h_lat, h_lon] = self.eclips_to_geo0_house([lon_angle], [lat_angle], t)
					# alt0, az0, distance0 = self.eclips_to_gorizont([lon_angle], [lat_angle], dt, lat, lon)

					new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
					new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
					dfdata= {
					  "from": {
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeLocalSpaceAspectLayer(self, type, type_tr, dt, lat, lon, color1 =[200, 200, 0], color2=[200, 200, 0], num_planet=11, aspects = [60, 90, 120]):
		if(type == "Sky"):
			df = self.makeLocalSpaceAspectSkyDataFrame(type_tr, dt, lat, lon, num_planet, aspects)
		elif (type == "SkyHouse"):
			df = self.makeLocalSpaceAspectSkyHouseDataFrame(type_tr, dt, lat, lon, aspects)
		elif (type == "AntisZodiac"):
			df = self.makeLocalSpaceAntisZodiacDataFrame(type_tr, dt, lat, lon, num_planet, aspects)
		elif (type == "AntisHouse"):
			df = self.makeLocalSpaceAntisHouseDataFrame(type_tr, dt, lat, lon, num_planet, aspects)
		elif(type == "Swe"):
			df = self.makeLocalSpaceAspectSweDataFrame(dt, lat, lon, num_planet, aspects)
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer

	def makeLocalSpaceAspectSkyDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [0, 60, 90, 120, 180, 240, 270, 300]):

		ts = api.load.timescale()
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		# distance2 = 6371*3.1  # Расстояние (в километрах)
		# sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		# jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)

		dfd = []
		for i in range(num_planet):

			planet_code = i

			if (type_tr == "Radix"):
				lat_angle0 = self.planet_latitude[i]
				lon_angle0 = self.planets_degree_ut[i]
			elif (type_tr == "Transit"):
				lat_angle0 = self.t_planet_latitude[i]
				lon_angle0 = self.t_planets_degree_ut[i]

			for aspect in aspects:
				if(aspect<=180):
					lat_angle =  lat_angle0 * (90-aspect)/90.0
				if(aspect>180):
					lat_angle =  lat_angle0 * (aspect-90-180)/90.0
				true_altitude = lat_angle
				lon_angle = lon_angle0 + aspect

				[h_lat, h_lon] = self.eclips_to_geo([lon_angle], [lat_angle], t)
				alt0, az0, distance0 = self.eclips_to_gorizont([lon_angle], [lat_angle], dt, lat, lon)
				azimuth = az0.degrees[0]
				new_latitude = h_lat[0]
				new_longitude = h_lon[0]
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
					"coordinates": [starting_longitude, starting_latitude]
				  },
				  "to": {
					# "name": self.name + "/" + "-"  + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"coordinates": [new_longitude, new_latitude]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [starting_longitude-180, -starting_latitude]
				  },
				  "to": {
					# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"coordinates": [new_longitude, new_latitude]
				  }
				}
				dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df
	def makeLocalSpaceAspectSkyHouseDataFrame(self, type_tr, dt, lat, lon, aspects = [0, 60, 90, 120, 180, 240, 270, 300]):
		#
		# alt0, az0, distance0 = self.eclips_to_gorizont0(self.houses_degree_ut, dt, lat, lon)
		# ts = api.load.timescale()
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# [h_lat, h_lon] = self.eclips_to_geo0_house(self.houses_degree_ut, self.houses_degree_ut, t)
		# # print(h_lat[0])
		#
		# starting_latitude = lat  # Начальная широта
		# starting_longitude = lon  # Начальная долгота
		# distance2 = 6371*3.1  # Расстояние (в километрах)
		#
		# dfd= []
		# for i in range(12):
		# 	if (1):
		# 		alt = alt0.degrees[i]
		# 		azimuth = az0.degrees[i]
		# 		new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
		# 		new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
		# 		# print(new_longitude)
		# 		new_latitude = h_lat[i]
		# 		new_longitude = h_lon[i]
		# 		# new_latitude2 = h_lat[i]
		# 		# new_longitude2 = -h_lon[i]
		#
		# 		dfdata= {
		# 		  "from": {
		# 			"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
		# 			"coordinates": [ starting_longitude,  starting_latitude ]
		# 		  },
		# 		  "to": {
		# 			"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
		# 			"coordinates": [ new_longitude, new_latitude ]
		# 		  }
		# 		}
		#
		# 		dfd.append(dfdata)
		# 		# dfdata= {
		# 		#   "from": {
		# 		# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
		# 		# 	"coordinates": [
		# 		# 	  starting_longitude,
		# 		# 	  starting_latitude
		# 		# 	]
		# 		#   },
		# 		#   "to": {
		# 		# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
		# 		# 	"coordinates": [
		# 		# 	  new_longitude2,
		# 		# 	  new_latitude2
		# 		# 	]
		# 		#   }
		# 		# }
		# 		# dfd.append(dfdata)
		# df = pd.DataFrame(dfd)
		# df["name"] = df["to"].apply(lambda t: t["name"])
		# return df

		ts = api.load.timescale()
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота

		dfd = []
		for i in range(len(self.houses_degree_ut)):
			planet_code = i
			if (type_tr == "Radix"):
				lat_angle0 = 0
				lon_angle0 = self.houses_degree_ut[i]
			elif (type_tr == "Transit"):
				lat_angle0 = 0
				lon_angle0 = self.t_houses_degree_ut[i]

			for aspect in aspects:
				if(aspect<=180):
					lat_angle =  lat_angle0 * (90-aspect)/90.0
				if(aspect>180):
					lat_angle =  lat_angle0 * (aspect-90-180)/90.0
				true_altitude = lat_angle
				lon_angle = lon_angle0 + aspect

				# [h_lat, h_lon] = self.eclips_to_geo([lon_angle], [lat_angle], t)
				[h_lat, h_lon] = self.eclips_to_geo0_house([lon_angle], [lat_angle], t)
				alt0, az0, distance0 = self.eclips_to_gorizont([lon_angle], [lat_angle], dt, lat, lon)
				azimuth = az0.degrees[0]
				new_latitude = h_lat[0]
				new_longitude = h_lon[0]
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
				# 	"coordinates": [starting_longitude, starting_latitude]
				#   },
				#   "to": {
				# 	# "name": self.name + "/" + "-"  + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	"coordinates": [new_longitude, new_latitude]
				#   }
				# }
				#
				# dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	"coordinates": [starting_longitude-180, -starting_latitude]
				#   },
				#   "to": {
				# 	# "name": self.name + "/ " + "+" + self.settings.settings_planet[i]['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self.settings.settings_planet[i]['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	"coordinates": [new_longitude, new_latitude]
				#   }
				# }
				# dfd.append(dfdata)

				dfdata= {
				  "from": {
					"name": self.name + "/"  + " K" + str(i+1) + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude,  starting_latitude ]
				  },
				  "to": {
					"name": self.name + "/"  + " K" + str(i+1) + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					"name": self.name + "/"  + "K" + str(i) + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [starting_longitude-180, -starting_latitude]
				  },
				  "to": {
					"name": self.name + "/"  + "K" + str(i) + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}
				dfd.append(dfdata)

		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeZenitDataFrame(self, dt, lat, lon):

		planet_names = { 1: 'mercuriy', 2: 'venus', 3: 'earth', 4: 'mars', 5: 'jupiter', 6: 'saturn', 7: 'uran', 8: 'neptun', 9: 'pluton', 10: 'sun', 301: 'moon'}
		data = load('de421.bsp')
		earth = data['earth']

		dfd= []
		for ip in range(11):
			# print(ip)
			if (ip == 0):
				i=301 # kernel 'de421.bsp' is missing 'JUPITER' - the targets it supports are: 0 SOLAR SYSTEM BARYCENTER, 1 MERCURY BARYCENTER, 2 VENUS BARYCENTER, 3 EARTH BARYCENTER, 4 MARS BARYCENTER, 5 JUPITER BARYCENTER, 6 SATURN BARYCENTER, 7 URANUS BARYCENTER, 8 NEPTUNE BARYCENTER, 9 PLUTO BARYCENTER, 10 SUN, 199 MERCURY, 399 EARTH, 299 VENUS, 301 MOON, 499 MARS
			else:
				i=ip
			if (i != 3):
				planet = data[i]
				geocentric_planet = planet - earth  # vector from geocenter to sun
				ts = load.timescale()
				t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
				planet_subpoint = wgs84.subpoint(geocentric_planet.at(t))  # subpoint method requires a geocentric position
				# print('subpoint latitude: ', planet_subpoint.latitude.degrees)
				# print('subpoint longitude: ', planet_subpoint.longitude.degrees)

				dfdata= {
				  "from": {
					"name": self.name + "/" + " K10 " + planet_names[i] + " (" + '{0:.1f}'.format(planet_subpoint.longitude.degrees) + ")",
					"coordinates": [
					  planet_subpoint.longitude.degrees,
					  -80
					]
				  },
				  "to": {
					"name": self.name + "/" + " K10 " + planet_names[i] + " (" + '{0:.1f}'.format(planet_subpoint.longitude.degrees) + ")",
					"coordinates": [
					  planet_subpoint.longitude.degrees,
					  80
					]
				  }
				}
				dfd.append(dfdata)
				dfdata = {
					"from": {
						"name": self.name + "/" + " K4 " + planet_names[i] + " (" + '{0:.1f}'.format(planet_subpoint.longitude.degrees+180) + ")",
						"coordinates": [
							planet_subpoint.longitude.degrees +180,
							-80
						]
					},
					"to": {
						"name": self.name + "/" + " K4 " + planet_names[i] + " (" + '{0:.1f}'.format(planet_subpoint.longitude.degrees+180) + ")",
						"coordinates": [
							planet_subpoint.longitude.degrees +180,
							80
						]
					}
				}
				dfd.append(dfdata)

		df = pd.DataFrame(dfd)
		# Use pandas to prepare data for tooltip
		df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		print (df)
		return df
	def makeZenitLayer(self, dt, lat, lon, color1 =[64, 255, 0], color2=[0, 128, 200]):
		df = self.makeZenitDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer


	def makeAscDataFrame(self, dt, lat, lon, num_planet=11):
		dfd= []
		# planet_id = 3
		# house_id = 0
		degree_delta = 2

		coord_arr_arr=[]
		coord_arr_arr_7=[]
		coord_arr=[]
		coord_arr_7=[]
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)

		event1 = openAstro.event_dt("ttt", dt, timezone=0, location="ttt", geolat=0, geolon=0)
		event1["geolat"] = lat
		event1["geolon"] = lon
		oa1 = openAstro(event1, type="Radix")
		oa1.calcAstro()

		step = 0.5
		for i in range(num_planet):
			print (self.settings.settings_planet[i]['name'])
			coord_arr = []
			coord_arr_7 = []
			planet_id = i
			for i_lon in range(int(-180 / step), int(180 / step) + 1):
				lon = i_lon * step  # Longitude ranges from -180 to 180 degrees
				# print (lon)
				# for lat in range(-60, 60, 1):  # Latitude ranges from -90 to 90 degrees
				for i_lat in range(int(-60 / step), int(60 / step) + 1):
					lat = i_lat * step  # Longitude ranges from -180 to 180 degrees
					# print (jul_day_UT, lat, lon)
					house = swe.houses(jul_day_UT, lat, lon)
					# print(house[0][0])
					# print (oa1.houses_degree_ut[house_id])
					# print(oa1.planets_degree_ut[planet_id], oa1.houses_degree_ut[planet_id], lat, lon)
					# if (oa1.degreeDiff(oa1.houses_degree_ut[house_id], oa1.planets_degree_ut[planet_id]) < degree_delta):
					if (abs(oa1.degreeDiff2(house[0][0], oa1.planets_degree_ut[planet_id])) < 0.5):
						# print(oa1.planets_degree_ut[house_id], oa1.houses_degree_ut[planet_id], lon, lat)
						# print(house[0][0], oa1.houses_degree_ut[planet_id], lon, lat, abs(oa1.degreeDiff(house[0][0], oa1.planets_degree_ut[planet_id])))
						coord_arr.append([lon, lat])
						# lat_0 = lat
						break
					if (abs(oa1.degreeDiff2(house[0][6], oa1.planets_degree_ut[planet_id])) < 0.5):
						# print(oa1.planets_degree_ut[house_id], oa1.houses_degree_ut[planet_id], lon, lat)
						# print(house[0][0], oa1.houses_degree_ut[planet_id], lon, lat)
						# print(house[0][0], oa1.houses_degree_ut[planet_id], lon, lat, abs(oa1.degreeDiff(house[0][0], oa1.planets_degree_ut[planet_id])))
						coord_arr_7.append([lon, lat])
						# lat_0 = lat
						break
			coord_arr_arr.append(coord_arr)
			coord_arr_arr_7.append(coord_arr_7)

		for ii in range(len(coord_arr_arr)):
			planet_id=ii
			coord_arr = coord_arr_arr[ii]
			for i in range(len(coord_arr)-1):
				dfdata= {
				  "from": {
					"name": " K1 " + self.settings.settings_planet[planet_id]['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K1 " + self.settings.settings_planet[planet_id]['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
					"coordinates": [coord_arr[i+1][0], coord_arr[i+1][1]]
				  }
				}
				dfd.append(dfdata)

		for ii in range(len(coord_arr_arr_7)):
			planet_id=ii
			coord_arr = coord_arr_arr_7[ii]
			for i in range(len(coord_arr)-1):
				dfdata= {
				  "from": {
					"name": " K7 " + self.settings.settings_planet[planet_id]['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K7 " + self.settings.settings_planet[planet_id]['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
					"coordinates": [coord_arr[i+1][0], coord_arr[i+1][1]]
				  }
				}
				dfd.append(dfdata)

		# print (dfd)
		df = pd.DataFrame(dfd)
		# Use pandas to prepare data for tooltip
		df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		# print (df)
		return df
	def makeAscLayer(self, dt, lat, lon, color1 =[255, 100, 100], color2=[255, 100, 100], num_planet=11):
		df = self.makeAscDataFrame(dt, lat, lon, num_planet)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer


	def makeLocalSpaceZodiakSkyLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150]):
		df = self.makeLocalSpaceZodiakSkyDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceZodiakSkyDataFrame(self, dt, lat, lon):

		𝜏 = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		zero = angle * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.sin(angle), np.cos(angle), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = bluffton
		alt0, az0, distance0 = p.altaz()
		i = np.argmax(alt0.degrees)  # Which of the 360 points has highest altitude?
		# print('Altitude of highest point on ecliptic:', alt.degrees[i])
		# print('Azimuth of highest point on ecliptic:', az.degrees[i])
		# print(az0.degrees)
		# print(alt0.degrees)
		# print(angle)

		earth = eph['earth']
		ts = load.timescale()
		place = earth + wgs84.latlon(lat * N, lon * E, elevation_m=287)
		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []
		for i in range(12):
			if (1):
				alt = alt0.degrees[i]
				azimuth = az0.degrees[i]
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " " + self.zodiac[i] + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " " + self.zodiac[i] + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude,  starting_latitude ]
				  },
				  "to": {
					# "name": self.name + "/"  + " " + self.zodiac[i] + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " " + self.zodiac[i] + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  new_longitude2,
				# 	  new_latitude2
				# 	]
				#   }
				# }
				# dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def eclips_to_gorizont0(self, eclips_arr, dt, lat, lon):
		# we get eclips degrees and return gorizodegrees !!! in dt time !!!
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)
		𝜏 = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		angle = - np.array(eclips_arr)/360 * 𝜏 + 1/4.0 * 𝜏

		zero = angle * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.sin(angle), np.cos(angle), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = bluffton
		alt0, az0, distance0 = p.altaz()
		return [alt0, az0, distance0]
	def eclips_to_gorizont(self, eclips_arr_lon, eclips_arr_lat, dt, lat, lon):
		# we get eclips degrees and return gorizodegrees !!! in dt time !!!
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)
		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		lon_rad = np.array(eclips_arr_lon)/360 * tau
		lat_rad = np.array(eclips_arr_lat) / 360 * tau

		zero = lon_rad * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = bluffton
		alt0, az0, distance0 = p.altaz()
		return [alt0, az0, distance0]

	def eclips_to_geo(self, eclips_arr_lon, eclips_arr_lat, t):
		tau = api.tau
		# lon_rad = - np.array(eclips_arr_lon) / 360 * tau + 1 / 4.0 * tau
		lon_rad = np.array(eclips_arr_lon) / 360 * tau
		lat_rad = np.array(eclips_arr_lat) / 360 * tau
		zero = lon_rad * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = 399
		lat, lon = wgs84.latlon_of(p)
		return [lat.degrees, lon.degrees]
	def eclips_to_geo0(self, eclips_arr_lon, eclips_arr_lat, t):
		tau = api.tau
		lon_rad = - np.array(eclips_arr_lon) / 360 * tau + 1 / 4.0 * tau
		lat_rad = np.array(eclips_arr_lat) / 360 * tau
		zero = lon_rad * 0.0
		f = framelib.ecliptic_frame
		# d = api.Distance([np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)])
		d = api.Distance([np.sin(lon_rad), np.cos(lon_rad), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = 399
		lat, lon = wgs84.latlon_of(p)
		# print(lon.degrees)
		return [lat.degrees, lon.degrees]
	def eclips_to_geo0_house(self, eclips_arr_lon, eclips_arr_lat, t):
		tau = api.tau
		lon_rad = - np.array(eclips_arr_lon) / 360 * tau + 1 / 4.0 * tau
		lat_rad = np.array(eclips_arr_lat) / 360 * tau
		zero = lon_rad * 0.0
		f = framelib.ecliptic_frame
		# d = api.Distance([np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)])
		d = api.Distance([np.sin(lon_rad), np.cos(lon_rad), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = 399
		lat, lon = wgs84.latlon_of(p)
		# print(lon.degrees)
		return [lat.degrees, lon.degrees]

	def makeLocalSpaceHouseSkyLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150]):
		df = self.makeLocalSpaceHouseSkyDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceHouseSkyDataFrame(self, dt, lat, lon):
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)

		# 𝜏 = api.tau
		# ts = api.load.timescale()
		# eph = api.load('de421.bsp')
		# bluffton = api.Topos(lat, lon)
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# # angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		# angle = - np.array(self.houses_degree_ut)/360 * 𝜏 + 1/4.0 * 𝜏
		#
		# zero = angle * 0.0
		# f = framelib.ecliptic_frame
		# d = api.Distance([np.sin(angle), np.cos(angle), zero])
		# v = api.Velocity([zero, zero, zero])
		# p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		# p.center = bluffton
		# alt0, az0, distance0 = p.altaz()
		alt0, az0, distance0 = self.eclips_to_gorizont0(self.houses_degree_ut, dt, lat, lon)


		# earth = eph['earth']
		# ts = load.timescale()
		# place = earth + wgs84.latlon(lat * N, lon * E, elevation_m=287)
		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []
		for i in range(12):
			if (1):
				alt = alt0.degrees[i]
				azimuth = az0.degrees[i]
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude,  starting_latitude ]
				  },
				  "to": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  new_longitude2,
				# 	  new_latitude2
				# 	]
				#   }
				# }
				# dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeLocalSpaceHouseSky2Layer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150]):
		df = self.makeLocalSpaceHouseSky2DataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceHouseSky2DataFrame(self, dt, lat, lon):

		alt0, az0, distance0 = self.eclips_to_gorizont0(self.houses_degree_ut, dt, lat, lon)
		ts = api.load.timescale()
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		[h_lat, h_lon] = self.eclips_to_geo0_house(self.houses_degree_ut, self.houses_degree_ut, t)
		# print(h_lat[0])

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []
		for i in range(12):
			if (1):
				alt = alt0.degrees[i]
				azimuth = az0.degrees[i]
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# print(new_longitude)
				new_latitude = h_lat[i]
				new_longitude = h_lon[i]
				# new_latitude2 = h_lat[i]
				# new_longitude2 = -h_lon[i]

				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude,  starting_latitude ]
				  },
				  "to": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  new_longitude2,
				# 	  new_latitude2
				# 	]
				#   }
				# }
				# dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df


	def makeLocalSpaceHouseTransitSkyLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150]):
		df = self.makeLocalSpaceHouseTransitSkyDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceHouseTransitSkyDataFrame(self, dt, lat, lon):
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)

		# 𝜏 = api.tau
		# ts = api.load.timescale()
		# eph = api.load('de421.bsp')
		# bluffton = api.Topos(lat, lon)
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# # angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		# angle = - np.array(self.t_houses_degree_ut)/360 * 𝜏 + 1/4.0 * 𝜏
		#
		# zero = angle * 0.0
		# f = framelib.ecliptic_frame
		# d = api.Distance([np.sin(angle), np.cos(angle), zero])
		# v = api.Velocity([zero, zero, zero])
		# p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		# p.center = bluffton
		# alt0, az0, distance0 = p.altaz()
		# i = np.argmax(alt0.degrees)  # Which of the 360 points has highest altitude?
		# print('Altitude of highest point on ecliptic:', alt.degrees[i])
		# print('Azimuth of highest point on ecliptic:', az.degrees[i])
		# print(az0.degrees)
		# print(alt0.degrees)
		# print(angle)
		alt0, az0, distance0 = self.eclips_to_gorizont0(self.t_houses_degree_ut, dt, lat, lon)

		# earth = eph['earth']
		# ts = load.timescale()
		# place = earth + wgs84.latlon(lat * N, lon * E, elevation_m=287)
		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.1  # Расстояние (в километрах)

		dfd= []
		for i in range(12):
			if (1):
				alt = alt0.degrees[i]
				azimuth = az0.degrees[i]
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude,  starting_latitude ]
				  },
				  "to": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  new_longitude2,
				# 	  new_latitude2
				# 	]
				#   }
				# }
				# dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeLocalSpaceHouseEquatorialSkyLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150]):
		df = self.makeLocalSpaceHouseEquatorialSkyDataFrame(dt, lat, lon)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.coordinates",
		get_target_position="to.coordinates",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceHouseEquatorialSkyDataFrame(self, dt, lat, lon):
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https://astronomy.stackexchange.com/questions/41482/how-to-find-the-local-azimuth-of-the-highest-point-of-the-ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)

		𝜏 = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# angle = - np.arange(12) / 12.0 * 𝜏 + 1/4.0 * 𝜏
		angle = - np.array(self.houses_degree_ut)/360 * 𝜏 + 1/4.0 * 𝜏

		zero = angle * 0.0
		f = framelib.ecliptic_frame
		d = api.Distance([np.sin(angle), np.cos(angle), zero])
		v = api.Velocity([zero, zero, zero])
		p = Apparent.from_time_and_frame_vectors(t, f, d, v)
		p.center = bluffton
		alt0, az0, distance0 = p.altaz()
		i = np.argmax(alt0.degrees)  # Which of the 360 points has highest altitude?
		# print('Altitude of highest point on ecliptic:', alt.degrees[i])
		# print('Azimuth of highest point on ecliptic:', az.degrees[i])
		# print(az0.degrees)
		# print(alt0.degrees)
		# print(angle)

		starting_latitude0 = 89.9
		starting_longitude0 = 0

		earth = eph['earth']
		ts = load.timescale()
		place = earth + wgs84.latlon(lat * N, lon * E, elevation_m=287)
		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371*3.14/2  # Расстояние (в километрах)

		dfd= []
		for i in range(12):
			if (1):
				alt = alt0.degrees[i]
				azimuth = az0.degrees[i]
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ starting_longitude0,  starting_latitude0 ]
				  },
				  "to": {
					# "name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
					"name": self.name + "/"  + " K" + str(i+1) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + ")",
					"coordinates": [ new_longitude, new_latitude ]
				  }
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiak-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  new_longitude2,
				# 	  new_latitude2
				# 	]
				#   }
				# }
				# dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df




	def makeIconLayer(self, df_data):

		# DATA_URL = "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/biergartens.json"
		ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Icon_for_my_work.png/640px-Icon_for_my_work.png"
		icon_data = {"url": ICON_URL, "width": 305, "height": 400, "anchorY": 400,}

		# df_data = [{"lat":47.29810329873421,"lon":39.710726380651636,"name":"Цирк"}]
		data = pd.DataFrame(df_data)

		data["icon_data"] = None
		for i in data.index:
		  data["icon_data"][i] = icon_data
		# view_state = pdk.data_utils.compute_view(data[["lon", "lat"]])

		layer = pdk.Layer(
		  type="IconLayer",
		  data=data,
		  get_icon="icon_data",
		  get_size=4,
		  size_scale=15,
		  get_position=["lon", "lat"],
		  pickable=True,
		)
		return layer

	def makeIconLayer2(self, df_data, lat, lon, icon_data = {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Icon_for_my_work.png/640px-Icon_for_my_work.png", "width": 305, "height": 400, "anchorY": 400, "get_size": 4, 'size_scale': 15}):

		# ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Icon_for_my_work.png/640px-Icon_for_my_work.png"
		# icon_data = {"url": ICON_URL, "width": 305, "height": 400, "anchorY": 400,}

		# df_data = [{"lat":47.29810329873421,"lon":39.710726380651636,"name":"Цирк"}]
		df_data_t = copy.deepcopy(df_data)
		for i in range(len(df_data)):
			arr = Geodesic.WGS84.Inverse(lat, lon, df_data[i]["lat"], df_data[i]["lon"])
			azimuth = arr["azi1"]
			if(azimuth<0): azimuth = azimuth + 360
			# txt = df_data_t[i]["name"]
			# df_data_t[i]["name"]= " " + "az=" + '{0:.1f}'.format(float(azimuth)) + " dist=" + '{0:.0f}'.format(float(arr["s12"]/1000))  +"km - " + df_data_t[i]["name"]
			df_data_t[i]["name"]= " " + "az=" + '{0:.1f}'.format(float(azimuth)) + " - " + df_data_t[i]["name"]
			df_data_t[i]["icon_data"]= icon_data
		data = pd.DataFrame(df_data_t)
		# print (data)

		# data["icon_data"] = None
		# for i in data.index:
		#   data["icon_data"][i] = icon_data

		layer = pdk.Layer(
		  type="IconLayer",
		  data=data,
		  get_icon="icon_data",
		  get_size=icon_data["get_size"],
		  size_scale=icon_data["size_scale"],
		  get_position=["lon", "lat"],
		  pickable=True,
		)
		return layer


	def calcProbability(self, num_planet=10, num_aspect=2, orb=3):
		pro = num_planet * orb * num_aspect *2 / 360
		print(pro)
		return pro


	def make_df_data(self, data):
		df_data = []
		for item in data:
			lat, lon, dt_str, name = item
			data_entry = {"lat": lat, "lon": lon, "dt_str":dt_str, "name": name}
			df_data.append(data_entry)
		return df_data



##############
# MAIN CLASS #
##############

#Main GTK Window
# class mainWindow:
# 	def __init__(self):
#
# 		#gtktopwindow
# 		self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
# 		self.window.connect("destroy", lambda w: Gtk.main_quit())
# 		self.window.set_title("OpenAstro.org")
# 		self.window.set_icon_from_file(cfg.iconWindow)
# 		self.window.maximize()
#
# 		self.vbox = Gtk.VBox()
#
# 		#uimanager
# 		self.uimanager = Gtk.UIManager()
# 		self.ui_mid = self.uimanager.add_ui_from_file(cfg.xml_ui)
# 		accelgroup = self.uimanager.get_accel_group()
# 		self.window.add_accel_group(accelgroup)
#
# 		#actions definitions
# 		self.actions = [('File', None, _('Chart') ),
# 								('Quit', Gtk.STOCK_QUIT, _("Quit!"), None,'Quit the Program', self.quit_cb),
# 	                     ('History', None, _('History') ),
# 	                     ('newChart', Gtk.STOCK_NEW, _('New Chart'), None, 'New Chart', self.eventDataNew ),
# 	                     ('importXML', Gtk.STOCK_OPEN, _('Open Chart'), None, 'Open Chart', self.doImport ),
# 	                     ('exportXML', Gtk.STOCK_SAVE, _('Save Chart'), None, 'Save Chart', self.doExport ),
# 	                     ('export', Gtk.STOCK_SAVE_AS, _('Save as') ),
# 	                     ('exportPNG', None, _('PNG Image'), None, 'PNG Image', self.doExport ),
# 	                     ('exportSVG', None, _('SVG Image'), None, 'SVG Image', self.doExport ),
# 	                     ('exportJPG', None, _('JPG Image'), None, 'JPG Image', self.doExport ),
# 	                     ('exportPDF', None, _('PDF File'), None, 'PDF File', self.doPrint ),
# 	                     ('import', None, _('Import') ),
# 	                     ('importOroboros', None, _('Oroboros (*.xml)'), None, 'Oroboros (*.xml)', self.doImport ),
# 	                     ('importAstrolog32', None, _('Astrolog (*.dat)'), None, 'Astrolog (*.dat)', self.doImport ),
# 	                     ('importSkylendar', None, _('Skylendar (*.skif)'), None, 'Skylendar (*.skif)', self.doImport ),
# 	                     ('importZet8', None, _('Zet8 Dbase (*.zbs)'), None, 'Zet8 Dbase (*.zbs)', self.doImport ),
# 	                     ('Event', None, _('Event') ),
# 	                     ('EditEvent', Gtk.STOCK_EDIT, _('Edit Event'), None, 'Event Data', self.eventData ),
# 	                     ('OpenDatabase', Gtk.STOCK_HARDDISK, _('Open Database'), None, 'Open Database', self.openDatabase ),
# 								('QuickOpenDatabase', None, _('Quick Open Database') ),
# 	                     ('OpenDatabaseFamous', Gtk.STOCK_HARDDISK, _('Open Famous People Database'), None, 'Open Database Famous', self.openDatabaseFamous ),
# 	                     ('Settings', None, _('Settings') ),
# 	                     ('Special', None, _('Chart Type') ),
# 	                     ('ZoomRadio', None, _('Zoom') ),
# 								('Planets', None, _('Planets & Angles'), None, 'Planets & Angles', self.settingsPlanets ),
# 								('Aspects', None, _('Aspects'), None, 'Aspects', self.settingsAspects ),
# 								('Colors', None, _('Colors'), None, 'Colors', self.settingsColors ),
# 								('Labels', None, _('Labels'), None, 'Labels', self.settingsLabel ),
# 								('Location', Gtk.STOCK_HOME, _('Set Home Location'), None, 'Set Location', self.settingsLocation ),
# 								('Configuration', Gtk.STOCK_PREFERENCES, _('Configuration'), None, 'Configuration', self.settingsConfiguration ),
# 								('Radix', None, _('Radix Chart'), None, 'Transit Chart', self.specialRadix ),
# 								('Transit', None, _('Transit Chart'), None, 'Transit Chart', self.specialTransit ),
# 								('Synastry', None, _('Synastry Chart'), None, 'Synastry Chart...', lambda w: self.openDatabaseSelect(_("Select for Synastry"),"Synastry") ),
# 								('Composite', None, _('Composite Chart'), None, 'Composite Chart...', lambda w: self.openDatabaseSelect(_("Select for Composite"),"Composite") ),
# 								('Combine', None, _('Combine Chart'), None, 'Combine Chart...', lambda w: self.openDatabaseSelect(_("Select for Combine"),"Combine") ),
# 								('Solar', None, _('Solar Return'), None, 'Solar Return...', self.specialSolar ),
# 								('SProgression', None, _('Secondary Progressions'), None, 'Secondary Progressions...', self.specialSProgression ),
# 								('Tables', None, _('Tables') ),
# 								('MonthlyTimeline', None, _('Monthly Timeline 1'), None, 'Monthly Timeline 1', self.tableMonthlyTimeline ),
# 								('MonthlyTimeline2', None, _('Monthly Timeline2'), None, 'Monthly Timeline2', self.tableMonthlyTimeline2 ),
# 								('CuspAspects', None, _('Cusp Aspects'), None, 'Cusp Aspects', self.tableCuspAspects ),
# 								('Extra', None, _('Extra') ),
# 								('exportDB', None, _('Export Database'), None, 'Export Database', self.extraExportDB ),
# 								('importDB', None, _('Import Database'), None, 'Import Database', self.extraImportDB ),
# 								('About', None, _('About') ),
# 								('AboutInfo', Gtk.STOCK_INFO, _('Info'), None, 'Info', self.aboutInfo )  ,
# 	                     ('AboutSupport', Gtk.STOCK_HELP, _('Support'), None, 'Support', lambda w: webbrowser.open_new('http://www.openastro.org/?Support') )
# 	                     ]
#
# 		#update UI
# 		self.updateUI()
#
# 		# Create a MenuBar
# 		menubar = self.uimanager.get_widget('/MenuBar')
# 		self.vbox.pack_start(menubar, expand=False, fill=True, padding=0)
#
# 		#make first SVG
# 		self.tempfilename = openAstro.makeSVG()
#
# 		# Draw svg pixbuf
# 		self.draw = drawSVG()
# 		self.draw.setSVG(self.tempfilename)
# 		scrolledwindow = Gtk.ScrolledWindow()
# 		scrolledwindow.add_with_viewport(self.draw)
# 		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
# 		self.vbox.pack_start(scrolledwindow, expand=True, fill=True, padding=0)
#
# 		self.window.add(self.vbox)
# 		self.window.show_all()
#
# 		#check if we need to ask for location
# 		if openAstro.ask_for_home:
# 			self.settingsLocation(self.window)
#
# 		#check internet connection
# 		self.checkInternetConnection()
#
# 		return
#
# 	"""
#
# 	'Extra' Menu Items Functions
#
# 	extraExportDB
# 	extraImportDB
#
# 	"""
#
# 	def extraExportDB(self, widget):
# 		chooser = Gtk.FileChooserDialog(parent=self.window, title=None,action=Gtk.FileChooserAction.SAVE,
#                                   buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
# 		chooser.set_current_folder(cfg.homedir)
# 		chooser.set_current_name('openastro-database.sql')
# 		filter = Gtk.FileFilter()
# 		filter.set_name(_("OpenAstro.org Databases (*.sql)"))
# 		filter.add_pattern("*.sql")
# 		chooser.add_filter(filter)
# 		response = chooser.run()
#
# 		if response == Gtk.ResponseType.OK:
# 			copyfile(cfg.peopledb, chooser.get_filename())
#
# 		elif response == Gtk.ResponseType.CANCEL:
# 					dprint('Dialog closed, no files selected')
# 		chooser.destroy()
#
# 	def extraImportDB(self, widget):
# 		chooser = Gtk.FileChooserDialog(parent=self.window, title=_("Please select database to import"),action=Gtk.FileChooserAction.OPEN,
#                                   buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
# 		chooser.set_current_folder(cfg.homedir)
# 		filter = Gtk.FileFilter()
# 		filter.set_name(_("OpenAstro.org Databases (*.sql)"))
# 		filter.add_pattern("*.sql")
# 		chooser.add_filter(filter)
# 		response = chooser.run()
#
# 		if response == Gtk.ResponseType.OK:
# 			db.databaseMerge(cfg.peopledb,chooser.get_filename())
#
# 		elif response == Gtk.ResponseType.CANCEL:
# 					dprint('Dialog closed, no files selected')
# 		chooser.destroy()
#
# 	"""
#
# 	Function to check if we have an internet connection
# 	for geonames.org geocoder
#
# 	"""
# 	def checkInternetConnection(self):
#
# 		if db.getAstrocfg('use_geonames.org') == "0":
# 			self.iconn = False
# 			dprint('iconn: not using geocoding!')
# 			return
#
# 		#from openastromod import timeoutsocket
# 		#timeoutsocket.setDefaultSocketTimeout(2)
# 		HOST='api.geonames.org'
# 		PORT=80
# 		s = None
#
# 		try:
# 			socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
# 		except socket.error as msg:
# 			self.iconn = False
# 			dprint('iconn: no connection (getaddrinfo)')
# 			return
#
# 		for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
# 			af, socktype, proto, canonname, sa = res
# 			try:
# 				s = socket.socket(af, socktype, proto)
# 			except socket.error as msg:
# 				s = None
# 				continue
# 			try:
# 				s.connect(sa)
# 			except (socket.error, timeoutsocket.Timeout):
# 				s.close()
# 				s = None
# 				continue
# 			break
#
# 		if s is None:
# 			self.iconn = False
# 			dprint('iconn: no connection')
# 		else:
# 			self.iconn = True
# 			dprint('iconn: got connection')
# 			#timeoutsocket.setDefaultSocketTimeout(20)
# 			s.close()
# 		return
#
# 	def zoom(self, action, current):
# 		#check for zoom level
# 		if current.get_name() == 'z80':
# 			openAstro.zoom=0.8
# 		elif current.get_name() == 'z150':
# 			openAstro.zoom=1.5
# 		elif current.get_name() == 'z200':
# 			openAstro.zoom=2
# 		else:
# 			openAstro.zoom=1
#
# 		#redraw svg
# 		openAstro.makeSVG()
# 		self.draw.queue_draw()
# 		self.draw.setSVG(self.tempfilename)
# 		return
#
#
# 	def doExport(self, widget):
#
# 		chooser = Gtk.FileChooserDialog(parent=self.window,title=None,action=Gtk.FileChooserAction.SAVE,
#                                   buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
# 		chooser.set_current_folder(cfg.homedir)
#
#
# 		filter = Gtk.FileFilter()
# 		if widget.get_name() == 'exportPNG':
# 			chooser.set_current_name(openAstro.name+'.png')
# 			filter.set_name(_("PNG Image Files (*.png)"))
# 			filter.add_mime_type("image/png")
# 			filter.add_pattern("*.png")
# 		elif widget.get_name() == 'exportJPG':
# 			chooser.set_current_name(openAstro.name+'.jpg')
# 			filter.set_name(_("JPG Image Files (*.jpg)"))
# 			filter.add_mime_type("image/jpeg")
# 			filter.add_pattern("*.jpg")
# 			filter.add_pattern("*.jpeg")
# 		elif widget.get_name() == 'exportSVG':
# 			chooser.set_current_name(openAstro.name+'.svg')
# 			filter.set_name(_("SVG Image Files (*.svg)"))
# 			filter.add_mime_type("image/svg+xml")
# 			filter.add_pattern("*.svg")
# 		elif widget.get_name() == 'exportXML':
# 			chooser.set_current_name(openAstro.name+'.oac')
# 			filter.set_name(_("OpenAstro Charts (*.oac)"))
# 			filter.add_mime_type("text/xml")
# 			filter.add_pattern("*.oac")
# 		chooser.add_filter(filter)
#
# 		filter = Gtk.FileFilter()
# 		filter.set_name(_("All files (*)"))
# 		filter.add_pattern("*")
# 		chooser.add_filter(filter)
#
# 		response = chooser.run()
#
# 		if response == Gtk.ResponseType.OK:
# 			if widget.get_name() == 'exportSVG':
# 				copyfile(cfg.tempfilename, chooser.get_filename())
# 			elif widget.get_name() == 'exportPNG':
# 				os.system("%s %s %s" % ('convert',cfg.tempfilename,"'"+chooser.get_filename()+"'"))
# 			elif widget.get_name() == 'exportJPG':
# 				os.system("%s %s %s" % ('convert',cfg.tempfilename,"'"+chooser.get_filename()+"'"))
# 			elif widget.get_name() == 'exportXML':
# 				openAstro.exportOAC(chooser.get_filename())
# 		elif response == Gtk.ResponseType.CANCEL:
# 					dprint('Dialog closed, no files selected')
#
# 		chooser.destroy()
# 		return
#
# 	def doImport(self, widget):
#
# 		chooser = Gtk.FileChooserDialog(parent=self.window,title=_('Select file to open'),action=Gtk.FileChooserAction.OPEN,
#                                   buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
# 		chooser.set_current_folder(cfg.homedir)
#
# 		filter = Gtk.FileFilter()
# 		if widget.get_name() == 'importXML':
# 			filter.set_name(_("OpenAstro Charts (*.oac)"))
# 			#filter.add_mime_type("text/xml")
# 			filter.add_pattern("*.oac")
# 		elif widget.get_name() == 'importOroboros':
# 			filter.set_name(_("Oroboros Charts (*.xml)"))
# 			#filter.add_mime_type("text/xml")
# 			filter.add_pattern("*.xml")
# 		elif widget.get_name() == 'importSkylendar':
# 			filter.set_name(_("Skylendar Charts (*.skif)"))
# 			filter.add_pattern("*.skif")
# 		elif widget.get_name() == 'importAstrolog32':
# 			filter.set_name(_("Astrolog32 Charts (*.dat)"))
# 			filter.add_pattern("*.dat")
# 		elif widget.get_name() == 'importZet8':
# 			filter.set_name(_("Zet8 Databases (*.zbs)"))
# 			filter.add_pattern("*.zbs")
# 		chooser.add_filter(filter)
# 		response = chooser.run()
#
# 		if response == Gtk.ResponseType.OK:
# 			if widget.get_name() == 'importXML':
# 				openAstro.importOAC(chooser.get_filename())
# 			elif widget.get_name() == 'importOroboros':
# 				openAstro.importOroboros(chooser.get_filename())
# 			elif widget.get_name() == 'importSkylendar':
# 				openAstro.importSkylendar(chooser.get_filename())
# 			elif widget.get_name() == 'importAstrolog32':
# 				openAstro.importAstrolog32(chooser.get_filename())
# 			elif widget.get_name() == 'importZet8':
# 				openAstro.importZet8(chooser.get_filename())
# 			self.updateChart()
# 		elif response == Gtk.ResponseType.CANCEL:
# 					dprint('Dialog closed, no files selected')
# 		chooser.destroy()
# 		return
#
# 	def specialRadix(self, widget):
# 		openAstro.type="Radix"
# 		openAstro.charttype=openAstro.label["radix"]
# 		openAstro.transit=False
# 		openAstro.makeSVG()
# 		self.draw.queue_draw()
# 		self.draw.setSVG(self.tempfilename)
#
# 	def specialTransit(self, widget):
# 		openAstro.type="Transit"
# 		openAstro.t_geolon=float(openAstro.home_geolon)
# 		openAstro.t_geolat=float(openAstro.home_geolat)
#
# 		now = datetime.datetime.now()
# 		timezone_str = zonetab.nearest_tz(openAstro.t_geolat,openAstro.t_geolon,zonetab.timezones())[2]
# 		#aware datetime object
# 		dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
# 		dt = pytz.timezone(timezone_str).localize(dt_input)
# 		#naive utc datetime object
# 		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()
# 		#transit data
# 		openAstro.t_year=dt_utc.year
# 		openAstro.t_month=dt_utc.month
# 		openAstro.t_day=dt_utc.day
# 		openAstro.t_hour=openAstro.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
# 		openAstro.t_timezone=openAstro.offsetToTz(dt.utcoffset())
# 		openAstro.t_altitude=25
#
# 		#make svg with transit
# 		openAstro.charttype="%s (%s-%02d-%02d %02d:%02d)" % (openAstro.label["transit"],dt.year,dt.month,dt.day,dt.hour,dt.minute)
# 		openAstro.transit=True
# 		openAstro.makeSVG()
# 		self.draw.queue_draw()
# 		self.draw.setSVG(self.tempfilename)
#
# 	def specialSolar(self, widget):
# 		# create a new window
# 		self.win_SS = Gtk.Dialog()
# 		self.win_SS.set_icon_from_file(cfg.iconWindow)
# 		self.win_SS.set_title(_("Select year for Solar Return"))
# 		self.win_SS.connect("delete_event", lambda w,e: self.win_SS.destroy())
# 		self.win_SS.move(150,150)
# 		self.win_SS.set_border_width(5)
# 		self.win_SS.set_size_request(300,100)
#
# 		#create a table
# 		table = Gtk.Table(2, 1, False)
# 		table.set_col_spacings(0)
# 		table.set_row_spacings(0)
# 		table.set_border_width(10)
#
# 		#options
# 		table.attach(Gtk.Label(_("Select year for Solar Return")), 0, 1, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
# 		entry=Gtk.Entry()
# 		entry.set_max_length(4)
# 		entry.set_width_chars(4)
# 		entry.set_text(str(datetime.datetime.now().year))
# 		table.attach(entry, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
#
# 		#make the ui layout with ok button
# 		self.win_SS.vbox.pack_start(table, True, True, 0)
#
# 		#ok button
# 		button = Gtk.Button(stock=Gtk.STOCK_OK)
# 		button.connect("clicked", self.specialSolarSubmit, entry)
# 		button.set_can_default(True)
# 		self.win_SS.action_area.pack_start(button, True, True, 0)
# 		button.grab_default()
#
# 		#cancel button
# 		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
# 		button.connect("clicked", lambda w: self.win_SS.destroy())
# 		self.win_SS.action_area.pack_start(button, True, True, 0)
#
# 		self.win_SS.show_all()
# 		return
#
# 	def specialSolarSubmit(self, widget, entry):
# 		intyear = int(entry.get_text())
# 		openAstro.localToSolar(intyear)
# 		self.win_SS.destroy()
# 		self.updateChart()
# 		return
#
# 	def specialSProgression(self, widget):
# 		# create a new window
# 		self.win_SSP = Gtk.Dialog(parent=self.window)
# 		self.win_SSP.set_icon_from_file(cfg.iconWindow)
# 		self.win_SSP.set_title(_("Enter Date"))
# 		self.win_SSP.connect("delete_event", lambda w,e: self.win_SSP.destroy())
# 		self.win_SSP.move(150,150)
# 		self.win_SSP.set_border_width(5)
# 		self.win_SSP.set_size_request(320,180)
#
# 		#create a table
# 		table = Gtk.Table(1, 4, False)
# 		table.set_col_spacings(0)
# 		table.set_row_spacings(0)
# 		table.set_border_width(10)
#
# 		#options
# 		table.attach(Gtk.Label(_("Select date for Secondary Progression")+":"), 0, 1, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)
# 		hbox = Gtk.HBox(spacing=4)  # pack_start(child, expand=True, fill=True, padding=0)
# 		entry={}
#
# 		hbox.pack_start(Gtk.Label(_('Year')+": "), False, False, 0)
# 		entry['Y']=Gtk.Entry()
# 		entry['Y'].set_max_length(4)
# 		entry['Y'].set_width_chars(4)
# 		entry['Y'].set_text(str(datetime.datetime.now().year))
# 		hbox.pack_start(entry['Y'], False, False, 0)
# 		hbox.pack_start(Gtk.Label(_('Month')+": "), False, False, 0)
# 		entry['M']=Gtk.Entry()
# 		entry['M'].set_max_length(2)
# 		entry['M'].set_width_chars(2)
# 		entry['M'].set_text('%02d'%(datetime.datetime.now().month))
# 		hbox.pack_start(entry['M'], False, False, 0)
# 		hbox.pack_start(Gtk.Label(_('Day')+": "), False, False, 0)
# 		entry['D']=Gtk.Entry()
# 		entry['D'].set_max_length(2)
# 		entry['D'].set_width_chars(2)
# 		entry['D'].set_text(str(datetime.datetime.now().day))
# 		hbox.pack_start(entry['D'], False, False, 0)
# 		table.attach(hbox,0,1,1,2, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)
#
# 		hbox = Gtk.HBox(spacing=4)
# 		hbox.pack_start(Gtk.Label(_('Hour')+": "), False, False, 0)
# 		entry['h']=Gtk.Entry()
# 		entry['h'].set_max_length(2)
# 		entry['h'].set_width_chars(2)
# 		entry['h'].set_text('%02d'%(datetime.datetime.now().hour))
# 		hbox.pack_start(entry['h'], False, False, 0)
# 		hbox.pack_start(Gtk.Label(_('Min')+": "), False, False, 0)
# 		entry['m']=Gtk.Entry()
# 		entry['m'].set_max_length(2)
# 		entry['m'].set_width_chars(2)
# 		entry['m'].set_text('%02d'%(datetime.datetime.now().minute))
# 		hbox.pack_start(entry['m'], False, False, 0)
# 		table.attach(hbox,0,1,2,3, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)
#
# 		#make the ui layout with ok button
# 		self.win_SSP.vbox.pack_start(table, True, True, 0)
#
# 		#ok button
# 		button = Gtk.Button(stock=Gtk.STOCK_OK)
# 		button.connect("clicked", self.specialSProgressionSubmit, entry)
# 		button.set_can_default(True)
# 		self.win_SSP.action_area.pack_start(button, True, True, 0)
# 		button.grab_default()
#
# 		#cancel button
# 		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
# 		button.connect("clicked", lambda w: self.win_SSP.destroy())
# 		self.win_SSP.action_area.pack_start(button, True, True, 0)
#
# 		self.win_SSP.show_all()
# 		return
#
# 	def specialSProgressionSubmit(self, widget, entry):
# 		dt	= datetime.datetime(int(entry['Y'].get_text()),int(entry['M'].get_text()),int(entry['D'].get_text()),int(entry['h'].get_text()),int(entry['m'].get_text()))
# 		openAstro.localToSProgression(dt)
# 		self.win_SSP.destroy()
# 		self.updateChart()
# 		return
#
#
#debug print function
def dprint(str):
	if "--debug" in sys.argv or DEBUG:
		print('%s' % str)

#gtk main

# def main():
#     Gtk.main()
#     return 0

#start the whole bunch

if __name__ == "__main__":
	cfg = openAstroCfg()
	db = openAstroSqlite()
	openAstro = openAstroInstance(db)
	mainWindow()
	main()










