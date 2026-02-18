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

# Basics and standard utilities used across the whole engine.
from typing import Dict, List, Any, Tuple, Optional, Union, Set
import copy
import math, sys, os, os.path, tempfile, gettext, codecs, datetime

# from icalendar import Calendar, Event
import pytz
#from datetime import datetime


#copyfile

#pysqlite
import sqlite3

from openastromod.utils import utc_to_local, local_to_utc, decHour, decHourJoin, offsetToTz, decTzStr, degreeDiff, \
	degreeDiff2, dec2deg, dec2deg_str, get_zodiac_sign
from openastromod.renderer import ChartRenderer
from openastromod.local_space import LocalSpaceMixin
from openastromod.local_to import LocalToMixin

# Register string adapter for sqlite
sqlite3.register_adapter(str, lambda s: s)

#template processing
from string import Template



import json
from pathlib import Path

# Internal OpenAstro modules (core calculation + helpers).
sys.path.append("/usr/lib/python3.5/dist-packages") #trying to 'fix' some problems importing openastromod on some distros
sys.path.append("/usr/lib/python3.5/site-packages") #trying to 'fix' some problems importing openastromod on some distros
from openastromod import zonetab, geoname, importfile, swiss as ephemeris


from skyfield.api import N, E, wgs84

import ephem

import svgwrite

from gettext import gettext as _

import json5

_SETTINGS0_CACHE = None

# Debug/version flags shared by the module.
LOCAL=True
DEBUG=False
VERSION='2.0.0'

# Base data directory resolution (local install first).
if LOCAL:
	DATADIR=os.path.dirname(__file__)
# elif os.path.exists(os.path.join(sys.prefix,'share','openastro.org')):
# 	DATADIR=os.path.join(sys.prefix,'share','openastro.org')
# elif os.path.exists(os.path.join('usr','local','share','openastro.org')):
# 	DATADIR=os.path.join('usr','local','share','openastro.org')
# elif os.path.exists(os.path.join('usr','share','openastro.org')):
# 	DATADIR=os.path.join('usr','share','openastro.org')
else:
	print("Exiting... can't find data directory")
	sys.exit()

# Translation registry for UI labels.
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
			# "nb":"Bokmål",
			# "pl":"język polski",
			"rom":"rromani ćhib",
			"ru":"Русский",
			"es":"Español",
			# "sv":"svenska",
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

	def __init__(self, settings: Dict[str, Any] = {}) -> None:
		# Load base settings, merge with overrides, normalize planet/house blocks,
		# and prepare translation + resource paths.
		self.version = VERSION
		dprint("-------------------------------")
		dprint('  OpenAstro2 ' + str(self.version))
		dprint("-------------------------------")
		# self.homedir = os.path.expanduser("~")

		# check for astrodir
		# self.astrodir = os.path.join(self.homedir, '.openastro.org')
		# if os.path.isdir(self.astrodir) == False:
		# 	os.mkdir(self.astrodir)

		# system tmpdir for generated artifacts
		system_tmp = tempfile.gettempdir()
		self.tmpdir = self._ensure_writable_tmpdir(os.path.join(system_tmp, 'openastro2'))

		# check for swiss local dir
		# self.swissLocalDir = os.path.join(self.astrodir, 'swiss_ephemeris')
		# if os.path.isdir(self.swissLocalDir) == False:
		# 	os.mkdir(self.swissLocalDir)

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
		# icons = os.path.join(DATADIR, 'icons')
		# self.iconWindow = os.path.join(icons, 'openastro.svg')
		# self.iconAspects = os.path.join(icons, 'aspects')

		# basic files
		# self.tempfilename = os.path.join(self.tmpdir, "openAstroChart.svg")
		# self.tempfilenameprint = os.path.join(self.tmpdir, "openAstroChartPrint.svg")
		# self.tempfilenametable = os.path.join(self.tmpdir, "openAstroChartTable.svg")
		# self.tempfilenametableprint = os.path.join(self.tmpdir, "openAstroChartTablePrint.svg")
		self.xml_ui = os.path.join(DATADIR, 'xml/openastro-ui.xml')
		self.xml_svg = os.path.join(DATADIR, 'xml/openastro-svg.xml')
		self.xml_svg2 = os.path.join(DATADIR, 'xml/openastro2-svg.xml')
		self.xml_svg_table = os.path.join(DATADIR, 'xml/openastro-svg-table.xml')

		#------------------------------

		DATADIR = Path(__file__).parent
		json_path = DATADIR / 'settings/settings2.json'
		global _SETTINGS0_CACHE
		if _SETTINGS0_CACHE is None:
			with open(json_path, 'r', encoding='utf-8') as f:
				_SETTINGS0_CACHE = json5.load(f)
		settings0 = copy.deepcopy(_SETTINGS0_CACHE)
		def merge_dicts(dict1, dict2):
			for key, value in dict2.items():
				if isinstance(value, dict):
					# Если значение является словарем, рекурсивно вызываем функцию merge_dicts
					dict1[key] = merge_dicts(dict1.get(key, {}), value)
				else:
					# Иначе перезаписываем значение ключа в dict1 значением из dict2
					dict1[key] = value
			return dict1

		self.settings = merge_dicts(settings0, settings)
		self.settings["settings_aspect_dic"] = self._build_settings_aspect_dic()
		self._normalize_planet_settings()
		self._normalize_house_settings()


		# self.astrocfg = self.settings["astrocfg"]
		# dprint(self.astrocfg)

		# #install language
		self.setLanguage(self.settings["astrocfg"]['language'])
		self.lang_label = LANGUAGES_LABEL

		self.settings_planet = self.settings["settings_planet"]
		self.settings_planet_dict = self.settings["settings_planet_dict"]
		self.settings_house = self.settings.get("settings_house", [])
		self.settings_house_dict = self.settings.get("settings_house_dict", {})
		return


	def read_settings(self, settings_path: str) -> Optional[Dict[str, Any]]:
		# Load external JSON/JSON5 settings file (relative to module root).
		try:
			DATADIR = Path(__file__).parent
			json_path = DATADIR / settings_path
			with open(f'{json_path}', 'r') as file:
				json_data = json5.load(file)
			return json_data
		except FileNotFoundError:
			print(f"File not found: {settings_path}")
			return None
		except json.JSONDecodeError:
			print(f"JSON decoding error in file: {settings_path}")
			return None


	def setLanguage(self, lang: Optional[str] = None) -> None:
		# Attach gettext translation for label strings without installing global _.
		if lang is None or lang == "default":
			self.gettext = TRANSLATION["default"].gettext
			dprint("installing default language")
		else:
			self.gettext = TRANSLATION[lang].gettext
			dprint("installing language (%s)" % (lang))
		return

	def getColors(self) -> Dict[str, Any]:
		# Convenience accessors for UI/settings blocks.
		out = self.settings["color_codes"]
		return out

	def getLabel(self) -> Dict[str, Any]:
		# Convenience accessors for UI/settings blocks.
		out = self.settings["label"]
		return out

	def getSettingsPlanet(self) -> List[Dict[str, Any]]:
		# Return list form of planet settings.
		return self.settings["settings_planet"]

	def getSettingsPlanetDict(self) -> Dict[str, Dict[str, Any]]:
		# Return dict form of planet settings (id->entry).
		return self.settings["settings_planet_dict"]

	def getSettingsHouse(self) -> List[Dict[str, Any]]:
		# Return list form of house settings.
		return self.settings.get("settings_house", [])

	def getSettingsHouseDict(self) -> Dict[str, Dict[str, Any]]:
		# Return dict form of house settings (id->entry).
		return self.settings.get("settings_house_dict", {})


	def getSettingsAspect(self) -> Dict[str, Any]:
		# Return list of aspect definitions.
		dict = self.settings["settings_aspect"]
		return dict

	@property
	def settings_svg(self) -> Dict[str, Any]:
		return self.settings["settings_svg"]

	def sanitize_for_snapshot(self) -> None:
		"""Remove machine-specific paths/fields for regression snapshots."""
		placeholder = "<tmp>"
		sensitive_attrs = (
			"tmpdir",
			"tempfilename",
			"tempfilenameprint",
			"tempfilenametable",
			"tempfilenametableprint",
			"astrodir",
			"homedir",
			"iconWindow",
			"iconAspects",
			"swissLocalDir",
			"xml_ui",
			"xml_svg",
			"xml_svg2",
			"xml_svg_table",
		)

		for attr in sensitive_attrs:
			if hasattr(self, attr):
				setattr(self, attr, placeholder)

		payloads = []
		if isinstance(self.settings, dict):
			payloads.append(self.settings)
		elif hasattr(self, "settings"):
			payloads.append(self.settings.__dict__)
			if hasattr(self.settings, "settings"):
				payloads.append(self.settings.settings)

		for payload in payloads:
			if not isinstance(payload, dict):
				continue
			for attr in sensitive_attrs:
				if attr in payload:
					payload[attr] = placeholder
			payload.pop("settings_planet_dict", None)
			payload.pop("settings_house_dict", None)
			payload.pop("settings_house", None)
			settings_svg = payload.get("settings_svg")
			if isinstance(settings_svg, dict):
				for attr in sensitive_attrs:
					if attr in settings_svg:
						settings_svg[attr] = placeholder
		if hasattr(self, "settings_planet_dict"):
			delattr(self, "settings_planet_dict")
		if hasattr(self, "settings_house_dict"):
			delattr(self, "settings_house_dict")
		if hasattr(self, "settings_house"):
			delattr(self, "settings_house")

	def _ensure_writable_tmpdir(self, preferred: str) -> str:
		# Try preferred tmpdir, then fallback to module-local tmp.
		candidates = [preferred, os.path.join(Path(__file__).parent, 'tmp')]
		for path in candidates:
			try:
				os.makedirs(path, exist_ok=True)
				test_file = os.path.join(path, '.write_test')
				with open(test_file, 'w') as tmp:
					tmp.write('')
				os.remove(test_file)
				return path
			except OSError:
				continue
		return preferred

	def _build_settings_aspect_dic(self) -> Dict[str, Dict[str, Any]]:
		"""Derive the aspect lookup dictionary from the list form stored in JSON."""
		aspect_dic: Dict[str, Dict[str, Any]] = {}
		for aspect in self.settings.get("settings_aspect", []):
			aspect_id = str(aspect.get("id"))
			entry = dict(aspect)
			entry["id"] = aspect_id
			entry["label"] = entry.get("label", f"{entry.get('degree')} gr")
			if "visible_json" not in entry:
				entry["visible_json"] = 1 if entry.get("is_major") == 1 else 0
			aspect_dic[aspect_id] = entry
		return aspect_dic

	def _normalize_planet_settings(self) -> None:
		# Normalize planet list/dict into a consistent dict form.
		self._normalize_settings_block("settings_planet", "settings_planet_dict")

	def _normalize_house_settings(self) -> None:
		# Normalize house list/dict into a consistent dict form.
		self._normalize_settings_block("settings_house", "settings_house_dict")

	def _normalize_settings_block(self, list_key: str, dict_key: str) -> None:
		# Accept either list or dict input and materialize a dict by id.
		ordered_items: List[Tuple[str, Dict[str, Any]]] = []
		list_payload = self.settings.get(list_key)
		if isinstance(list_payload, list) and list_payload:
			for entry in list_payload:
				entry_id = entry.get("id")
				if entry_id is None:
					continue
				ordered_items.append((str(entry_id), entry))
		else:
			dict_payload = self.settings.get(dict_key)
			if isinstance(dict_payload, dict) and dict_payload:
				ordered_items = list(dict_payload.items())

		if not ordered_items:
			self.settings[dict_key] = {}
			self.settings[list_key] = []
			return

		seen: set[str] = set()
		normalized_items: List[Tuple[str, Dict[str, Any]]] = []
		for key, entry in ordered_items:
			entry_id = entry.get("id", key)
			entry_key = str(entry_id if entry_id is not None else key)
			if entry_key in seen:
				entry_key = f"{entry_key}_{len(seen)}"
			seen.add(entry_key)
			normalized_items.append((entry_key, entry))

		self.settings[dict_key] = {key: entry for key, entry in normalized_items}
		self.settings[list_key] = [entry for _, entry in normalized_items]


	def checkSwissEphemeris(self, num: int) -> None:
		# 00 = -01-600
		# 06 = 600 - 1200
		# 12 = 1200 - 1800
		# 18 = 1800 - 2400
		# 24 = 2400 - 3000
		seas = 'ftp://ftp.astro.com/pub/swisseph/ephe/seas_12.se1'
		semo = 'ftp://ftp.astro.com/pub/swisseph/ephe/semo_12.se1'
		sepl = 'ftp://ftp.astro.com/pub/swisseph/ephe/sepl_12.se1'


class openAstro(LocalSpaceMixin, LocalToMixin):
	"""
	Main API: builds events, computes ephemerides, assembles data dicts,
	and renders SVG output for different chart types.
	"""
	ZODIAC_CANONICAL = [
		"Aries",
		"Taurus",
		"Gemini",
		"Cancer",
		"Leo",
		"Virgo",
		"Libra",
		"Scorpio",
		"Sagittarius",
		"Capricorn",
		"Aquarius",
		"Pisces",
	]
	MODULE_BASE_ATTRS = (
		"planets_sign",
		"planets_degree",
		"planets_degree_ut",
		"planets_retrograde",
		"houses_degree",
		"houses_sign",
		"houses_degree_ut",
		"lunar_phase",
	)
	MODULE_EXTENDED_ATTRS = MODULE_BASE_ATTRS + (
		"planet_longitude",
		"planet_latitude",
		"planet_lon_speed",
		"planet_lat_speed",
		"planet_hour_angle",
		"planet_azimuth",
		"planet_true_altitude",
		"planet_apparent_altitude",
	)
	TRANSIT_ATTRS = (
		"planets_sign",
		"planets_degree",
		"planets_degree_ut",
		"planets_retrograde",
		"houses_degree",
		"houses_sign",
		"houses_degree_ut",
		"planet_azimuth",
		"planet_latitude",
		"planet_longitude",
		"planet_lon_speed",
		"planet_lat_speed",
	)

	@staticmethod
	def event(name: str = "Now", year: Union[str, int] = "", month: Union[str, int] = "", day: Union[str, int] = "", hour: Union[str, int] = "", minute: Union[str, int] = "", second: Union[str, int] = "", timezone: Optional[float] = None, location: str = "London", countrycode: str = "", geolat: Optional[float] = None, geolon: Optional[float] = None, altitude: int = 25) -> Dict[str, Any]:
		"""
		Build an event dictionary from explicit date/time and location fields.
		This is the canonical shape used throughout calculation and rendering.
		"""
		event = {}
		geo = None
		if(timezone is None or geolat is None or geolon is None):
			geoname0 = geoname.search(location, countrycode)
			if geoname0 and len(geoname0) > 0:
				geo = geoname0[0]
		if(year=="" and month=="" and day=="" and hour=="" and minute=="" and second==""):
			now = datetime.datetime.now()
			year = now.year
			month = now.month
			day = now.day
			hour = now.hour
			minute = now.minute
			second = now.second

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
			if geo is not None:
				dt = pytz.timezone(geo["timezonestr"]).localize(dt_input)
				# Datetime offset to float in hours
				utc_offset = dt.utcoffset()
				if utc_offset is not None:
					dh = float(utc_offset.days * 24)
					sh = float(utc_offset.seconds / 3600.0)
					event["timezone"] = dh + sh
				else:
					event["timezone"] = 0.0
			else:
				event["timezone"] = 0.0
		if(timezone is None or geolat is None or geolon is None):
			if geo is not None:
				event["geonameid"] = geo["geonameId"]
				event["location"] = geo["name"]
				event["geolat"] = geo["lat"]
				event["geolon"] = geo["lng"]
				event["countrycode"] = geo["countryCode"]
				event["timezonestr"] = geo["timezonestr"]
			else:
				event["location"] = location
				event["geolat"] = 0.0
				event["geolon"] = 0.0
				event["countrycode"] = countrycode
		else:
			event["location"] = location
			event["geolat"] = geolat
			event["geolon"] = geolon
		event["altitude"] = altitude
		return event

	@classmethod
	def event_dt_str(cls, name: str = "Now", dt_str: str = "", dt_str_format: str = "%Y-%m-%d %H:%M:%S", timezone: Union[bool, float] = False, location: str = "London", countrycode: str = "", geolat: Union[bool, float] = False, geolon: Union[bool, float] = False, altitude: int = 25) -> Dict[str, Any]:
		"""
		Parse datetime from string and delegate to event().
		"""
		# date_time_str = '2022-12-01 10:27:03.929149'
		dt = datetime.datetime.strptime(dt_str, dt_str_format)
		year = dt.year
		month = dt.month
		day = dt.day
		hour = dt.hour
		minute = dt.minute
		second = dt.second
		return cls.event(name, year, month, day, hour, minute, second, timezone, location, countrycode, geolat, geolon, altitude)

	@classmethod
	def event_dt(cls, name: str = "Now", dt: Optional[datetime.datetime] = None, timezone: Union[bool, float] = False, location: str = "London", countrycode: str = "", geolat: Union[bool, float] = False, geolon: Union[bool, float] = False, altitude: int = 25) -> Dict[str, Any]:
		"""
		Build event from datetime object (default: now).
		"""
		# date_time_str = '2022-12-01 10:27:03.929149'
		# dt = datetime.datetime.strptime(dt_str, dt_str_format)
		if dt is None:
			dt = datetime.datetime.now()
		year = dt.year
		month = dt.month
		day = dt.day
		hour = dt.hour
		minute = dt.minute
		second = dt.second
		return cls.event(name, year, month, day, hour, minute, second, timezone, location, countrycode, geolat, geolon, altitude)


	def __init__(self, event1: Dict[str, Any], event2: List[Any] = [], type: str = "Radix", settings: Dict[str, Any] = {}, oa_args: Dict[str, Any] = {}, lang: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
		"""
		Initialize settings, normalize input events, and precompute UTC values.
		"""
		if lang is not None:
			settings = copy.deepcopy(settings)
			settings.setdefault("astrocfg", {})
			settings["astrocfg"]["language"] = lang
		self.settings = openAstroSettings(settings=settings)
		if lang is not None:
			self.settings.setLanguage(lang)
			self.settings.settings["astrocfg"]["language"] = lang
		self._init_house_metadata()
		self._renderer = ChartRenderer(self, dprint)

		self.event1 = event1
		self.event2 = event2
		self.type = type
		self.settings.type = type
		self.settings.settings["astrocfg"]['type'] = type
		self.planets_aspects_list: List[Dict[str, Any]] = []
		self.t_planets_aspects_list: List[Dict[str, Any]] = []
		self.aspect_all_str = ""
		self.t_aspect_all_str = ""

		# self.screen_width = 1920
		# self.screen_height = 1080
		# self.screen_width = 1024
		# self.screen_height = 576
		self.screen_width = self.settings.settings["settings_svg"]["screen_width"]
		self.screen_height = self.settings.settings["settings_svg"]["screen_height"]

		self.name = self.event1["name"]
		self.charttype = self.type
		self.year = self.event1["year"]
		self.month = self.event1["month"]
		self.day = self.event1["day"]
		self.h = self.event1["hour"]
		self.m = self.event1["minute"]
		self.s = self.event1["second"]
		self.hour=decHourJoin(self.event1["hour"],self.event1["minute"], self.event1["second"])
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
			# self.t_h = self.event2["hour"]
			# self.t_m = self.event2["minute"]
			# self.t_s = self.event2["second"]
			self.t_hour = decHourJoin(self.event2["hour"], self.event2["minute"], self.event2["second"])
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
			h, m, s = decHour(self.t_hour)
			utc = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			tz = datetime.timedelta(seconds=float(self.t_timezone) * float(3600))
			utc_loc = utc - tz
			self.t_year = utc_loc.year
			self.t_month = utc_loc.month
			self.t_day = utc_loc.day
			self.t_hour = decHourJoin(utc_loc.hour, utc_loc.minute, utc_loc.second)
			self.t_utc_year = utc_loc.year
			self.t_utc_month = utc_loc.month
			self.t_utc_day = utc_loc.day
			self.t_utc_h = utc_loc.hour
			self.t_utc_m = utc_loc.minute
			self.t_utc_s = utc_loc.second

			self.t_h = utc_loc.hour
			self.t_m = utc_loc.minute
			self.t_s = utc_loc.second

			self.dt2_utc = utc_loc



		# OpenAstro1 used UTC time in database
		self.localToUtc()
		#Make locals
		self.utcToLocal()

		#configuration
		#ZOOM 1 = 100%
		self.zoom = self.settings.settings["settings_svg"]["zoom"]

		#12 zodiacs
		self.zodiac = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
		self.zodiac_short = ['Ari','Tau','Gem','Cnc','Leo','Vir','Lib','Sco','Sgr','Cap','Aqr','Psc']
		self.zodiac_color = ['#482900','#6b3d00','#5995e7','#2b4972','#c54100','#2b286f','#69acf1','#ffd237','#ff7200','#863c00','#4f0377','#6cbfff']
		self.zodiac_element = ['fire','earth','air','water','fire','earth','air','water','fire','earth','air','water']
		self.zodiac_hotcold = ['hot','cold', 'hot','cold', 'hot','cold', 'hot','cold', 'hot','cold', 'hot','cold']
		self.zodiac_drywet = ['dry','dry', 'wet','wet', 'dry','dry', 'wet','wet', 'dry','dry', 'wet','wet']
		self.zodiac_quality = ['сardinal','fixed','mutable', 'сardinal','fixed','mutable', 'сardinal','fixed','mutable', 'сardinal','fixed','mutable']
		self.zodiac_yinyang = ['yang','ying', 'yang','ying', 'yang','ying', 'yang','ying', 'yang','ying', 'yang','ying']
		self.zodiac_attention = ['outer','outer', 'inner','inner', 'outer','outer', 'inner','inner', 'outer','outer', 'inner','inner']

		#get color configuration
		# self.colors = self.settings.getColors()
		# self.label = self.settings.getLabel()
		self.oa_args = oa_args
		self.args = args
		self.kwargs = kwargs

		return

	def _copy_module_attrs(self, module_data, attrs, prefix: str = "") -> None:
		for attr in attrs:
			if hasattr(module_data, attr):
				setattr(self, f"{prefix}{attr}", getattr(module_data, attr))

	@property
	def renderer(self) -> ChartRenderer:
		return self._renderer

	def _translate_label(self, text: Optional[str]) -> Optional[str]:
		if text is None:
			return None
		gettext_fn = getattr(self.settings, "gettext", None)
		if callable(gettext_fn):
			return gettext_fn(text)
		return text

	def _planet_label(self, name: str) -> str:
		key = (name or "").strip()
		if not key:
			return key
		if key.isupper():
			return self._translate_label(key) or key
		key_lower = key.lower()
		mapping = {
			"mean node": "Mean Node",
			"true node": "True Node",
			"mean apogee": "Lilith",
			"osc. apogee": "Osc. Lilith",
			"osc apogee": "Osc. Lilith",
			"day pars": "Day Pars",
			"night pars": "Night Pars",
			"marriage pars": "Marriage Pars",
			"asc": "Asc",
			"dsc": "Dsc",
			"mc": "Mc",
			"ic": "Ic",
		}
		msgid = mapping.get(key_lower)
		if msgid is None:
			msgid = " ".join(part.capitalize() for part in key.split(" "))
		return self._translate_label(msgid) or msgid

	def _zodiac_label(self, index: int) -> str:
		if 0 <= index < len(self.ZODIAC_CANONICAL):
			return self._translate_label(self.ZODIAC_CANONICAL[index]) or self.ZODIAC_CANONICAL[index]
		if 0 <= index < len(self.zodiac):
			return self._translate_label(self.zodiac[index]) or self.zodiac[index]
		return ""

	def _aspect_label(self, label: Optional[str]) -> Optional[str]:
		if label is None:
			return None
		return self._translate_label(label) or label

	def _aspect_type_label(self, aspect_type: Optional[str]) -> Optional[str]:
		if aspect_type is None:
			return None
		return self._translate_label(aspect_type) or aspect_type

	def _get_house_settings_with_numbers(self) -> List[Dict[str, Any]]:
		house_list: List[Dict[str, Any]] = []
		for idx, entry in enumerate(self.settings.getSettingsHouse()):
			entry_copy = dict(entry)
			entry_copy["_house_number"] = idx
			house_list.append(entry_copy)
		return house_list

	def _build_body_settings(self) -> List[Dict[str, Any]]:
		def clone_entry(entry: Dict[str, Any], is_house: bool, house_number: Optional[int] = None) -> Dict[str, Any]:
			entry_copy = dict(entry)
			entry_copy["_is_house"] = is_house
			if is_house and house_number is not None:
				entry_copy["_house_number"] = house_number
			return entry_copy

		planet_list = list(self.settings.getSettingsPlanet())
		house_entries: Dict[str, Dict[str, Any]] = {}
		orphan_houses: List[Dict[str, Any]] = []
		for entry in self._get_house_settings_with_numbers():
			entry_id = entry.get("id")
			entry_copy = clone_entry(entry, True)
			if entry_id is None:
				orphan_houses.append(entry_copy)
				continue
			house_entries[str(entry_id)] = entry_copy

		bodies: List[Dict[str, Any]] = []
		for entry in planet_list:
			entry_id = entry.get("id")
			if entry_id is None:
				bodies.append(clone_entry(entry, False))
				continue
			key = str(entry_id)
			if key in house_entries:
				house_info = house_entries.pop(key)
				house_number = house_info.get("_house_number")
				entry_copy = clone_entry(entry, True, house_number)
				entry_copy["_house_entry"] = house_info
				bodies.append(entry_copy)
			else:
				bodies.append(clone_entry(entry, False))

		if house_entries or orphan_houses:
			def parse_id(value: Any) -> Optional[int]:
				try:
					return int(value)
				except (TypeError, ValueError):
					return None

			remaining_entries = list(house_entries.values()) + orphan_houses
			remaining = sorted(
				remaining_entries,
				key=lambda item: (0, parse_id(item.get("id"))) if parse_id(item.get("id")) is not None else (1, item.get("_house_number", 0)),
			)
			for entry in remaining:
				entry_id = parse_id(entry.get("id"))
				entry_copy = clone_entry(entry, True, entry.get("_house_number"))
				if entry_id is None:
					bodies.append(entry_copy)
					continue
				inserted = False
				for idx, current in enumerate(bodies):
					current_id = parse_id(current.get("id"))
					if current_id is None:
						continue
					if current_id > entry_id:
						bodies.insert(idx, entry_copy)
						inserted = True
						break
				if not inserted:
					bodies.append(entry_copy)

		return bodies

	def _init_house_metadata(self) -> None:
		house_list = self._get_house_settings_with_numbers()
		self.house_entries: List[Dict[str, Any]] = house_list
		self.house_id_set: Set[str] = set()
		self.house_index_by_id: Dict[str, int] = {}
		self.house_planet_index_by_number: Dict[int, int] = {}
		for idx, entry in enumerate(house_list):
			entry_id = entry.get("id")
			if entry_id is None:
				continue
			key = str(entry_id)
			self.house_id_set.add(key)
			self.house_index_by_id[key] = idx
		angle_ids = {"23", "26", "29", "32"}
		detected_angles: Set[int] = set()
		for key in angle_ids:
			index_value = self.house_index_by_id.get(key)
			if index_value is not None:
				detected_angles.add(index_value)
		if not detected_angles and house_list:
			detected_angles = {n for n in (0, 1, 2, 3) if n < len(house_list)}
		self.angle_house_numbers: Set[int] = detected_angles

	def _sync_house_indices(self) -> None:
		mapping: Dict[int, int] = {}
		body_lookup: Dict[str, int] = {}
		for idx, entry in enumerate(self.planets):
			entry_id = entry.get("id")
			if entry_id is None:
				continue
			key = str(entry_id)
			body_lookup[key] = idx
			house_number = self.house_index_by_id.get(key)
			if house_number is not None:
				mapping[house_number] = idx
		self.house_planet_index_by_number = mapping
		self.body_index_by_id = body_lookup

	def get_house_planet_index(self, house_number: int) -> Optional[int]:
		return self.house_planet_index_by_number.get(house_number)

	def get_body_index_by_id(self, body_id: Union[int, str]) -> Optional[int]:
		key = str(body_id)
		return getattr(self, "body_index_by_id", {}).get(key)

	def get_house_number_by_id(self, house_id: Union[int, str]) -> Optional[int]:
		return self.house_index_by_id.get(str(house_id))

	def get_house_planet_entry(self, house_number: int) -> Optional[Dict[str, Any]]:
		idx = self.get_house_planet_index(house_number)
		if idx is None:
			return None
		if 0 <= idx < len(self.planets):
			return self.planets[idx]
		return None

	def _house_entry_by_number(self, house_number: int) -> Optional[Dict[str, Any]]:
		if 0 <= house_number < len(self.house_entries):
			return self.house_entries[house_number]
		return None

	def _house_name_by_number(self, house_number: int) -> str:
		entry = self._house_entry_by_number(house_number)
		if entry:
			return entry.get("name", f"House {house_number + 1}")
		return f"House {house_number + 1}"

	def get_house_number_for_index(self, index: int) -> Optional[int]:
		if index < 0 or index >= len(self.planets):
			return None
		entry_id = self.planets[index].get("id")
		if entry_id is None:
			return None
		return self.house_index_by_id.get(str(entry_id))

	def _is_angle_index(self, index: int) -> bool:
		house_number = self.get_house_number_for_index(index)
		return house_number in getattr(self, "angle_house_numbers", set())

	def is_angle_house_number(self, house_number: int) -> bool:
		return house_number in getattr(self, "angle_house_numbers", set())

	def _first_house_planet_index(self) -> int:
		if not hasattr(self, "house_planet_index_by_number") or not self.house_planet_index_by_number:
			return len(getattr(self, "planets", []))
		return min(self.house_planet_index_by_number.values())

	def _refresh_retrograde_flags(self, prefix: str = "") -> None:
		retro_attr = f"{prefix}planets_retrograde"
		speed_attr = f"{prefix}planet_lon_speed"
		retrograde_list = getattr(self, retro_attr, None)
		speed_list = getattr(self, speed_attr, None)
		if not isinstance(retrograde_list, list) or not isinstance(speed_list, list):
			return
		limit = min(len(retrograde_list), len(speed_list))
		for idx in range(limit):
			if idx >= len(self.planets) or self._is_house_index(idx):
				continue
			retrograde_list[idx] = bool(speed_list[idx] < 0)

	def get_house_color(self, house_number: int, default: Optional[str] = None) -> str:
		entry = self.get_house_planet_entry(house_number) or self._house_entry_by_number(house_number)
		if entry and entry.get("color"):
			return entry["color"]
		if default is not None:
			return default
		return self.settings.settings["color_codes"].get('houses_radix_line', "#444444")

	def _apply_house_positions_to_planets(self) -> None:
		houses = getattr(self, "houses_degree_ut", [])
		for house_number, degree in enumerate(houses):
			idx = self.get_house_planet_index(house_number)
			if idx is None:
				continue
			if hasattr(self, "planets_degree_ut") and idx < len(self.planets_degree_ut):
				self.planets_degree_ut[idx] = degree
			if hasattr(self, "planets_degree") and idx < len(self.planets_degree):
				self.planets_degree[idx] = self.houses_degree[house_number]
			if hasattr(self, "planets_sign") and idx < len(self.planets_sign):
				self.planets_sign[idx] = self.houses_sign[house_number]
			if hasattr(self, "planets_retrograde") and idx < len(self.planets_retrograde):
				self.planets_retrograde[idx] = False

	def _is_house_index(self, index: int) -> bool:
		if index < 0 or index >= len(self.planets):
			return False
		return bool(self.planets[index].get("_is_house"))

	@property
	def settings_svg(self) -> Dict[str, Any]:
		if isinstance(self.settings, dict):
			return self.settings.get("settings_svg", {})
		return getattr(self.settings, "settings_svg", getattr(self.settings, "settings", {}).get("settings_svg", {}))

	@property
	def planets_aspects_list_t(self) -> List[Dict[str, Any]]:
		return self.t_planets_aspects_list

	@planets_aspects_list_t.setter
	def planets_aspects_list_t(self, value: List[Dict[str, Any]]) -> None:
		self.t_planets_aspects_list = value

	def sanitize_for_snapshot(self) -> None:
		sensitive_attrs = (
			"tmpdir",
			"tempfilename",
			"tempfilenameprint",
			"tempfilenametable",
			"tempfilenametableprint",
			"astrodir",
			"homedir",
			"iconWindow",
			"iconAspects",
			"swissLocalDir",
		)
		for attr in sensitive_attrs:
			if hasattr(self, attr):
				setattr(self, attr, "<tmp>")
		if hasattr(self, "settings") and hasattr(self.settings, "sanitize_for_snapshot"):
			self.settings.sanitize_for_snapshot()
		if hasattr(self, "settings") and isinstance(self.settings, dict):
			for attr in sensitive_attrs:
				if attr in self.settings:
					self.settings[attr] = "<tmp>"
		ephemeral_attrs = (
			"body_index_by_id",
			"house_entries",
			"house_id_set",
			"house_index_by_id",
			"house_planet_index_by_number",
			"angle_house_numbers",
			"planet_lat_speed",
			"planet_lon_speed",
		)
		for attr in ephemeral_attrs:
			if hasattr(self, attr):
				delattr(self, attr)
		if hasattr(self, "planets"):
			for entry in self.planets:
				if isinstance(entry, dict):
					entry.pop("_house_entry", None)
					entry.pop("_house_number", None)
					entry.pop("_is_house", None)
		if hasattr(self, "_first_house_planet_index"):
			house_start = self._first_house_planet_index()
		else:
			house_start = len(getattr(self, "planets", []))
		if house_start < len(getattr(self, "planets", [])):
			numeric_attrs = (
				"planets_degree_ut",
				"planets_degree",
				"planets_sign",
				"planet_longitude",
				"planet_latitude",
				"planet_lon_speed",
				"planet_lat_speed",
			)
			for attr in numeric_attrs:
				seq = getattr(self, attr, None)
				if not isinstance(seq, list):
					continue
				for idx in range(house_start, len(seq)):
					seq[idx] = idx


	def utcToLocal(self):
		#make local time variables from global UTC
		self.year_loc, self.month_loc, self.day_loc, self.hour_loc, self.minute_loc, self.second_loc \
			= utc_to_local(self.year, self.month, self.day, self.hour, self.timezone)



	def calcAstro( self ):
		"""
		Core calculation pipeline:
		- select chart type,
		- compute ephemerides,
		- populate planetary/house arrays,
		- build dictionary structures.
		"""
		# empty element points
		self.fire = 0.0
		self.earth = 0.0
		self.air = 0.0
		self.water = 0.0

		# get database planet + house settings
		self.planets = self._build_body_settings()
		self._sync_house_indices()

		# get database aspect settings
		self.aspects = self.settings.getSettingsAspect()

		# Combine module data
		if self.type == "Combine":
			# make calculations
			module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			h, m, s = self.decHour(self.t_hour)
			dt_new = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			self.e2_dt_utc = dt_new

		# Direction module data
		elif self.type == "Direction":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self._copy_module_attrs(module_data, self.MODULE_BASE_ATTRS)
			t_module_data = self.localToDirection(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon, self.t_geolat, self.t_altitude)
			# t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
			# 								  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
			# 								  self.settings.settings["astrocfg"])
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")

		elif self.type == "DirectionWithEnd":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			solaryearsecs = 31556925.51  # 365 days, 5 hours, 48 minutes, 45.51 seconds
			h, m, s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)

			dt_end = datetime.datetime.strptime(self.oa_args['dateEndStr'], "%Y-%m-%d %H:%M:%S")
			dt_direction = dt_end - dt_original
			dt_dir_seconds = dt_direction.total_seconds()
			if self.oa_args['DirectionToEndType'] == "to_ic":
				# 90 to IC
				delta_degr = (module_data.houses_degree_ut[3] - module_data.houses_degree_ut[0])
				if(delta_degr < 0):
					delta_degr = 360 + delta_degr
				solaryearsecs = (dt_dir_seconds / delta_degr)
			if self.oa_args['DirectionToEndType'] == "to_ic_back":
				# 90 to IC
				delta_degr = (module_data.houses_degree_ut[3] - module_data.houses_degree_ut[0])
				if(delta_degr > 0):
					delta_degr = delta_degr - 360
				solaryearsecs = (dt_dir_seconds / delta_degr)
			elif self.oa_args['DirectionToEndType'] == "to_mc_forward":
				# 270 to MC
				delta_degr = (module_data.houses_degree_ut[9] - module_data.houses_degree_ut[0])
				if(delta_degr < 0):
					delta_degr = 360 + delta_degr
				solaryearsecs = (dt_dir_seconds / delta_degr)
			elif self.oa_args['DirectionToEndType'] == "to_mc_back":
				# -90 to MC
				delta_degr = (module_data.houses_degree_ut[9] - module_data.houses_degree_ut[0])
				if(delta_degr > 0):
					delta_degr = delta_degr - 360
				solaryearsecs = (dt_dir_seconds / delta_degr)
			elif self.oa_args['DirectionToEndType'] == "360":
				solaryearsecs = 31556925.51/4  # 365 days, 5 hours, 48 minutes, 45.51 seconds
			elif self.oa_args['DirectionToEndType'] == "to_360":
				solaryearsecs =  dt_dir_seconds / 360
			elif self.oa_args['DirectionToEndType'] == "to_90":
				solaryearsecs = dt_dir_seconds / 90
			elif self.oa_args['DirectionToEndType'] == "90":
				solaryearsecs = 31556925.51  # 365 days, 5 hours, 48 minutes, 45.51 seconds

			self._copy_module_attrs(module_data, self.MODULE_BASE_ATTRS)
			t_module_data = self.localToDirectionWithEnd(solaryearsecs, self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon, self.t_geolat, self.t_altitude)
			# t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
			# 								  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
			# 								  self.settings.settings["astrocfg"])
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")


		elif self.type == "DirectionPast":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self._copy_module_attrs(module_data, self.MODULE_BASE_ATTRS)
			self._copy_module_attrs(module_data, ("planet_azimuth", "planet_latitude", "planet_longitude"), prefix="t_")
			t_module_data = self.localToDirectionPast(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon, self.t_geolat, self.t_altitude)
			# t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
			# 								  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
			# 								  self.settings.settings["astrocfg"])
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")

		# DirectionReal module data
		elif self.type == "DirectionRealPast":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToDirectionRealPast(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
			# grab transiting module data
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")
		elif self.type == "DirectionRealFuture":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToDirectionRealFuture(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
			# grab transiting module data
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")
		# Solar module data
		elif self.type == "Solar":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToSolar(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
		elif self.type == "SolarNext":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToSolarNext(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
		elif self.type == "SolarPrev":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToSolarPrev(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
		elif self.type == "SolarNear":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToSolarNear(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
		elif self.type == "NewMoonNext":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToNewMoonNext(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])


		elif self.type == "NewMoonPrev":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToNewMoonPrev(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])


		elif self.type == "FullMoonNext":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToFullMoonNext(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
									self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])


		elif self.type == "FullMoonPrev":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToFullMoonPrev(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
							  self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])


		# Lunar module data
		elif self.type == "Lunar":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToLunar(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
		elif self.type == "AscReturn":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToAscReturn(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])

		elif self.type == "EarthReturn":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToEarthReturn(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											self.t_geolat, self.t_altitude)
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])

		elif self.type == "GeoZodiac":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			self.planets_degree_ut = module_data.planets_degree_ut
			self.localToGeoZodiac()
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])


		elif self.type == "SProgression":
			dt	= datetime.datetime(self.t_year, self.t_month, self.t_day, self.t_h, self.t_m, self.t_s)
			# print (dt)
			self.localToSProgression(dt)
			# module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
			# 								self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
			# 								self.settings.settings["astrocfg"], houses_override=self.houses_override)
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			t_module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
											  self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"], houses_override=self.houses_override)
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")
		elif self.type == "SProgressionPast":
			dt	= datetime.datetime(self.t_year, self.t_month, self.t_day, self.t_h, self.t_m, self.t_s)
			# print (dt)
			self.localToSProgressionPast(dt)
			# module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
			# 								self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
			# 								self.settings.settings["astrocfg"], houses_override=self.houses_override)
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
											self.geolat, self.altitude, self.planets, self.zodiac,
											self.settings.settings["astrocfg"])
			t_module_data = ephemeris.ephData(self.sp_year, self.sp_month, self.sp_day, self.sp_hour, self.sp_geolon,
											  self.sp_geolat, self.sp_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"], houses_override=self.houses_override)
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")

		elif self.type == "FixarPlanetMoment":
			module_data = ephemeris.ephData.ephData_fixar(self, self.year, self.month, self.day, self.hour, self.t_year, self.t_month, self.t_day, self.t_hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"], None)
			self.module_data = module_data
			self.type = "Radix"
		elif self.type == "FixarPlanetRadix":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			self.module_data = module_data
			t_module_data = ephemeris.ephData.ephData_fixar(self, self.year, self.month, self.day, self.hour, self.t_year, self.t_month, self.t_day, self.t_hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"], None)
			self.type = "Transit"

		elif self.type == "FixarPlanetTransit":
			module_data = ephemeris.ephData.ephData_fixar(self, self.year, self.month, self.day, self.hour, self.t_year, self.t_month, self.t_day, self.t_hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"], None)
			self.module_data = module_data
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
			self.type = "Transit"

		elif self.type == "FixarEarthMoment":
			module_data = ephemeris.ephData.ephData_fixar_earth(self, self.year, self.month, self.day, self.hour, self.t_year,
														  self.t_month, self.t_day, self.t_hour, self.geolon,
														  self.geolat,
														  self.altitude, self.planets, self.zodiac,
														  self.settings.settings["astrocfg"], None)
			self.type = "Radix"
		elif self.type == "FixarEarthTransit":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			self.module_data = module_data
			t_module_data = ephemeris.ephData.ephData_fixar_earth(self, self.year, self.month, self.day, self.hour, self.t_year,
														  self.t_month, self.t_day, self.t_hour, self.geolon,
														  self.geolat,
														  self.altitude, self.planets, self.zodiac,
														  self.settings.settings["astrocfg"], None)
			self.type = "Transit"

		elif (self.type == "Zemletochki" or self.type == "ZemletochkiG" or self.type == "Sefarial"
			  or self.type == "ZemletochkiAntis" or self.type == "ZemletochkiGAntis" or self.type == "SefarialAntis"
			  or self.type == "ZemletochkiContrAntis" or self.type == "ZemletochkiGContrAntis" or self.type == "SefarialContrAntis"
		):
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			# if self.kwargs.get("zemletochki_antis", False) == True:
			if self.type == "ZemletochkiContrAntis" or self.type == "ZemletochkiGContrAntis" or self.type == "SefarialContrAntis":
				for i in range(len(module_data.planets_degree_ut)):
					module_data.planets_degree_ut[i] = 360 - module_data.planets_degree_ut[i]
					module_data.planets_sign[i], module_data.planets_degree[i] = get_zodiac_sign(module_data.planets_degree_ut[i])
			elif self.type == "ZemletochkiAntis" or self.type == "ZemletochkiGAntis" or self.type == "SefarialAntis":
				for i in range(len(module_data.planets_degree_ut)):
					module_data.planets_degree_ut[i] = 180 - module_data.planets_degree_ut[i]
					module_data.planets_sign[i], module_data.planets_degree[i] = get_zodiac_sign(module_data.planets_degree_ut[i])

			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
			h, m, s = self.decHour(self.t_hour)
			dt_new = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			self.e2_dt_utc = dt_new
			self.type = "Transit"

		elif self.type == "Transit" or self.type == "Composite":
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			t_module_data = ephemeris.ephData(self.t_year, self.t_month, self.t_day, self.t_hour, self.t_geolon,
											  self.t_geolat, self.t_altitude, self.planets, self.zodiac,
											  self.settings.settings["astrocfg"])
			h, m, s = self.decHour(self.t_hour)
			dt_new = datetime.datetime(self.t_year, self.t_month, self.t_day, h, m, s)
			self.e2_dt_utc = dt_new
		else:
			# make calculations
			module_data = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon, self.geolat,
											self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])

		self.makePlanetNames()

		# Transit module data
		# if self.type == "Transit" or self.type == "Composite":
		if self.type != "Radix":
			# grab transiting module data
			self._copy_module_attrs(t_module_data, self.TRANSIT_ATTRS, prefix="t_")
			self._refresh_retrograde_flags(prefix="t_")
			self.t_makePlanetDict()
			self.makeAspectsTransitTransit()

		# grab normal module data
		self._copy_module_attrs(module_data, self.MODULE_EXTENDED_ATTRS)
		self._refresh_retrograde_flags()
		self.makePlanetDict()

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
				self.houses_sign[i], self.houses_degree[i] = get_zodiac_sign(self.houses_degree_ut[i])

			# new planets
			for i in range(len(self.planets)):
				if self._is_house_index(i):
					break
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
				self.planets_sign[i], self.planets_degree[i] = get_zodiac_sign(self.planets_degree_ut[i])
				self.planets_retrograde[i] = False


	def makePlanetDict(self):
		"""
		Build natal planet/house dictionaries and fill astro_dict["planet_dict"].
		"""
		"""
		Make self.planets_dict for all planets
		And self.houses_dict for all houses
		:return:
		"""
		settings_planet_dict: Dict[str, Dict[str, Any]] = {}
		settings_house_dict: Dict[str, Dict[str, Any]] = {}
		settings_payload = getattr(self, "settings", None)
		if isinstance(settings_payload, dict):
			settings_planet_dict = settings_payload.get("settings_planet_dict", {}) or {}
			settings_house_dict = settings_payload.get("settings_house_dict", {}) or {}
		else:
			settings_planet_dict = getattr(settings_payload, "settings_planet_dict", None) or {}
			if not isinstance(settings_planet_dict, dict):
				settings_planet_dict = getattr(settings_payload, "settings", {}).get("settings_planet_dict", {}) or {}
			settings_house_dict = getattr(settings_payload, "settings_house_dict", None) or {}
			if not isinstance(settings_house_dict, dict):
				settings_house_dict = getattr(settings_payload, "settings", {}).get("settings_house_dict", {}) or {}

		self.planets_dict = {}
		t_planet_dict = {}
		t_house_dict = {}
		existing_astro_dict = getattr(self, "astro_dict", None)
		if isinstance(existing_astro_dict, dict):
			t_planet_dict = existing_astro_dict.get("t_planet_dict", {})
			t_house_dict = existing_astro_dict.get("t_house_dict", {})
		tt_planet_dict = {}
		if isinstance(existing_astro_dict, dict):
			tt_planet_dict = existing_astro_dict.get("tt_planet_dict", {})
		self.astro_dict = {
			"planet_dict": {},
			"house_dict": {},
			"t_planet_dict": t_planet_dict,
			"t_house_dict": t_house_dict,
			"tt_planet_dict": tt_planet_dict,
		}
		self.houses_dict = {}
		self.planets_all_str = ""
		self.houses_all_str = ""
		house_id_set = set()
		house_dict = getattr(self, "settings_house_dict", None)
		if not house_dict:
			settings_payload = getattr(self, "settings", None)
			if isinstance(settings_payload, dict):
				house_dict = settings_payload.get("settings_house_dict", {})
			else:
				house_dict = getattr(settings_payload, "settings_house_dict", {}) if settings_payload is not None else {}
		for key, entry in house_dict.items():
			try:
				house_id_set.add(int(key))
			except (TypeError, ValueError):
				if isinstance(entry, dict) and "id" in entry:
					try:
						house_id_set.add(int(entry["id"]))
					except (TypeError, ValueError):
						pass
		i=0
		hi =0
		# Цикл для заполнения словаря
		for name, sign, degree, degree_ut, retrograde in zip(self.planets_name, self.planets_sign, self.planets_degree, self.planets_degree_ut, self.planets_retrograde):
			translated_name = self._planet_label(name)
			translated_zodiac = self._zodiac_label(self.planets_sign[i])
			retrograde_str = ' retrograde' if self.planets_retrograde[i] else ''
			planets_house = self.get_house_for_planet(degree_ut, self.houses_degree_ut, one_house=True)
			planets_houses = self.get_house_for_planet(degree_ut, self.houses_degree_ut, one_house=False)
			# foreach h in planets_houses:
			if ("planet_in_one_house" in self.settings.settings["astrocfg"] and self.settings.settings["astrocfg"]["planet_in_one_house"] == 1):
				house_name = [self._translate_label(self._house_name_by_number(idx)) for idx in planets_house]
				house_str = ', '.join(house_name)
			else:
				houses_names = [self._translate_label(self._house_name_by_number(idx)) for idx in planets_houses]
				house_str = ', '.join(houses_names)
			planets_position_str = f"{translated_name} {self.dec2deg_str(degree, type='2')} {translated_zodiac} {house_str}{retrograde_str}"
			planet_orb_default = self.getPlanetOrbDefault(i)
			planet_lon_speed = self.planet_lon_speed[i] if hasattr(self, "planet_lon_speed") and i < len(self.planet_lon_speed) else None
			planet_lat_speed = self.planet_lat_speed[i] if hasattr(self, "planet_lat_speed") and i < len(self.planet_lat_speed) else None
			if planet_lon_speed is not None and planet_lat_speed is not None:
				planet_speed = math.hypot(planet_lon_speed, planet_lat_speed)
			else:
				planet_speed = planet_lon_speed if planet_lon_speed is not None else 0
			planet_entry = {
				'planets_name': translated_name,
				'planets_name_raw': name,
				'planets_position_str': planets_position_str,
				'planets_sign': sign,
				'planets_degree': degree,
				'planets_degree_ut': degree_ut,
				'planet_longitude': self.planet_longitude[i] if hasattr(self, "planet_longitude") and i < len(self.planet_longitude) else None,
				'planet_latitude': self.planet_latitude[i] if hasattr(self, "planet_latitude") and i < len(self.planet_latitude) else None,
				'planet_lon_speed': planet_lon_speed,
				'planet_lat_speed': planet_lat_speed,
				'planet_speed': planet_speed,
				'planets_house': planets_house,
				'planets_houses': planets_houses,
				'planets_retrograde': retrograde,
				'planets_zodiac': translated_zodiac,
				'planets_zodiac_raw': self.zodiac[self.planets_sign[i]],
				'planets_zodiac_short': self.zodiac_short[self.planets_sign[i]],
				'planets_zodiac_short_raw': self.zodiac_short[self.planets_sign[i]],
				'planets_zodiac_quality': self._translate_label(self.zodiac_quality[self.planets_sign[i]]),
				'planets_zodiac_hotcold': self._translate_label(self.zodiac_hotcold[self.planets_sign[i]]),
				'planets_zodiac_drywet': self._translate_label(self.zodiac_drywet[self.planets_sign[i]]),
				'planets_zodiac_yinyang': self._translate_label(self.zodiac_yinyang[self.planets_sign[i]]),
				'planets_zodiac_attention': self._translate_label(self.zodiac_attention[self.planets_sign[i]]),
				'planets_id': i,
				'aspects_orbis_planet': planet_orb_default,
			}
			astro_entry = {"planet_type": "planet"}
			for key, value in planet_entry.items():
				if key.startswith("planets_"):
					astro_key = "planet_" + key[len("planets_"):]
				elif key.startswith("aspects_"):
					astro_key = "aspect_" + key[len("aspects_"):]
				else:
					astro_key = key
				astro_entry[astro_key] = value
			if isinstance(self.planets[i], dict) and "aspects" in self.planets[i]:
				astro_entry["aspects"] = self.planets[i]["aspects"]
			self.planets_dict[i] = planet_entry
			planet_id = self.planets[i].get("id", i) if isinstance(self.planets[i], dict) else i
			try:
				planet_id_key = int(planet_id)
			except (TypeError, ValueError):
				planet_id_key = planet_id
			if planet_id_key in house_id_set:
				astro_entry["planet_type"] = "house"
			visible_entry = settings_planet_dict.get(str(planet_id))
			if not isinstance(visible_entry, dict):
				visible_entry = settings_planet_dict.get(planet_id)
			planet_weight = visible_entry.get("weight", 1) if isinstance(visible_entry, dict) else 1
			astro_entry["planet_weight"] = planet_weight
			astro_entry["planet_visible_json"] = 1 if isinstance(visible_entry, dict) and visible_entry.get("visible_json") == 1 else 0
			self.astro_dict["planet_dict"][str(planet_id)] = astro_entry

			if self._is_house_index(i):
				houses_position_str = f"{translated_name} {self.dec2deg_str(degree, type='2')} {translated_zodiac}"
				house_entry = {
					'houses_name': translated_name,
					'houses_name_raw': name,
					'houses_position_str': houses_position_str,
					'houses_sign': sign,
					'houses_degree': degree,
					'houses_degree_ut': degree_ut,
					'houses_retrograde': retrograde,
					'houses_zodiac': translated_zodiac,
					'houses_zodiac_raw': self.zodiac[self.planets_sign[i]],
					'houses_zodiac_short': self.zodiac_short[self.planets_sign[i]],
					'houses_zodiac_short_raw': self.zodiac_short[self.planets_sign[i]],
					'houses_zodiac_quality': self._translate_label(self.zodiac_quality[self.planets_sign[i]]),
					'houses_zodiac_hotcold': self._translate_label(self.zodiac_hotcold[self.planets_sign[i]]),
					'houses_zodiac_drywet': self._translate_label(self.zodiac_drywet[self.planets_sign[i]]),
					'houses_zodiac_yinyang': self._translate_label(self.zodiac_yinyang[self.planets_sign[i]]),
					'houses_zodiac_attention': self._translate_label(self.zodiac_attention[self.planets_sign[i]]),
					'houses_id': hi,
				}
				self.houses_dict[i] = house_entry
				astro_house_entry = {"planet_type": "house"}
				for key, value in house_entry.items():
					if key.startswith("houses_"):
						astro_key = "planet_" + key[len("houses_"):]
					else:
						astro_key = key
					astro_house_entry[astro_key] = value
				house_id = self.planets[i].get("id", hi) if isinstance(self.planets[i], dict) else hi
				astro_house_entry["house_id"] = house_id
				astro_house_entry["house_number"] = hi
				visible_entry = settings_house_dict.get(str(house_id))
				if not isinstance(visible_entry, dict):
					visible_entry = settings_house_dict.get(house_id)
				astro_house_entry["planet_visible_json"] = 1 if isinstance(visible_entry, dict) and visible_entry.get("visible_json") == 1 else 0
				self.astro_dict["house_dict"][str(house_id)] = astro_house_entry
				if ('visible_json' in self.planets[i] and self.planets[i]['visible_json'] == 1):
					self.houses_all_str = self.houses_all_str + houses_position_str + """
"""
				hi += 1
			else:
				# Don't add houses to planets_all_str
				if ('visible_json' in self.planets[i] and self.planets[i]['visible_json'] == 1):
					self.planets_all_str = self.planets_all_str  + planets_position_str + """
"""
			i+=1
		return self.astro_dict

	def t_makePlanetDict(self):
		"""
		Build transit planet/house dictionaries and fill astro_dict["t_planet_dict"].
		"""
		"""
		Make self.planets_dict for all planets
		And self.houses_dict for all houses
		self.t_planets_all_str
		self.t_houses_all_str

		:return:
		"""
		settings_planet_dict: Dict[str, Dict[str, Any]] = {}
		settings_house_dict: Dict[str, Dict[str, Any]] = {}
		settings_payload = getattr(self, "settings", None)
		if isinstance(settings_payload, dict):
			settings_planet_dict = settings_payload.get("settings_planet_dict", {}) or {}
			settings_house_dict = settings_payload.get("settings_house_dict", {}) or {}
		else:
			settings_planet_dict = getattr(settings_payload, "settings_planet_dict", None) or {}
			if not isinstance(settings_planet_dict, dict):
				settings_planet_dict = getattr(settings_payload, "settings", {}).get("settings_planet_dict", {}) or {}
			settings_house_dict = getattr(settings_payload, "settings_house_dict", None) or {}
			if not isinstance(settings_house_dict, dict):
				settings_house_dict = getattr(settings_payload, "settings", {}).get("settings_house_dict", {}) or {}

		self.t_planets_dict = {}
		if not isinstance(getattr(self, "astro_dict", None), dict):
			self.astro_dict = {}
		self.astro_dict.setdefault("t_planet_dict", {})
		self.astro_dict.setdefault("t_house_dict", {})
		self.astro_dict.setdefault("tt_planet_dict", {})
		self.t_houses_dict = {}
		self.t_planets_all_str = ""
		self.t_houses_all_str = ""
		self.t_aspect_all_str = ""
		house_id_set = set()
		house_dict = getattr(self, "settings_house_dict", None)
		if not house_dict:
			settings_payload = getattr(self, "settings", None)
			if isinstance(settings_payload, dict):
				house_dict = settings_payload.get("settings_house_dict", {})
			else:
				house_dict = getattr(settings_payload, "settings_house_dict", {}) if settings_payload is not None else {}
		for key, entry in house_dict.items():
			try:
				house_id_set.add(int(key))
			except (TypeError, ValueError):
				if isinstance(entry, dict) and "id" in entry:
					try:
						house_id_set.add(int(entry["id"]))
					except (TypeError, ValueError):
						pass
		i = 0
		hi = 0
		# Цикл для заполнения словаря
		for name, sign, degree, degree_ut, retrograde in zip(self.planets_name, self.t_planets_sign,
											self.t_planets_degree, self.t_planets_degree_ut,
											self.t_planets_retrograde):
			translated_name = self._planet_label(name)
			translated_zodiac = self._zodiac_label(self.t_planets_sign[i])
			retrograde_str = ' retrograde' if self.t_planets_retrograde[i] else ''
			planets_house = self.get_house_for_planet(degree_ut, self.t_houses_degree_ut, one_house=True)
			planets_houses = self.get_house_for_planet(degree_ut, self.t_houses_degree_ut, one_house=False)
			# foreach h in planets_houses:
			if ("planet_in_one_house" in self.settings.settings["astrocfg"] and self.settings.settings["astrocfg"]["planet_in_one_house"] == 1):
				house_name = [self._translate_label(self._house_name_by_number(idx)) for idx in planets_house]
				house_str = ', '.join(house_name)
			else:
				houses_names = [self._translate_label(self._house_name_by_number(idx)) for idx in planets_houses]
				house_str = ', '.join(houses_names)
			planets_position_str = f"{translated_name} {self.dec2deg_str(degree, type='2')} {translated_zodiac} {house_str}{retrograde_str}"
			planet_orb_default = self.getPlanetOrbDefault(i)
			planet_lon_speed = self.t_planet_lon_speed[i] if hasattr(self, "t_planet_lon_speed") and i < len(self.t_planet_lon_speed) else None
			planet_lat_speed = self.t_planet_lat_speed[i] if hasattr(self, "t_planet_lat_speed") and i < len(self.t_planet_lat_speed) else None
			if planet_lon_speed is not None and planet_lat_speed is not None:
				planet_speed = math.hypot(planet_lon_speed, planet_lat_speed)
			else:
				planet_speed = planet_lon_speed if planet_lon_speed is not None else planet_lat_speed
			planet_entry = {
				'planets_name': translated_name,
				'planets_name_raw': name,
				'planets_position_str': planets_position_str,
				'planets_sign': sign,
				'planets_degree': degree,
				'planets_degree_ut': degree_ut,
				'planet_longitude': self.t_planet_longitude[i] if hasattr(self, "t_planet_longitude") and i < len(self.t_planet_longitude) else None,
				'planet_latitude': self.t_planet_latitude[i] if hasattr(self, "t_planet_latitude") and i < len(self.t_planet_latitude) else None,
				'planet_lon_speed': planet_lon_speed,
				'planet_lat_speed': planet_lat_speed,
				'planet_speed': planet_speed,
				'planets_house': planets_house,
				'planets_houses': planets_houses,
				'planets_retrograde': retrograde,
				'planets_zodiac': translated_zodiac,
				'planets_zodiac_raw': self.zodiac[self.t_planets_sign[i]],
				'planets_zodiac_short': self.zodiac_short[self.t_planets_sign[i]],
				'planets_zodiac_short_raw': self.zodiac_short[self.t_planets_sign[i]],
				'planets_zodiac_quality': self._translate_label(self.zodiac_quality[self.t_planets_sign[i]]),
				'planets_zodiac_hotcold': self._translate_label(self.zodiac_hotcold[self.t_planets_sign[i]]),
				'planets_zodiac_drywet': self._translate_label(self.zodiac_drywet[self.t_planets_sign[i]]),
				'planets_zodiac_yinyang': self._translate_label(self.zodiac_yinyang[self.t_planets_sign[i]]),
				'planets_zodiac_attention': self._translate_label(self.zodiac_attention[self.t_planets_sign[i]]),
				'planets_id': i,
				'aspects_orbis_planet': planet_orb_default,
			}
			astro_entry = {"planet_type": "planet"}
			for key, value in planet_entry.items():
				if key.startswith("planets_"):
					astro_key = "planet_" + key[len("planets_"):]
				elif key.startswith("aspects_"):
					astro_key = "aspect_" + key[len("aspects_"):]
				else:
					astro_key = key
				astro_entry[astro_key] = value
			if isinstance(self.planets[i], dict) and "aspects" in self.planets[i]:
				astro_entry["aspects"] = self.planets[i]["aspects"]
			self.t_planets_dict[i] = planet_entry
			planet_id = self.planets[i].get("id", i) if isinstance(self.planets[i], dict) else i
			try:
				planet_id_key = int(planet_id)
			except (TypeError, ValueError):
				planet_id_key = planet_id
			if planet_id_key in house_id_set:
				astro_entry["planet_type"] = "house"
			visible_entry = settings_planet_dict.get(str(planet_id))
			if not isinstance(visible_entry, dict):
				visible_entry = settings_planet_dict.get(planet_id)
			planet_weight = visible_entry.get("weight", 1) if isinstance(visible_entry, dict) else 1
			astro_entry["planet_weight"] = planet_weight
			astro_entry["planet_visible_json"] = 1 if isinstance(visible_entry, dict) and visible_entry.get("visible_json") == 1 else 0
			self.astro_dict["t_planet_dict"][str(planet_id)] = astro_entry

			if self._is_house_index(i):
				houses_position_str = f"{translated_name} {self.dec2deg_str(degree, type='2')} {translated_zodiac}"
				house_entry = {
					'houses_name': translated_name,
					'houses_name_raw': name,
					'houses_position_str': houses_position_str,
					'houses_sign': sign,
					'houses_degree': degree,
					'houses_degree_ut': degree_ut,
					'houses_retrograde': retrograde,
					'houses_zodiac': translated_zodiac,
					'houses_zodiac_raw': self.zodiac[self.t_planets_sign[i]],
					'houses_zodiac_short': self.zodiac_short[self.t_planets_sign[i]],
					'houses_zodiac_short_raw': self.zodiac_short[self.t_planets_sign[i]],
					'houses_zodiac_quality': self._translate_label(self.zodiac_quality[self.t_planets_sign[i]]),
					'houses_zodiac_hotcold': self._translate_label(self.zodiac_hotcold[self.t_planets_sign[i]]),
					'houses_zodiac_drywet': self._translate_label(self.zodiac_drywet[self.t_planets_sign[i]]),
					'houses_zodiac_yinyang': self._translate_label(self.zodiac_yinyang[self.t_planets_sign[i]]),
					'houses_zodiac_attention': self._translate_label(self.zodiac_attention[self.t_planets_sign[i]]),
					'houses_id': hi,
				}
				self.t_houses_dict[i] = house_entry
				astro_house_entry = {"planet_type": "house"}
				for key, value in house_entry.items():
					if key.startswith("houses_"):
						astro_key = "planet_" + key[len("houses_"):]
					else:
						astro_key = key
					astro_house_entry[astro_key] = value
				house_id = self.planets[i].get("id", hi) if isinstance(self.planets[i], dict) else hi
				astro_house_entry["house_id"] = house_id
				astro_house_entry["house_number"] = hi
				visible_entry = settings_house_dict.get(str(house_id))
				if not isinstance(visible_entry, dict):
					visible_entry = settings_house_dict.get(house_id)
				astro_house_entry["planet_visible_json"] = 1 if isinstance(visible_entry, dict) and visible_entry.get("visible_json") == 1 else 0
				self.astro_dict["t_house_dict"][str(house_id)] = astro_house_entry
				if ('visible_json' in self.planets[i] and self.planets[i]['visible_json'] == 1):
					self.t_houses_all_str = self.t_houses_all_str + houses_position_str + """
"""
				hi += 1
			else:
				# Don't add houses to planets_all_str
				if ('t_visible_json' in self.planets[i] and self.planets[i]['t_visible_json'] == 1):
					self.t_planets_all_str = self.t_planets_all_str + planets_position_str + """
"""
			i += 1
		# Placeholder for natal->transit aspects dict, built in renderer during transit aspects.
		self.planets_dict_t = {}
		return self.astro_dict


	def get_house_for_planet(self, planet_degree, houses_degree_ut, one_house=True):
		"""
        Определяет номер дома для планеты по её координатам.

        :param planet_degree: Координата планеты (от 0 до 360 градусов).
        :param houses_degree_ut: Список координат домов (12 элементов).
        :param one_house: Get only one house.
        :return: Номер дома (1-12).
        """
		houses=[]
		# Дополняем список домов, чтобы удобно обработать переход через 360/0
		extended_houses = houses_degree_ut + [houses_degree_ut[0] + 360]

		# Определяем дом
		for i in range(12):
			# if extended_houses[i] <= planet_degree < extended_houses[i + 1]:
			if self.is_coordinate_within_arc(planet_degree, extended_houses[i], extended_houses[i + 1]):
				if i not in houses:
					houses.append(i)
			# Add orb 5 degree
			if (one_house==False):
				if self.is_coordinate_within_arc((planet_degree + 5)%360 , extended_houses[i], extended_houses[i + 1]):
					if i not in houses:
						houses.append(i)
		return houses


	def is_coordinate_within_arc(self, degree, start_angle, end_angle):
		"""
		Chech that planet is into shotter arc
		:param degree:
		:param start_angle:
		:param end_angle:
		:return:
		"""
		# Normalize all angles to be within 0-360 range
		degree = degree % 360
		start_angle = start_angle % 360
		end_angle = end_angle % 360

		# Ensure start_angle is less than or equal to end_angle
		if start_angle > end_angle:
			# If the arc spans across 0 degrees, adjust the comparison
			return (degree >= start_angle) or (degree <= end_angle)
		else:
			# If the arc does not span across 0 degrees, perform a simple range check
			return start_angle <= degree <= end_angle


	def makePlanetNames(self):
		self.planets_name = [entry.get('name', '') for entry in self.planets]

	def makeTableRecti(self, dt1_str, dt2_str):
		dt1 = datetime.datetime.strptime(dt1_str, "%Y-%m-%d %H:%M:%S")
		dt2 = datetime.datetime.strptime(dt2_str, "%Y-%m-%d %H:%M:%S")
		aspects_id_arr = []
		aspects_dic = []
		dt_str_arr = []

		dt = dt1
		i=0
		doc = svgwrite.Drawing(filename="table.svg")
		while dt <= dt2:
			# aspects_id_arr.append([])
			print(dt.strftime("%Y-%m-%d %H:%M:%S"))
			dt += datetime.timedelta(minutes=1)
			event1 = self.event_dt_str("tmp", dt_str=dt.strftime("%Y-%m-%d %H:%M:%S"), timezone=3, location="СПб",
											geolat=59.871391, geolon=30.332604)
			oa_args = {}
			oa_args['DirectionToEndType'] = "360"
			oa_args['dateEndStr'] = "1990-08-15 09:40:00"
			oa2 = openAstro(event1, self.event2, type="DirectionWithEnd", settings=self.settings.settings, oa_args=oa_args)
			oa2.calcAstro()
			r = self.settings.settings["settings_svg"]["r"]
			self.c3 = 120
			oa2.makeAspectsTransit(r, (r - self.c3))
			aspects_id_arr.append(oa2.t_planets_aspects_id_arr)
			# print (oa2.t_planets_aspects_id_dic)
			aspects_dic.append(oa2.t_planets_aspects_id_dic)

			# dt_str_arr.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
			dt_str_arr.append(dt.strftime("%H:%M"))
			# print(oa2.planets_degree_ut)
			# print(oa2.t_planets_aspects_arr)
			# print(oa2.t_planets_aspects_id_arr)
			i=i+1
		# print(aspects_id_arr)
		width = 2000
		height = 4000
		row_height = height / (len(aspects_id_arr[0])+1)
		col_width = width / (len(aspects_id_arr)+1)
		doc.add(doc.rect(insert=(0, 0), size=(width, height),  fill="white"))
		# for t in range(len(aspects_id_arr)):
		# 	for i in range(len(aspects_id_arr[0])):
		# 		for j in range(len(aspects_id_arr[0][i])):
		# 			print(aspects_id_arr[t][i][j])
		l = 0
		for t in range(len(aspects_id_arr)):
			x = (t + 1) * col_width
			doc.add(doc.text(dt_str_arr[t], insert=(x + col_width / 2, 0 + row_height / 2)))

		for i in range(len(aspects_id_arr[0])):
			for j in range(len(aspects_id_arr[0][i])):
				y = (l+1) * row_height
				# print(aspects_id_arr[t][i][j])
				flag_asp = False
				for t in range(len(aspects_id_arr)):
					if(aspects_id_arr[t][i][j] != ""):
						flag_asp = True
						# print (self.settings.settings["settings_aspect_dic"][aspects_id_arr[t][i][j]]['name'])
						aspect_id = self.settings.settings["settings_aspect_dic"][aspects_id_arr[t][i][j]]['id']
						is_major = self.settings.settings["settings_aspect_dic"][aspects_id_arr[t][i][j]]['is_major']
				if(flag_asp and y<2000 and is_major):
					# str = self._settings_planet_entry(i)['label_short'] + " " + aspects_id_arr[t][i][j] + " " + self._settings_planet_entry(j)['label_short']
					str = self._settings_planet_entry(i)['label_short'] + " " + aspect_id + " " + self._settings_planet_entry(j)['label_short']
					doc.add(doc.text(str, insert=(0 + col_width / 2, y + row_height / 2)))
					l = l + 1
					for t in range(len(aspects_id_arr)):
						x = (t+1) * col_width
						# doc.add(doc.text(aspects_id_arr[t][i][j], insert=(x + col_width / 2, y + row_height / 2)))
						# print (aspects_arr[t][i][j]['delta'])
						# print (t)
						# print (i)
						# print (j)
						# print (aspects_dic[t][i][j])
						doc.add(doc.text(aspects_dic[t][i][j]['delta'], insert=(x + col_width / 2, y + row_height / 2)))
				# doc.rect(x, y, col_width, row_height, fill="white", stroke="black")
				# doc.text(str(aspects_id_arr[t][i]), x + col_width / 2, y + row_height / 2)
				# dwg = svgwrite.Drawing('test.svg', profile='tiny')
				# dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
				# dwg.add(dwg.text('Test', insert=(0, 0.2)))

				# for j in range(len(aspects_id_arr[t][i])):
				# 	print(aspects_id_arr[t][i][j])

		doc.save()

	def makeSVG2(self, printing=None):
		return self.renderer.makeSVG2(printing)

	#draw transit ring
	def transitRing(self, r):
		return self.renderer.transitRing(r)


	def get_chart_start_point(self):
		"""
		Get first point to drow natal chart.
		(Right point of chart = 7th house or zemletyl of zemletochki)
		:return:
		"""
		if (self.settings.type == "Zemletochki" or self.settings.type == "ZemletochkiG" or self.settings.type == "Sefarial"
				or self.settings.type == "ZemletochkiAntis" or self.settings.type == "ZemletochkiGAntis" or self.settings.type == "SefarialAntis"
				or self.settings.type == "ZemletochkiContrAntis" or self.settings.type == "ZemletochkiGContrAntis" or self.settings.type == "SefarialContrAntis"
		):
			return self.t_planets_degree_ut[46]
			# return self.houses_degree_ut[6]
		else:
			return self.houses_degree_ut[6]
	#draw degree ring
	def degreeRing(self, r):
		return self.renderer.degreeRing(r)


	def degreeTransitRing(self, r):
		return self.renderer.degreeTransitRing(r)
	#floating latitude an longitude to string
	def lat2str(self, coord):
		return self.renderer.lat2str(coord)

	def lon2str(self, coord):
		return self.renderer.lon2str(coord)

	# Utility function wrappers - delegate to utils.py functions
	def decHour(self, input: float) -> List[int]:
		return decHour(input)

	def decHourJoin(self, inH: int, inM: int, inS: int) -> float:
		return decHourJoin(inH, inM, inS)

	def offsetToTz(self, dtoffset: datetime.timedelta) -> float:
		return offsetToTz(dtoffset)

	def decTzStr(self, tz: float) -> str:
		return decTzStr(tz)

	def degreeDiff(self, a: Union[int, float], b: Union[int, float]) -> float:
		return degreeDiff(a, b, self.settings.settings["astrocfg"]["round_aspects"] == 1)

	def degreeDiff2(self, a: Union[int, float], b: Union[int, float]) -> float:
		return degreeDiff2(a, b, self.settings.settings["astrocfg"]["round_aspects"] == 1)

	def dec2deg(self, dec: float, type: str = "3") -> str:
		return dec2deg(dec, type)

	def dec2deg_str(self, dec: float, type: str = "3") -> str:
		return dec2deg_str(dec, type)

	#draw svg aspects: ring, aspect ring, degreeA degreeB
	def drawAspect(self, r, ar, degA, degB, color):
		return self.renderer.drawAspect(r, ar, degA, degB, color)

	def sliceToX(self, slice, r, offset):
		return self.renderer.sliceToX(slice, r, offset)

	def sliceToY(self, slice, r, offset):
		return self.renderer.sliceToY(slice, r, offset)

	def zodiacSlice(self, num, r, style, type):
		return self.renderer.zodiacSlice(num, r, style, type)

	def makeZodiac( self , r ):
		return self.renderer.makeZodiac(r)

	def makeHouses( self , r ):
		return self.renderer.makeHouses(r)


	def getPlanetsDegut(self, temp_planets_degree_ut, flag_transit="Radix"):
		"""
		Get planets dict for visible planets.
		Key = degree_ut[i]
		Value = i
		#list of planets sorted by degree

		:param temp_planets_degree_ut:
		:param flag_transit:
		:return:
		"""
		planets_degut={}

		diff=range(len(self.planets))
		for i in range(len(self.planets)):
			if not self._is_house_index(i):  # exclude houses
				if flag_transit=="Transit":
					# if 't_visible' in self.planets[i] and self.planets[i]['t_visible'] == 1:
					# 	# if "visible2" exist and == 0 than pass
					# 	if ("planet_orb" in self.planets[i]
					# 			and "visible2" in self.planets[i]['planet_orb'][self.type]
					# 			and self.planets[i]['planet_orb'][self.type]["visible2"] == 0):
					# 		pass
					# 	else:
					# 		planets_degut[temp_planets_degree_ut[i]]=i
					if (self.ifShowPlanetInTransit(i)):
						planets_degut[temp_planets_degree_ut[i]] = i

				else:
					if self.planets[i]['visible'] == 1:
						planets_degut[temp_planets_degree_ut[i]]=i
		return planets_degut


	def makePlanets( self , r ):
		return self.renderer.makePlanets(r)


	def makePatterns( self ):
		return self.renderer.makePatterns()

	def makeAspects( self , r , ar ):
		"""
		Compute natal-natal aspects and populate planets_dict/astro_dict aspects.
		"""
		out=""
		self._reset_natal_aspect_data()
		self.planets_aspects= {}
		self.planets_aspects_arr = [[[0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.settings.settings["settings_aspect"]))]
		self.planets_aspects_arr_diff = [[[0.0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.settings.settings["settings_aspect"]))]
		for i in range(len(self.planets)):
			self.planets_aspects[i] = {}
			start=self.planets_degree_ut[i]
			# for x in range(i):
			for x in range(len(self.planets)):
				if i == x:
					continue
				self.planets_aspects[i][x] = {}
				end=self.planets_degree_ut[x]
				diff=float(self.degreeDiff(start,end))
				#loop orbs
				if (self.planets[i]['visible_aspect_line'] == 1) & (self.planets[x]['visible_aspect_line'] == 1) & \
					(self.planets[i]['visible'] == 1) & (self.planets[x]['visible'] == 1):
					for z in range(len(self.settings.settings["settings_aspect"])):

						# orb = self.settings.settings["settings_aspect"][z]['orb']
						# orb1 = self.settings.settings["settings_aspect"][z]['orb']
						# orb2 = self.settings.settings["settings_aspect"][z]['orb']
						# if ('planet_orb' in self.planets[i]):
						# 	if (self.type in self.planets[i]['planet_orb']):
						# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
						# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
						# 		aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
						# 		# dprint (aspect)
						# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
						# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
						# if ('planet_orb' in self.planets[x]):
						# 	if (self.type in self.planets[x]['planet_orb']):
						# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
						# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
						# 		aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
						# 		# dprint (aspect)
						# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
						# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
						# orb = max([orb1, orb2])
						# # orb = (orb1 + orb2)/2
						#
						#
						#
						# if	( float(self.settings.settings["settings_aspect"][z]['degree']) - float(orb) ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + float(orb) ):
						if (self.planetsInAspect(diff, z, i, x)):
							#check if we want to display this aspect
							if self.settings.settings["settings_aspect"][z]['visible'] == 1:
								# self.planets_aspects[z][i][x] = 1
								# self.planets_aspects_arr[z][i][x] = 1

								aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
								if ('planet_orb' in self.planets[i] and 'planet_orb' in self.planets[x] ):
									orb1 = self.planets[i]['planet_orb'][self.type][aspect]
									orb2 = self.planets[x]['planet_orb'][self.type][aspect]
									orb = max([orb1, orb2])
								else:
									orb = self.settings.settings["settings_aspect"][z]['orb']

								self.planets_aspects_arr[z][i][x] = orb-abs(float(self.settings.settings["settings_aspect"][z]['degree']) - abs(float(diff)))
								if(i==x):
									self.planets_aspects_arr[z][i][x] = 0
								# out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.planets_degree_ut[x] , self.settings.settings["color_codes"]["aspect_%s" %(self.settings.settings["settings_aspect"][z]['degree'])] )
								out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.planets_degree_ut[x] , self.settings.settings["settings_aspect"][z]['color'] )
								self._record_natal_aspect(i, x, diff, z)

		return out

	def ifShowPlanetInTransit(self, i):
		if 't_visible' in self.planets[i]:
			if self.planets[i]['t_visible'] == 1:
				if ('planet_orb' in self.planets[i] and "visible2" in self.planets[i]['planet_orb'][self.type]):
					if self.planets[i]['planet_orb'][self.type]["visible2"] == 1:
						return True
					else:
						return False
				else: # t_visible = 1 only
					return True
		return False

	def _is_transit_aspect_visible(self, natal_index: int, transit_index: int) -> bool:
		natal_entry = self.planets[natal_index]
		transit_entry = self.planets[transit_index]
		if natal_entry.get("visible", 1) == 1 and transit_entry.get("visible", 1) == 1:
			natal_orb = natal_entry.get("planet_orb", {}).get(self.type, {})
			transit_orb = transit_entry.get("planet_orb", {}).get(self.type, {})
			if natal_orb.get("visible_aspect_line21", 1) == 1 and transit_orb.get("visible_aspect_line12", 1) == 1:
				return True
		return (
			(natal_entry.get("visible") == 1)
			and (transit_entry.get("t_visible", 1) == 1)
			and (natal_entry.get("visible_aspect_line", 1) == 1)
			and (transit_entry.get("visible_aspect_line", 1) == 1)
		)

	def makeAspectsTransit( self , r , ar ):
		"""
		Compute natal-to-transit aspects (event1 vs event2).
		"""
		out = ""
		self._reset_transit_aspect_data()
		self.atgrid=[]
		self.t_planets_aspects_id_arr = []
		self.t_planets_aspects_id_dic = []
		aspect_arr = {}
		self.t_planets_aspects_arr = [[[0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.settings.settings["settings_aspect"]))]
		self.t_planets_aspects_arr_diff = [[[0.0 for x in range(len(self.planets))] for x in range(len(self.planets))] for x in range(len(self.settings.settings["settings_aspect"]))]
		for i in range(len(self.planets)):
			self.t_planets_aspects_id_arr.append([])
			self.t_planets_aspects_id_dic.append([])
			start=self.planets_degree_ut[i]
			for x in range(len(self.planets)):
				self.t_planets_aspects_id_arr[i].append("")
				aspect_arr['id'] = ""
				aspect_arr['delta'] = ""
				self.t_planets_aspects_id_dic[i].append({'id':"", 'delta':""})
				end=self.t_planets_degree_ut[x]
				diff=float(self.degreeDiff(start,end))
				asp_visible = self._is_transit_aspect_visible(i, x)

				if 	asp_visible == True:
					if ('planet_orb' in self.planets[x]):
						if (self.type in self.planets[x]['planet_orb']):
							# if (("visible2" in self.planets[x]['planet_orb'][self.type] and self.planets[x]['planet_orb'][self.type]["visible2"] == 1)):
							if (self.ifShowPlanetInTransit(x)):
								if (1):
									for z in range(len(self.settings.settings["settings_aspect"])):
										#check for personal planets and determine orb
										# if 0 <= i <= 4 or 0 <= x <= 4:
										# 	orb_before = 1.0
										# else:
										# 	orb_before = 2.0
										#
										#
										# orb = self.settings.settings["settings_aspect"][z]['orb']
										# orb1 = self.settings.settings["settings_aspect"][z]['orb']
										# orb2 = self.settings.settings["settings_aspect"][z]['orb']
										# if ('planet_orb' in self.planets[i]):
										# 	if (self.type in self.planets[i]['planet_orb']):
										# 		if ("default" in self.planets[i]['planet_orb'][self.type]):
										# 			orb1 = self.planets[i]['planet_orb'][self.type]["default"]
										# 		aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
										# 		# dprint (aspect)
										# 		if (aspect in self.planets[i]['planet_orb'][self.type]):
										# 			orb1 = self.planets[i]['planet_orb'][self.type][aspect]
										# if ('planet_orb' in self.planets[x]):
										# 	if (self.type in self.planets[x]['planet_orb']):
										# 		if ("default" in self.planets[x]['planet_orb'][self.type]):
										# 			orb2 = self.planets[x]['planet_orb'][self.type]["default"]
										# 		aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
										# 		# dprint (aspect)
										# 		if (aspect in self.planets[x]['planet_orb'][self.type]):
										# 			orb2 = self.planets[x]['planet_orb'][self.type][aspect]
										# orb = max([orb1, orb2])
										# # orb = (orb1 + orb2)/2
										#
										# #check if we want to display this aspect
										# # if	( float(self.settings.settings["settings_aspect"][z]['degree']) - orb_before ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + 1.0 ):
										# if	( float(self.settings.settings["settings_aspect"][z]['degree']) - orb ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + orb ):
										if (self.planetsInAspect(diff, z, i, x)):
											aspect_entry = self.settings.settings["settings_aspect"][z]
											show_aspect = aspect_entry.get("t_visible", aspect_entry.get("visible", 1)) == 1
											if show_aspect:
												# self.planets_aspects[z][i][x] = 1
												# self.planets_aspects_arr[z][i][x] = 1

												aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
												if ('planet_orb' in self.planets[i] and 'planet_orb' in self.planets[x]):
													orb1 = self.planets[i]['planet_orb'][self.type][aspect]
													orb2 = self.planets[x]['planet_orb'][self.type][aspect]
													orb = max([orb1, orb2])
												else:
													orb = self.settings.settings["settings_aspect"][z]['orb']

												self.t_planets_aspects_arr[z][i][x] = orb - abs(
													float(self.settings.settings["settings_aspect"][z]['degree']) - abs(float(diff)))
												# print(self.planets[x]['name'])
												# out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.t_planets_degree_ut[x] , self.settings.settings["color_codes"]["aspect_%s" %(self.settings.settings["settings_aspect"][z]['degree'])] )
												out = out + self.drawAspect( r , ar , self.planets_degree_ut[i] , self.t_planets_degree_ut[x] , self.settings.settings["settings_aspect"][z]['color'] )

												# self.t_planets_aspects_id_arr[z][i] = 1
												self.t_planets_aspects_id_arr[i][x] = self.settings.settings["settings_aspect"][z]['id']
												# aspect_arr['id'] = self.settings.settings["settings_aspect"][z]['id']
												# aspect_arr['delta'] = self.t_planets_aspects_arr[z][i][x]
												# print(aspect_arr['delta'])
												# self.t_planets_aspects_id_dic[i][x] = aspect_arr
												self.t_planets_aspects_id_dic[i][x] = {'id':self.settings.settings["settings_aspect"][z]['id'], 'delta':self.t_planets_aspects_arr[z][i][x]}
												self._record_transit_aspect(i, x, diff, z)
												# print(self.t_planets_aspects_id_dic[i][x])

											#aspect grid dictionary
											if self.settings.settings["settings_aspect"][z]['visible_grid'] == 1:
												self.atgrid.append({})
												# self.atgrid[-1]['p1']=i
												# self.atgrid[-1]['p2']=x
												# self.atgrid[-1]['aid']=z
												# self.atgrid[-1]['diff']=diff
										# self.t_planets_aspects_id_dic[i][x] = aspect_arr
		self._compute_impact_score_for_transit_by_natal()
		return out

	def _reset_natal_aspect_data(self) -> None:
		self.planets_aspects_list = []
		self.aspect_all_str = ""
		if hasattr(self, "planets_dict") and isinstance(self.planets_dict, dict):
			for entry in self.planets_dict.values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)
		if hasattr(self, "houses_dict") and isinstance(self.houses_dict, dict):
			for entry in self.houses_dict.values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)
		if isinstance(getattr(self, "astro_dict", None), dict):
			for entry in self.astro_dict.get("planet_dict", {}).values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)

	def _reset_transit_aspect_data(self) -> None:
		self.t_planets_aspects_list = []
		self.t_aspect_all_str = ""
		if isinstance(getattr(self, "astro_dict", None), dict):
			for entry in self.astro_dict.get("t_planet_dict", {}).values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)
		if hasattr(self, "planets_dict_t") and isinstance(self.planets_dict_t, dict):
			for entry in self.planets_dict_t.values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)

	def _reset_tt_aspect_data(self) -> None:
		if isinstance(getattr(self, "astro_dict", None), dict):
			for entry in self.astro_dict.get("tt_planet_dict", {}).values():
				if isinstance(entry, dict):
					entry.pop("aspects", None)
					entry.pop("planet_impact", None)

	def _ensure_tt_planet_dict(self) -> None:
		if not isinstance(getattr(self, "astro_dict", None), dict):
			return
		tt_planet_dict = self.astro_dict.get("tt_planet_dict")
		if isinstance(tt_planet_dict, dict) and tt_planet_dict:
			return
		tt_planet_dict = {}
		for key, entry in self.astro_dict.get("t_planet_dict", {}).items():
			if isinstance(entry, dict):
				base = dict(entry)
				base.pop("aspects", None)
				base.pop("planet_impact", None)
				tt_planet_dict[key] = base
		self.astro_dict["tt_planet_dict"] = tt_planet_dict

	def _is_tt_aspect_visible(self, i: int, x: int) -> bool:
		p1 = self.planets[i]
		p2 = self.planets[x]
		return (
			p1.get("t_visible", 1) == 1
			and p2.get("t_visible", 1) == 1
			and p1.get("t_visible_json", 1) == 1
			and p2.get("t_visible_json", 1) == 1
			and p1.get("visible_aspect_line", 1) == 1
			and p2.get("visible_aspect_line", 1) == 1
		)

	def makeAspectsTransitTransit(self) -> None:
		"""
		Compute transit-to-transit aspects (event2 vs event2) into tt_planet_dict.
		"""
		self._ensure_tt_planet_dict()
		self._reset_tt_aspect_data()
		if not isinstance(getattr(self, "astro_dict", None), dict):
			return
		astro_tt = self.astro_dict.get("tt_planet_dict", {})
		if not isinstance(astro_tt, dict):
			return
		for i in range(len(self.planets)):
			start = self.t_planets_degree_ut[i]
			for x in range(len(self.planets)):
				if i == x:
					continue
				if not self._is_tt_aspect_visible(i, x):
					continue
				if not self.ifShowPlanetInTransit(i) or not self.ifShowPlanetInTransit(x):
					continue
				end = self.t_planets_degree_ut[x]
				diff = float(self.degreeDiff(start, end))
				for z in range(len(self.settings.settings["settings_aspect"])):
					if not self.planetsInAspect(diff, z, i, x):
						continue
					aspect_entry = self.settings.settings["settings_aspect"][z]
					show_aspect = aspect_entry.get("t_visible", aspect_entry.get("visible", 1)) == 1
					if not show_aspect:
						continue
					aspects_degree_id = aspect_entry["id"]
					aspect_type = aspect_entry.get("type")
					aspect_label = self.settings.settings["settings_aspect_dic"][aspects_degree_id].get("label")
					aspect_label_tr = self._aspect_label(aspect_label)
					aspect_type_tr = self._aspect_type_label(aspect_type)
					planet_name_a = self._planet_label(self.planets[i]["name"])
					planet_name_b = self._planet_label(self.planets[x]["name"])
					aspect_weight = self.settings.settings["settings_aspect_dic"].get(aspects_degree_id, {}).get("weight", 1)
					asp_orb = abs(float(diff - float(aspect_entry["degree"])))
					asp_orb_deg = self.dec2deg_str(asp_orb, type="2")
					orb1, orb2, aspect_orb_default = self.getAspectOrbs(z, i, x)
					aspect_accuracy = None
					aspect_score = None
					if aspect_orb_default and aspect_orb_default != 0:
						aspect_accuracy = asp_orb / aspect_orb_default
						aspect_score = 1 - aspect_accuracy
					settings_payload = getattr(self, "settings", None)
					settings_planet_dict = {}
					if isinstance(settings_payload, dict):
						settings_planet_dict = settings_payload.get("settings_planet_dict", {}) or {}
					else:
						settings_planet_dict = getattr(settings_payload, "settings_planet_dict", None) or {}
						if not isinstance(settings_planet_dict, dict):
							settings_planet_dict = getattr(settings_payload, "settings", {}).get("settings_planet_dict", {}) or {}
					planet_weight1 = self._planet_weight_by_index(settings_planet_dict, i)
					planet_weight2 = self._planet_weight_by_index(settings_planet_dict, x)
					planet_id_a = self._planet_entry_id(i)
					planet_id_b = self._planet_entry_id(x)
					aspect_orbis_score = aspect_score if aspect_score is not None else 0
					aspect_impact = aspect_orbis_score * aspect_weight * planet_weight1 * planet_weight2
					asp_dict_a = {
						"aspect_str": f"{planet_name_a} {aspect_label_tr} {planet_name_b}\n  orb={asp_orb_deg}",
						"planet_name1": planet_name_a,
						"planet_name2": planet_name_b,
						"planet_id1": planet_id_a,
						"planet_id2": planet_id_b,
						"aspect_degree": aspect_entry["degree"],
						"aspect_diff": diff,
						"aspect_orbis": asp_orb,
						"aspect_label": aspect_label_tr,
						"aspect_id": aspects_degree_id,
						"aspect_orbis_calc": aspect_orb_default,
						"aspect_orbis_accuracy": aspect_accuracy,
						"aspect_orbis_score": aspect_score,
						"aspect_orbis_planet": orb2,
						"aspect_orbis_deg": asp_orb_deg,
						"aspect_weight": aspect_weight,
						"aspect_type": aspect_type_tr,
						"aspect_impact": aspect_impact,
					}
					asp_dict_b = dict(asp_dict_a)
					asp_dict_b["aspect_orbis_planet"] = orb1
					asp_dict_b["planet_id1"], asp_dict_b["planet_id2"] = asp_dict_b["planet_id2"], asp_dict_b["planet_id1"]
					asp_dict_b["planet_name1"], asp_dict_b["planet_name2"] = asp_dict_b["planet_name2"], asp_dict_b["planet_name1"]
					asp_dict_b["aspect_str"] = f"{asp_dict_b['planet_name1']} {asp_dict_b['aspect_label']} {asp_dict_b['planet_name2']}\n  orb={asp_orb_deg}"
					planet_key_a = self._planet_entry_key(i)
					planet_key_b = self._planet_entry_key(x)
					if planet_key_a in astro_tt:
						astro_tt[planet_key_a].setdefault("aspects", {})[planet_key_b] = asp_dict_a
						self._accumulate_planet_impact_natal(astro_tt[planet_key_a], aspect_type, asp_dict_a.get("aspect_impact", 0))
					if planet_key_b in astro_tt:
						astro_tt[planet_key_b].setdefault("aspects", {})[planet_key_a] = asp_dict_b
						self._accumulate_planet_impact_natal(astro_tt[planet_key_b], aspect_type, asp_dict_b.get("aspect_impact", 0))


	def _record_natal_aspect(self, a: int, b: int, diff: float, aspect_index: int) -> None:
		"""
		Build aspect payloads and attach them to planet_dict and astro_dict (natal).
		"""
		aspect_entry = self.settings.settings["settings_aspect"][aspect_index]
		aspects_degree_id = aspect_entry['id']
		aspect_weight = self.settings.settings["settings_aspect_dic"].get(aspects_degree_id, {}).get("weight", 1)
		aspect_type = aspect_entry.get('type')
		aspect_label = self.settings.settings["settings_aspect_dic"][aspects_degree_id].get('label')
		aspect_label_tr = self._aspect_label(aspect_label)
		aspect_type_tr = self._aspect_type_label(aspect_type)
		planet_name_a = self._planet_label(self.planets[a]['name'])
		planet_name_b = self._planet_label(self.planets[b]['name'])
		asp_orb = abs(float(diff - float(self.settings.settings["settings_aspect"][aspect_index]['degree'])))
		asp_orb_deg = self.dec2deg_str(asp_orb, type='2')
		asp_str = f"{planet_name_a} {aspect_label_tr} {planet_name_b}\n  orb={asp_orb_deg}"
		orb1, orb2, aspect_orb_default = self.getAspectOrbs(aspect_index, a, b)
		aspect_accuracy = None
		aspect_score = None
		if aspect_orb_default and aspect_orb_default != 0:
			aspect_accuracy = asp_orb / aspect_orb_default
			aspect_score = 1 - aspect_accuracy
		# aspect_impact = aspect_orbis_score * aspect_weight * planet_weight(planet_id1) * planet_weight(planet_id2)
		settings_payload = getattr(self, "settings", None)
		settings_planet_dict = {}
		if isinstance(settings_payload, dict):
			settings_planet_dict = settings_payload.get("settings_planet_dict", {}) or {}
		else:
			settings_planet_dict = getattr(settings_payload, "settings_planet_dict", None) or {}
			if not isinstance(settings_planet_dict, dict):
				settings_planet_dict = getattr(settings_payload, "settings", {}).get("settings_planet_dict", {}) or {}
		planet_weight1 = self._planet_weight_by_index(settings_planet_dict, a)
		planet_weight2 = self._planet_weight_by_index(settings_planet_dict, b)
		planet_id_a = self._planet_entry_id(a)
		planet_id_b = self._planet_entry_id(b)
		aspect_orbis_score = aspect_score if aspect_score is not None else 0
		aspect_impact = aspect_orbis_score * aspect_weight * planet_weight1 * planet_weight2
		asp_dict_a = {
			'aspect_str': asp_str,
			'planet_name1': planet_name_a,
			'planet_name2': planet_name_b,
			'planet_id1': planet_id_a,
			'planet_id2': planet_id_b,
			'aspect_degree': self.settings.settings["settings_aspect"][aspect_index]['degree'],
			'aspect_diff': diff,
			'aspect_orbis': asp_orb,
			'aspect_label': aspect_label_tr,
			'aspect_id': aspects_degree_id,
			'aspect_orbis_calc': aspect_orb_default,
			'aspect_orbis_accuracy': aspect_accuracy,
			'aspect_orbis_score': aspect_score,
			'aspect_orbis_planet': orb2,
			'aspect_orbis_deg': asp_orb_deg,
			'aspect_weight': aspect_weight,
			'aspect_type': aspect_type_tr,
			'aspect_impact': aspect_impact,
		}
		asp_dict_b = dict(asp_dict_a)
		asp_dict_b['aspect_orbis_planet'] = orb1
		asp_dict_b['planet_id1'], asp_dict_b['planet_id2'] = asp_dict_b['planet_id2'], asp_dict_b['planet_id1']
		asp_dict_b['planet_name1'], asp_dict_b['planet_name2'] = asp_dict_b['planet_name2'], asp_dict_b['planet_name1']
		asp_dict_b['aspect_str'] = f"{asp_dict_b['planet_name1']} {asp_dict_b['aspect_label']} {asp_dict_b['planet_name2']}\n  orb={asp_orb_deg}"
		self.planets_aspects_list.append(asp_dict_a)
		if ('visible_json' in self.planets[a] and self.planets[a]['visible_json'] == 1):
			if ('visible_json' in self.planets[b] and self.planets[b]['visible_json'] == 1):
				if ('visible_json' in self.settings.settings["settings_aspect_dic"][aspects_degree_id]
					and self.settings.settings["settings_aspect_dic"][aspects_degree_id]['visible_json'] == 1):
					self.aspect_all_str = self.aspect_all_str + asp_str + """\n"""
		if hasattr(self, "planets_dict") and isinstance(self.planets_dict, dict):
			self.planets_dict.setdefault(a, {}).setdefault('aspects', {})[b] = asp_dict_a
			self.planets_dict.setdefault(b, {}).setdefault('aspects', {})[a] = asp_dict_b
		if isinstance(getattr(self, "astro_dict", None), dict):
			astro_planets = self.astro_dict.get("planet_dict", {})
			planet_key_a = self._planet_entry_key(a)
			planet_key_b = self._planet_entry_key(b)
			visible_pair = self.planet_visible_json(a) == 1 and self.planet_visible_json(b) == 1
			if planet_key_a in astro_planets:
				astro_planets[planet_key_a].setdefault('aspects', {})[planet_key_b] = asp_dict_a
				if visible_pair:
					self._accumulate_planet_impact_natal(astro_planets[planet_key_a], aspect_type, asp_dict_a.get("aspect_impact", 0))
			if planet_key_b in astro_planets:
				astro_planets[planet_key_b].setdefault('aspects', {})[planet_key_a] = asp_dict_b
				if visible_pair:
					self._accumulate_planet_impact_natal(astro_planets[planet_key_b], aspect_type, asp_dict_b.get("aspect_impact", 0))
		# Houses aspects
		if (22 < a and a < 35):
			if hasattr(self, "houses_dict") and isinstance(self.houses_dict, dict):
				self.houses_dict.setdefault(a, {}).setdefault('aspects', {})[b] = asp_dict_a
		if (22 < b and b < 35):
			if hasattr(self, "houses_dict") and isinstance(self.houses_dict, dict):
				self.houses_dict.setdefault(b, {}).setdefault('aspects', {})[a] = asp_dict_b

	def planet_visible_json(self, planet_id: int, use_transit: bool = False) -> int:
		planet_key = planet_id
		if isinstance(getattr(self, "planets", None), list) and 0 <= planet_id < len(self.planets):
			planet = self.planets[planet_id]
			if isinstance(planet, dict):
				planet_key = planet.get("id", planet_id)
		if isinstance(getattr(self, "astro_dict", None), dict):
			planet_bucket = "t_planet_dict" if use_transit else "planet_dict"
			planet_entry = self.astro_dict.get(planet_bucket, {}).get(str(planet_key))
			if isinstance(planet_entry, dict):
				return 1 if planet_entry.get("planet_visible_json") == 1 else 0
		if isinstance(getattr(self, "planets", None), list) and 0 <= planet_id < len(self.planets):
			planet = self.planets[planet_id]
			if isinstance(planet, dict):
				visible_key = "t_visible_json" if use_transit else "visible_json"
				return 1 if planet.get(visible_key) == 1 else 0
		return 0

	def _planet_entry_id(self, planet_index: int) -> Any:
		if isinstance(getattr(self, "planets", None), list) and 0 <= planet_index < len(self.planets):
			planet = self.planets[planet_index]
			if isinstance(planet, dict):
				return planet.get("id", planet_index)
		return planet_index

	def _planet_entry_key(self, planet_index: int) -> str:
		return str(self._planet_entry_id(planet_index))

	def _planet_weight_by_index(self, settings_planet_dict: Dict[str, Dict[str, Any]], planet_index: int) -> float:
		planet_id = self._planet_entry_id(planet_index)
		entry = settings_planet_dict.get(str(planet_id))
		if not isinstance(entry, dict):
			entry = settings_planet_dict.get(planet_id)
		# Fallback for legacy settings where keys match internal indices.
		if not isinstance(entry, dict):
			entry = settings_planet_dict.get(str(planet_index))
		if not isinstance(entry, dict):
			entry = settings_planet_dict.get(planet_index)
		return entry.get("weight", 1) if isinstance(entry, dict) else 1

	def _record_transit_aspect(self, natal_index: int, transit_index: int, diff: float, aspect_index: int) -> None:
		"""
		Build aspect payloads and attach them to transit dicts (natal->transit).
		"""
		aspect_entry = self.settings.settings["settings_aspect"][aspect_index]
		aspects_degree_id = aspect_entry['id']
		aspect_weight = self.settings.settings["settings_aspect_dic"].get(aspects_degree_id, {}).get("weight", 1)
		aspect_type = aspect_entry.get('type')
		aspect_label = self.settings.settings["settings_aspect_dic"][aspects_degree_id].get('label')
		aspect_label_tr = self._aspect_label(aspect_label)
		aspect_type_tr = self._aspect_type_label(aspect_type)
		planet_name_a = self._planet_label(self.planets[natal_index]['name'])
		planet_name_b = self._planet_label(self.planets[transit_index]['name'])
		asp_orb = abs(float(diff - float(self.settings.settings["settings_aspect"][aspect_index]['degree'])))
		asp_orb_deg = self.dec2deg_str(asp_orb, type='2')
		asp_str = f"{planet_name_a} {aspect_label_tr} {planet_name_b} orb={asp_orb_deg}"
		orb1, orb2, aspect_orb_default = self.getAspectOrbs(aspect_index, natal_index, transit_index)
		aspect_accuracy = None
		aspect_score = None
		if aspect_orb_default and aspect_orb_default != 0:
			aspect_accuracy = asp_orb / aspect_orb_default
			aspect_score = 1 - aspect_accuracy
		# aspect_impact = aspect_orbis_score * aspect_weight * planet_weight(planet_id1) * planet_weight(planet_id2)
		settings_payload = getattr(self, "settings", None)
		settings_planet_dict = {}
		if isinstance(settings_payload, dict):
			settings_planet_dict = settings_payload.get("settings_planet_dict", {}) or {}
		else:
			settings_planet_dict = getattr(settings_payload, "settings_planet_dict", None) or {}
			if not isinstance(settings_planet_dict, dict):
				settings_planet_dict = getattr(settings_payload, "settings", {}).get("settings_planet_dict", {}) or {}
		planet_weight1 = self._planet_weight_by_index(settings_planet_dict, natal_index)
		planet_weight2 = self._planet_weight_by_index(settings_planet_dict, transit_index)
		planet_id_natal = self._planet_entry_id(natal_index)
		planet_id_transit = self._planet_entry_id(transit_index)
		aspect_orbis_score = aspect_score if aspect_score is not None else 0
		aspect_impact = aspect_orbis_score * aspect_weight * planet_weight1 * planet_weight2
		asp_dict_a = {
			'aspect_str': asp_str,
			'planet_name1': planet_name_a,
			'planet_name2': planet_name_b,
			'planet_id1': planet_id_natal,
			'planet_id2': planet_id_transit,
			'aspect_degree': self.settings.settings["settings_aspect"][aspect_index]['degree'],
			'aspect_diff': diff,
			'aspect_orbis': asp_orb,
			'aspect_label': aspect_label_tr,
			'aspect_id': aspects_degree_id,
			'aspect_orbis_calc': aspect_orb_default,
			'aspect_orbis_accuracy': aspect_accuracy,
			'aspect_orbis_score': aspect_score,
			'aspect_orbis_planet': orb2,
			'aspect_orbis_deg': asp_orb_deg,
			'aspect_weight': aspect_weight,
			'aspect_type': aspect_type_tr,
			'aspect_impact': aspect_impact,
		}
		asp_dict_b = dict(asp_dict_a)
		asp_dict_b['aspect_orbis_planet'] = orb1
		# asp_dict_b['planet_id1'], asp_dict_b['planet_id2'] = asp_dict_b['planet_id2'], asp_dict_b['planet_id1']
		# asp_dict_b['planet_name1'], asp_dict_b['planet_name2'] = asp_dict_b['planet_name2'], asp_dict_b['planet_name1']
		asp_dict_b['aspect_str'] = f"t.{asp_dict_b['planet_name2']} {asp_dict_b['aspect_label']} n.{asp_dict_b['planet_name1']} orb={asp_orb_deg}"
		self.t_planets_aspects_list.append(asp_dict_a)
		if ('visible_json' in self.planets[natal_index] and self.planets[natal_index]['visible_json'] == 1):
			if ('t_visible_json' in self.planets[transit_index] and self.planets[transit_index]['t_visible_json'] == 1):
				if ('visible_json' in self.settings.settings["settings_aspect_dic"][aspects_degree_id]
					and self.settings.settings["settings_aspect_dic"][aspects_degree_id]['visible_json'] == 1):
					self.t_aspect_all_str = self.t_aspect_all_str + asp_str + """\n"""
		if hasattr(self, "planets_dict") and isinstance(self.planets_dict, dict):
			if not getattr(self, "planets_dict_t", None):
				self.planets_dict_t = {}
				for planet_key, pdata in self.planets_dict.items():
					base = dict(pdata)
					if 'aspects' in base:
						base.pop('aspects')
					self.planets_dict_t[planet_key] = base
			if natal_index in self.planets_dict_t:
				self.planets_dict_t[natal_index].setdefault('aspects', {})[transit_index] = asp_dict_a
		if isinstance(getattr(self, "astro_dict", None), dict):
			astro_transit = self.astro_dict.get("t_planet_dict", {})
			planet_key = self._planet_entry_key(transit_index)
			natal_key = self._planet_entry_key(natal_index)
			if planet_key in astro_transit:
				astro_transit[planet_key].setdefault('aspects', {})[natal_key] = asp_dict_b
				if self.planet_visible_json(natal_index) == 1 and self.planet_visible_json(transit_index, use_transit=True) == 1:
					self._accumulate_planet_impact(astro_transit[planet_key], aspect_type, asp_dict_b.get("aspect_impact", 0))
					impact_target = astro_transit.get(natal_key)
					if isinstance(impact_target, dict):
						self._accumulate_planet_impact1(
							impact_target,
							aspect_type,
							asp_dict_b.get("aspect_impact", 0),
						)

	def _accumulate_planet_impact(self, target: Dict[str, Any], aspect_type: Optional[str], impact: Optional[float]) -> None:
		"""
		Accumulate impact for transit planet entries into planet_impact2.score.
		"""
		impact_bucket = aspect_type if aspect_type in {"tense", "neutral", "harmonious"} else "neutral"
		value = impact or 0
		planet_impact = target.setdefault(
			"planet_impact2",
			{"score": {"tense": 0, "neutral": 0, "harmonious": 0, "all": 0}},
		)
		if "score" not in planet_impact:
			legacy = {
				"tense": planet_impact.get("tense", 0),
				"neutral": planet_impact.get("neutral", 0),
				"harmonious": planet_impact.get("harmonious", 0),
				"all": planet_impact.get("all", 0),
			}
			planet_impact.clear()
			planet_impact["score"] = legacy
		score = planet_impact.setdefault(
			"score",
			{"tense": 0, "neutral": 0, "harmonious": 0, "all": 0},
		)
		score[impact_bucket] = score.get(impact_bucket, 0) + value
		score["all"] = score.get("all", 0) + value

	def _merge_impact_scores(self, base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
		"""
		Merge two impact dictionaries using the domain-specific dominance rules.
		"""
		def normalize(score: Dict[str, float]) -> Dict[str, float]:
			tense = score.get("tense", 0) or 0
			neutral = score.get("neutral", 0) or 0
			harmonious = score.get("harmonious", 0) or 0
			if tense >= harmonious:
				tense = tense + harmonious
				harmonious = 0
			else:
				harmonious = tense + harmonious
				tense = 0
			return {"tense": tense, "neutral": neutral, "harmonious": harmonious}

		# base_norm = normalize(base)
		# extra_norm = normalize(extra)
		base_norm = base
		extra_norm = extra
		tense = base_norm["tense"] + extra_norm["tense"]
		harmonious = base_norm["harmonious"] + extra_norm["harmonious"]
		neutral = base_norm["neutral"] + extra_norm["neutral"]
		return {
			"tense": tense,
			"neutral": neutral,
			"harmonious": harmonious,
			"all": tense + neutral + harmonious,
		}

	def _multiply_impact_scores(self, base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
		"""
		Multiply two impact dictionaries with cross-bucket mapping rules.
		"""
		base_vals = {
			"tense": base.get("tense", 0) or 0,
			"neutral": base.get("neutral", 0) or 0,
			"harmonious": base.get("harmonious", 0) or 0,
		}
		extra_vals = {
			"tense": extra.get("tense", 0) or 0,
			"neutral": extra.get("neutral", 0) or 0,
			"harmonious": extra.get("harmonious", 0) or 0,
		}
		out = {"tense": 0, "neutral": 0, "harmonious": 0}
		for a_key, a_val in base_vals.items():
			for b_key, b_val in extra_vals.items():
				prod = a_val * b_val
				if prod == 0:
					continue
				if a_key == b_key:
					bucket = a_key
				elif (a_key == "tense" and b_key == "neutral") or (a_key == "neutral" and b_key == "tense"):
					bucket = "tense"
				elif (a_key == "tense" and b_key == "harmonious") or (a_key == "harmonious" and b_key == "tense"):
					bucket = "neutral"
				elif (a_key == "harmonious" and b_key == "neutral") or (a_key == "neutral" and b_key == "harmonious"):
					bucket = "harmonious"
				else:
					bucket = a_key
				out[bucket] += prod/3
		return {
			"tense": out["tense"],
			"neutral": out["neutral"],
			"harmonious": out["harmonious"],
			"all": out["tense"] + out["neutral"] + out["harmonious"],
		}

	def _set_planet_impact_sum12(self, transit_entry: Dict[str, Any]) -> None:
		"""
		Sum planet_impact2 and planet_impact1 element-wise into planet_impact_sum12.
		"""
		impact2 = transit_entry.get("planet_impact2", {})
		impact1 = transit_entry.get("planet_impact1", {})
		score2 = impact2.get("score", {}) if isinstance(impact2, dict) else {}
		score1 = impact1.get("score", {}) if isinstance(impact1, dict) else {}
		sum_score = {
			"tense": (score2.get("tense", 0) or 0) + (score1.get("tense", 0) or 0),
			"neutral": (score2.get("neutral", 0) or 0) + (score1.get("neutral", 0) or 0),
			"harmonious": (score2.get("harmonious", 0) or 0) + (score1.get("harmonious", 0) or 0),
		}
		sum_score["all"] = sum_score["tense"] + sum_score["neutral"] + sum_score["harmonious"]
		sum_payload = {"score": sum_score}
		for score_key in (
			"score_sum_natal",
			"score_sum_transit",
			"score_sum_natal_transit",
			"score_mult_natal",
			"score_mult_transit",
			"score_mult_natal_transit",
		):
			score2 = impact2.get(score_key, {}) if isinstance(impact2, dict) else {}
			score1 = impact1.get(score_key, {}) if isinstance(impact1, dict) else {}
			sum_entry = {
				"tense": (score2.get("tense", 0) or 0) + (score1.get("tense", 0) or 0),
				"neutral": (score2.get("neutral", 0) or 0) + (score1.get("neutral", 0) or 0),
				"harmonious": (score2.get("harmonious", 0) or 0) + (score1.get("harmonious", 0) or 0),
			}
			sum_entry["all"] = sum_entry["tense"] + sum_entry["neutral"] + sum_entry["harmonious"]
			sum_payload[score_key] = sum_entry
		transit_entry["planet_impact_sum12"] = sum_payload

	def _compute_impact_score_for_transit_by_natal(self) -> None:
		"""
		Compute score_natal/score_transit/score_natal_transit and their multiplicative variants.
		"""
		astro_dict = getattr(self, "astro_dict", None)
		if not isinstance(astro_dict, dict):
			return
		impact_coef = self.settings.settings.get("astrocfg", {}).get("impact_planet_coef_natal_sum", 1)
		impact_coef_transit = self.settings.settings.get("astrocfg", {}).get("impact_planet_coef_transit_sum", 1)
		natal_planets = astro_dict.get("planet_dict", {})
		transit_planets = astro_dict.get("t_planet_dict", {})
		tt_planets = astro_dict.get("tt_planet_dict", {})
		if not isinstance(natal_planets, dict) or not isinstance(transit_planets, dict):
			return
		for planet_id, transit_entry in transit_planets.items():
			if not isinstance(transit_entry, dict):
				continue
			natal_entry = natal_planets.get(str(planet_id))
			if not isinstance(natal_entry, dict):
				continue
			natal_impact = natal_entry.get("planet_impact", {}).get("score", {})
			if not isinstance(natal_impact, dict):
				natal_impact = {}
			natal_scaled = {
				"tense": (natal_impact.get("tense", 0) or 0) * impact_coef,
				"neutral": (natal_impact.get("neutral", 0) or 0) * impact_coef,
				"harmonious": (natal_impact.get("harmonious", 0) or 0) * impact_coef,
				"all": (natal_impact.get("all", 0) or 0) * impact_coef,
			}
			transit_scaled = {}
			if isinstance(tt_planets, dict):
				tt_entry = tt_planets.get(str(planet_id))
				if isinstance(tt_entry, dict):
					tt_impact = tt_entry.get("planet_impact", {}).get("score", {})
					if not isinstance(tt_impact, dict):
						tt_impact = {}
					transit_scaled = {
						"tense": (tt_impact.get("tense", 0) or 0) * impact_coef_transit,
						"neutral": (tt_impact.get("neutral", 0) or 0) * impact_coef_transit,
						"harmonious": (tt_impact.get("harmonious", 0) or 0) * impact_coef_transit,
						"all": (tt_impact.get("all", 0) or 0) * impact_coef_transit,
					}
			for impact_key in ("planet_impact2", "planet_impact1"):
				impact_entry = transit_entry.get(impact_key)
				if not isinstance(impact_entry, dict):
					continue
				score = impact_entry.get("score", {})
				if not isinstance(score, dict):
					score = {}
				impact_entry["score_sum_natal"] = self._merge_impact_scores(score, natal_scaled)
				impact_entry["score_sum_transit"] = self._merge_impact_scores(score, transit_scaled)
				combined_extra = {
					"tense": (natal_scaled.get("tense", 0) or 0) + (transit_scaled.get("tense", 0) or 0),
					"neutral": (natal_scaled.get("neutral", 0) or 0) + (transit_scaled.get("neutral", 0) or 0),
					"harmonious": (natal_scaled.get("harmonious", 0) or 0) + (transit_scaled.get("harmonious", 0) or 0),
					"all": (natal_scaled.get("all", 0) or 0) + (transit_scaled.get("all", 0) or 0),
				}
				impact_entry["score_sum_natal_transit"] = self._merge_impact_scores(score, combined_extra)
				impact_entry["score_mult_natal"] = self._multiply_impact_scores(score, natal_scaled)
				impact_entry["score_mult_transit"] = self._multiply_impact_scores(score, transit_scaled)
				# impact_entry["score_mult_natal_transit"] = self._multiply_impact_scores(score, combined_extra)
				score_mult_natal_transit = self._merge_impact_scores(impact_entry["score_mult_natal"], impact_entry["score_mult_transit"])
				score_2score = self._multiply_impact_scores(score, score)
				score_mult_natal_transit = self._merge_impact_scores(score_mult_natal_transit,score_2score)
				impact_entry["score_mult_natal_transit"] = score_mult_natal_transit
			self._set_planet_impact_sum12(transit_entry)

	def _accumulate_planet_impact_natal(
		self,
		target: Dict[str, Any],
		aspect_type: Optional[str],
		impact: Optional[float],
	) -> None:
		"""
		Accumulate impact for natal planet entries into planet_impact.score.
		"""
		impact_bucket = aspect_type if aspect_type in {"tense", "neutral", "harmonious"} else "neutral"
		value = impact or 0
		planet_impact = target.setdefault(
			"planet_impact",
			{"score": {"tense": 0, "neutral": 0, "harmonious": 0, "all": 0}},
		)
		score = planet_impact.setdefault(
			"score",
			{"tense": 0, "neutral": 0, "harmonious": 0, "all": 0},
		)
		score[impact_bucket] = score.get(impact_bucket, 0) + value
		score["all"] = score.get("all", 0) + value

	def _accumulate_planet_impact1(
		self,
		target: Dict[str, Any],
		aspect_type: Optional[str],
		impact: Optional[float],
	) -> None:
		"""
		Accumulate impact for planet_impact1.score (transit aspects by target planet).
		"""
		impact_bucket = aspect_type if aspect_type in {"tense", "neutral", "harmonious"} else "neutral"
		value = impact or 0
		planet_impact1 = target.setdefault(
			"planet_impact1",
			{"score": {"tense": 0, "neutral": 0, "harmonious": 0, "all": 0}},
		)
		if "score" not in planet_impact1:
			legacy = {
				"tense": planet_impact1.get("tense", 0),
				"neutral": planet_impact1.get("neutral", 0),
				"harmonious": planet_impact1.get("harmonious", 0),
				"all": planet_impact1.get("all", 0),
			}
			planet_impact1.clear()
			planet_impact1["score"] = legacy
		score = planet_impact1.setdefault(
			"score",
			{"tense": 0, "neutral": 0, "harmonious": 0, "all": 0},
		)
		score[impact_bucket] = score.get(impact_bucket, 0) + value
		score["all"] = score.get("all", 0) + value

	def makeAspectTransitGrid( self , r ):
		return self.renderer.makeAspectTransitGrid(r)

	def makeAspectGrid( self , r ):
		return self.renderer.makeAspectGrid(r)

	def getAspectOrbs(self, aspect_id, p1_id, p2_id):
		"""
		Return per-planet orbs and max orb for a planet pair/aspect.
		Returns (None, None, None) if the aspect should be disabled (orb < 0).
		"""
		z = aspect_id
		i = p1_id
		x = p2_id
		orb_default = self.settings.settings["settings_aspect"][z]['orb']
		orb1 = orb_default
		orb2 = orb_default
		if ('planet_orb' in self.planets[i]):
			if (self.type in self.planets[i]['planet_orb']):
				if ("default" in self.planets[i]['planet_orb'][self.type]):
					orb1 = self.planets[i]['planet_orb'][self.type]["default"]
				aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
				if (aspect in self.planets[i]['planet_orb'][self.type]):
					orb1 = self.planets[i]['planet_orb'][self.type][aspect]
		if ('planet_orb' in self.planets[x]):
			if (self.type in self.planets[x]['planet_orb']):
				if ("default" in self.planets[x]['planet_orb'][self.type]):
					orb2 = self.planets[x]['planet_orb'][self.type]["default"]
				aspect = str(self.settings.settings["settings_aspect"][z]['degree'])
				if (aspect in self.planets[x]['planet_orb'][self.type]):
					orb2 = self.planets[x]['planet_orb'][self.type][aspect]
		if orb1 < 0 or orb2 < 0:
			return None, None, None
		return orb1, orb2, max([orb1, orb2])

	def getAspectOrb(self, aspect_id, p1_id, p2_id):
		"""
		Calculate orb for a planet pair/aspect based on settings and per-planet overrides.
		Returns None if the aspect should be disabled (orb < 0).
		"""
		_, _, orb = self.getAspectOrbs(aspect_id, p1_id, p2_id)
		return orb

	def getPlanetOrbDefault(self, planet_id):
		orb_default = None
		if 'planet_orb' in self.planets[planet_id]:
			if (self.type in self.planets[planet_id]['planet_orb']):
				if ("default" in self.planets[planet_id]['planet_orb'][self.type]):
					orb_default = self.planets[planet_id]['planet_orb'][self.type]["default"]
		if orb_default is None:
			# Fallback: use a neutral default orb from aspect settings.
			orb_default = self.settings.settings["settings_aspect"][0]['orb']
		return orb_default

	def planetsInAspect( self , diff, aspect_id, p1_id, p2_id ):
		# if(p1_id==2 and p2_id==3 and self.settings.settings["settings_aspect"][aspect_id]['degree']==108 ):
		# 	1
		z = aspect_id
		orb = self.getAspectOrb(aspect_id, p1_id, p2_id)
		if orb is None:
			return False

		# check if we want to display this aspect
		# if	( float(self.settings.settings["settings_aspect"][z]['degree']) - orb_before ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + 1.0 ):
		if (float(self.settings.settings["settings_aspect"][z]['degree']) - orb) <= diff <= (float(self.settings.settings["settings_aspect"][z]['degree']) + orb):
			return True
		else:
			return False

	def makeElements( self , r ):
		return self.renderer.makeElements(r)

	def makePlanetGrid( self ):
		return self.renderer.makePlanetGrid()

	def makePlanetGrid_t(self):
		return self.renderer.makePlanetGrid_t()

	def makeHousesGrid( self ):
		return self.renderer.makeHousesGrid()

	def makeHousesGrid_t( self ):
		return self.renderer.makeHousesGrid_t()





#debug print function
def dprint(str):
	if "--debug" in sys.argv or DEBUG:
		print('%s' % str)
