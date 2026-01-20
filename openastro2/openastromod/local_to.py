from __future__ import annotations

import datetime

import ephem
import pytz

from skyfield.api import load, wgs84

from openastromod import swiss as ephemeris
from openastromod.utils import decHour, decHourJoin, local_to_utc


def _dprint(message):
	try:
		from openastro2.openastro2 import dprint as global_dprint
	except ImportError:
		return
	global_dprint(message)


class LocalToMixin:
		def localToUtc(self):
			# OpenAstro1 used UTC time in database
			# make global UTC time variables from local

			self.utc_year, self.utc_month, self.utc_day, self.utc_h, self.utc_m, self.utc_s \
				= local_to_utc(self.year, self.month, self.day, self.hour, self.timezone)

			h, m, s = decHour(self.hour)
			utc = datetime.datetime(self.year, self.month, self.day, h, m, s)
			tz = datetime.timedelta(seconds=float(self.timezone) * float(3600))
			utc_loc = utc - tz
			self.year = utc_loc.year
			self.month = utc_loc.month
			self.day = utc_loc.day
			self.hour = decHourJoin(utc_loc.hour, utc_loc.minute, utc_loc.second)


		def localToDirection(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# newyear = t_year
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
			dt_direction = dt_new - dt_original

			dt_dir_seconds = dt_direction.total_seconds()
			gradus_delta = (dt_dir_seconds / solaryearsecs)

			_dprint(self.planets_degree_ut)
			mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
												self.geolat, self.altitude, self.planets, self.zodiac,
												self.settings.settings["astrocfg"])
			_dprint(mdata.planets_degree_ut)
			for i in range(len(self.planets_degree_ut)):
				mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
				while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
				while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0
				mdata.planet_longitude[i] = mdata.planets_degree_ut[i]

			for i in range(len(self.houses_degree_ut)):
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
				if mdata.houses_degree_ut[i] > 360.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
				elif mdata.houses_degree_ut[i] < 0.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0

			# adjust list index 32 and 33
			for i in range(len(self.planets_degree_ut)):
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

			_dprint(self.planets_degree_ut)
			_dprint(mdata.planets_degree_ut)

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

			self.__class__.transit=False
			_dprint(dt_new)
			return mdata

		def localToDirectionWithEnd(self, solaryearsecs, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# newyear = t_year
			# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
			dt_direction = dt_new - dt_original

			dt_dir_seconds = dt_direction.total_seconds()
			gradus_delta = (dt_dir_seconds / solaryearsecs)

			_dprint(self.planets_degree_ut)
			mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
												self.geolat, self.altitude, self.planets, self.zodiac,
												self.settings.settings["astrocfg"])
			_dprint(mdata.planets_degree_ut)
			for i in range(len(self.planets_degree_ut)):
				mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
				while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
				while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0
				mdata.planet_longitude[i] = mdata.planets_degree_ut[i]

			for i in range(len(self.houses_degree_ut)):
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
				if mdata.houses_degree_ut[i] > 360.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
				elif mdata.houses_degree_ut[i] < 0.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0

			# adjust list index 32 and 33
			for i in range(len(self.planets_degree_ut)):
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

			_dprint(self.planets_degree_ut)
			_dprint(mdata.planets_degree_ut)

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
			self.type = "Direction"

			self.__class__.transit=False
			_dprint(dt_new)
			return mdata
		def localToDirectionPast(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# newyear = t_year
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
			dt_direction = dt_new - dt_original

			dt_dir_seconds = dt_direction.total_seconds()
			gradus_delta = - (dt_dir_seconds / solaryearsecs) # For past change + to -

			_dprint(self.planets_degree_ut)
			mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
												self.geolat, self.altitude, self.planets, self.zodiac,
												self.settings.settings["astrocfg"])
			_dprint(mdata.planets_degree_ut)
			for i in range(len(self.planets_degree_ut)):
				mdata.planets_degree_ut[i] = mdata.planets_degree_ut[i] + gradus_delta
				while ( mdata.planets_degree_ut[i] < 0 ): mdata.planets_degree_ut[i]+=360.0
				while ( mdata.planets_degree_ut[i] > 360.0): mdata.planets_degree_ut[i]-=360.0
				mdata.planet_longitude[i] = mdata.planets_degree_ut[i]

			for i in range(len(self.houses_degree_ut)):
				mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + gradus_delta
				if mdata.houses_degree_ut[i] > 360.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] - 360.0
				elif mdata.houses_degree_ut[i] < 0.0:
					mdata.houses_degree_ut[i] = mdata.houses_degree_ut[i] + 360.0

			# adjust list index 32 and 33
			for i in range(len(self.planets_degree_ut)):
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

			_dprint(self.planets_degree_ut)
			_dprint(mdata.planets_degree_ut)

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

			self.__class__.transit=False
			_dprint(dt_new)
			return mdata

		def localToDirectionRealPast(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# newyear = t_year
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			# solaryearsecs = 31556925.51 *(1 + 20/360 ) # 365 days, 5 hours, 48 minutes, 45.51 seconds
			# solaryearsecs = 31536000
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			print (dt_original)
			print (dt_new)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
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

			self.__class__.transit=False
			_dprint(dt_new)
			return
		def localToDirectionRealFuture(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# newyear = t_year
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			# solaryearsecs = 31556925.51 *(1 + 20/360 ) # 365 days, 5 hours, 48 minutes, 45.51 seconds
			# solaryearsecs = 31536000
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			print (dt_original)
			print (dt_new)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
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

			self.__class__.transit=False
			_dprint(dt_new)
			return

		def localToProgressionReal(self, t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude):

			# # solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			# solaryearsecs = 27.3215817 * 24 * 60 * 60  # 27,3215817 days
			# _dprint("localToSolar: from %s to %s" % (self.year, newyear))
			# h, m, s = self.decHour(self.hour)
			# dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
			# t_h, t_m, t_s = self.decHour(t_hour)
			# # dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			# dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
			# _dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
			# # mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			# mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
			# 						  self.zodiac, self.settings.settings["astrocfg"])
			# _dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
			# sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			# _dprint("localToSolar: sundiff %s" % (sundiff))
			# sundelta = (sundiff / 360.0) * solaryearsecs
			# _dprint("localToSolar: sundelta %s" % (sundelta))
			# dt_delta = datetime.timedelta(seconds=int(sundelta))
			# dt_new = dt_new + dt_delta

			# newyear = t_year
			solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			_dprint("localToSolar: from %s to %s" %(self.year,t_year))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			print (dt_original)
			print (dt_new)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
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
			# # # mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			# # mdata = ephemeris.ephData(t_year,t_month,t_day,t_hour,t_geolon,t_geolat,t_altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			# # _dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[0]) )
			# # sundiff = self.planets_degree_ut[0] - mdata.planets_degree_ut[0]
			# # _dprint("localToSolar: sundiff %s" %(sundiff))
			# # sundelta = ( sundiff / 360.0 ) * solaryearsecs
			# # _dprint("localToSolar: sundelta %s" % (sundelta))
			# # dt_delta = datetime.timedelta(seconds=int(sundelta))
			# # dt_delta = datetime.timedelta(seconds=int(sundelta))
			# # dt_new = dt_new + dt_delta
			# # mdata = ephemeris.ephData(dt_new.year,dt_new.month,dt_new.day,self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second),self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			# # _dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[0]))
			# # _dprint(dt_new)
			# _dprint(self.planets_degree_ut)
			# mdata = ephemeris.ephData(self.year, self.month, self.day, self.hour, self.geolon,
			# 									self.geolat, self.altitude, self.planets, self.zodiac,
			# 									self.settings.settings["astrocfg"])
			# _dprint(mdata.planets_degree_ut)
			# for i in range(len(self.planets_degree_ut)):
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
			# for i in range(len(self.planets_degree_ut)):
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
			# _dprint(self.planets_degree_ut)
			# _dprint(mdata.planets_degree_ut)
			# #
			# # self.t_year = dt_new.year
			# # self.t_month = dt_new.month
			# # self.t_day = dt_new.day
			# # self.t_hour = self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second)
			# # self.t_geolon = self.geolon
			# # self.t_geolat = self.geolat
			# # self.t_altitude = self.altitude
			# # self.type = "Transit"
			# # self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)

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

			self.__class__.transit=False
			_dprint(dt_new)
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
			# _dprint("localToSolar: from %s to %s" %(self.year,newyear))
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year,t_month,t_day,t_h,t_m,t_s)
			_dprint("localToSolar: first sun %s" % (self.planets_degree_ut[0]) )
			# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			mdata = ephemeris.ephData(t_year,t_month,t_day,t_hour,t_geolon,t_geolat,t_altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			_dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[0]) )
			# sundiff = -360 + self.planets_degree_ut[0] - mdata.planets_degree_ut[0]
			sundiff = self.planets_degree_ut[0] - mdata.planets_degree_ut[0]
			if(sundiff > 0):
				sundiff = sundiff - 360
			_dprint("localToSolar: sundiff %s" %(sundiff))
			sundelta = ( sundiff / 360.0 ) * solaryearsecs
			_dprint("localToSolar: sundelta %s" % (sundelta))
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year,dt_new.month,dt_new.day,self.decHourJoin(dt_new.hour,dt_new.minute,dt_new.second),self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			_dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[0]))
			# _dprint(dt_new)
			#get precise
			planet_id = 0
			for i in range(20):
				# get precise
				solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
				step = 360 / solaryearsecs
				sundiff = self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
				if(sundiff>180):
					sundiff = sundiff - 360
				sundelta = sundiff / step
				dt_delta = datetime.timedelta(seconds=int(sundelta))
				dt_new = dt_new + dt_delta
				mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
				# _dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit=False
			_dprint(dt_new)
			return

		def localToSolarNext(self, t_year, t_month, t_day, t_hour, t_geolon,
												t_geolat, t_altitude):
			return self.localToSolar(t_year+1, t_month, t_day, t_hour, t_geolon,
												t_geolat, t_altitude)

		def localToSolarPrev(self, t_year, t_month, t_day, t_hour, t_geolon,
												t_geolat, t_altitude):
			return self.localToSolar(t_year-1, t_month, t_day, t_hour, t_geolon,
												t_geolat, t_altitude)

		def localToSolarNear(self, t_year, t_month, t_day, t_hour, t_geolon,
												t_geolat, t_altitude):
			h,m,s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year,self.month,self.day,h,m,s)
			t_h,t_m,t_s = self.decHour(t_hour)
			dt_new_year = datetime.datetime(self.year,t_month,t_day,t_h,t_m,t_s)
			dt_delta = dt_original - dt_new_year
			if(datetime.timedelta(days=0) < dt_delta and dt_delta < datetime.timedelta(days=90)): # dr-t >0 t->dr
				return self.localToSolar(t_year + 1, t_month, t_day, t_hour, t_geolon,
										 t_geolat, t_altitude)
			elif(datetime.timedelta(days=-90) < dt_delta and dt_delta < datetime.timedelta(days=0)): # dr-t < 0 dr->t
				return self.localToSolar(t_year - 1, t_month, t_day, t_hour, t_geolon,
										 t_geolat, t_altitude)
			else:
				return self.localToSolar(t_year, t_month, t_day, t_hour, t_geolon,
										 t_geolat, t_altitude)

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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit=False
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit=False
			# _dprint(dt_new)
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit=False
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit=False
			# _dprint(dt_new)
			return


		def localToLunar(self, t_year, t_month, t_day, t_hour, t_geolon,
						 t_geolat, t_altitude):
			planet_id = 1
			newyear = t_year
			# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			solaryearsecs = 27.3215817 * 24 * 60 * 60  # 27,3215817 days
			# _dprint("localToSolar: from %s to %s" % (self.year, newyear))
			h, m, s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
			t_h, t_m, t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
			# _dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_id]))
			# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
									  self.zodiac, self.settings.settings["astrocfg"])
			_dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_id]))
			sundiff = -360 + self.planets_degree_ut[planet_id] - mdata.planets_degree_ut[planet_id]
			# _dprint("localToSolar: sundiff %s" % (sundiff))
			sundelta = (sundiff / 360.0) * solaryearsecs
			# _dprint("localToSolar: sundelta %s" % (sundelta))
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,
									  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), t_geolon, t_geolat,
									  t_altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			# _dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_id]))
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
				mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
				# _dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_id]))
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit = False
			# print(dt_new)
			return


		def localToGeoZodiac(self):
			# geo_zodiac_start = -17.5833333
			geo_zodiac_start = self.settings.settings["astrocfg"]["geo_zodiac_start"]
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
			lon_geo_zodiac = lon_geo - lon_astro
			# lon_geo_zodiac = lon_geo
			if lon_geo_zodiac<0:
				lon_geo_zodiac = lon_geo_zodiac+360
			if lon_geo_zodiac>360:
				lon_geo_zodiac = lon_geo_zodiac-360
			if lon_geo_zodiac<-360:
				lon_geo_zodiac = lon_geo_zodiac+360

			# print ("lon_geo = ", lon_geo)
			# print ("lon_astro = ", lon_astro)
			# print ("lon_geo_zodiac = ", lon_geo_zodiac)

			_dprint("localToGeoZodiac: second Earth %s" % (self.planets_degree_ut[planet_id]))
			# print (self.planets_degree_ut[planet_id])
			degree_diff = lon_geo_zodiac - geo_zodiac_start
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit = False
			# print(dt_new)
			return



		def localToAscReturn(self, t_year, t_month, t_day, t_hour, t_geolon,
						 t_geolat, t_altitude):
			planet_index = self.get_house_planet_index(0)
			if planet_index is None:
				raise KeyError("Ascendant house entry is missing")
			newyear = t_year
			# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			solaryearsecs = 1 * 24 * 60 * 60 / 4 # 27,3215817 days
			# _dprint("localToSolar: from %s to %s" % (self.year, newyear))
			h, m, s = self.decHour(self.hour)
			dt_original = datetime.datetime(self.year, self.month, self.day, h, m, s)
			t_h, t_m, t_s = self.decHour(t_hour)
			# dt_new = datetime.datetime(newyear,self.month,self.day,h,m,s)
			dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
			# _dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_index]))
			# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
									  self.zodiac, self.settings.settings["astrocfg"])
			_dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_index]))
			sundiff = self.planets_degree_ut[planet_index] - mdata.planets_degree_ut[planet_index]
			# _dprint("localToSolar: sundiff %s" % (sundiff))
			sundelta = (sundiff / 360.0) * solaryearsecs
			# _dprint("localToSolar: sundelta %s" % (sundelta))
			dt_delta = datetime.timedelta(seconds=int(sundelta))
			dt_new = dt_new + dt_delta
			mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,
									  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), t_geolon, t_geolat,
									  t_altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
			# _dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_index]))
			# print(dt_new)
			for i in range(100):
				# get precise
				moonyearsecs = 1 * 24 * 60 * 60 /3 # 27,3215817 days
				step = 360 / moonyearsecs
				sundiff = self.planets_degree_ut[planet_index] - mdata.planets_degree_ut[planet_index]
				sundelta = sundiff / step
				dt_delta = datetime.timedelta(seconds=int(sundelta))
				dt_new = dt_new + dt_delta
				mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,								  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
				# _dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_index]))
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit = False
			# print(dt_new)
			return

		def localToEarthReturn(self, t_year, t_month, t_day, t_hour, t_geolon,
						 t_geolat, t_altitude):
			planet_index = self.get_house_planet_index(0)
			if planet_index is None:
				raise KeyError("Ascendant house entry is missing")
			# solaryearsecs = 31556925.51 # 365 days, 5 hours, 48 minutes, 45.51 seconds
			solaryearsecs = 1 * 24 * 60 * 60 / 4 #
			# _dprint("localToSolar: from %s to %s" % (self.year, newyear))
			h, m, s = self.decHour(self.hour)
			# dt = datetime.datetime(self.year, self.month, self.day, h, m, s)
			t_h, t_m, t_s = self.decHour(t_hour)
			dt_new = datetime.datetime(t_year, t_month, t_day, t_h, t_m, t_s)
			t_geolon_new = t_geolon
			# _dprint("localToSolar: first sun %s" % (self.planets_degree_ut[planet_index]))
			# mdata = ephemeris.ephData(newyear,self.month,self.day,self.hour,self.geolon,self.geolat,self.altitude,self.planets,self.zodiac,self.settings.settings["astrocfg"])
			mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon, t_geolat, t_altitude, self.planets,
									  self.zodiac, self.settings.settings["astrocfg"])
			_dprint("localToSolar: second sun %s" % (mdata.planets_degree_ut[planet_index]))
			sundiff = self.planets_degree_ut[planet_index] - mdata.planets_degree_ut[planet_index]
			# _dprint("localToSolar: sundiff %s" % (sundiff))
			# sundelta = (sundiff / 360.0) * solaryearsecs
			# _dprint("localToSolar: sundelta %s" % (sundelta))
			# dt_delta = datetime.timedelta(seconds=int(sundelta))
			t_geolon_new = t_geolon_new + sundiff
			mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon_new, t_geolat, t_altitude, self.planets,
									  self.zodiac, self.settings.settings["astrocfg"])
			# print(sundiff)
			# _dprint("localToSolar: new sun %s" % (mdata.planets_degree_ut[planet_index]))
			# print(dt_new)
			for i in range(100):
				# get precise
				moonyearsecs = 1 * 24 * 60 * 60 /10 # 27,3215817 days
				step = 360 / moonyearsecs
				sundiff = self.planets_degree_ut[planet_index] - mdata.planets_degree_ut[planet_index]
				sundelta = sundiff / 4
				# dt_delta = datetime.timedelta(seconds=int(sundelta))
				# dt_new = dt_new + dt_delta
				t_geolon_new = t_geolon_new + sundelta
				# mdata = ephemeris.ephData(dt_new.year, dt_new.month, dt_new.day,  self.decHourJoin(dt_new.hour, dt_new.minute, dt_new.second), self.geolon, self.geolat,								  self.altitude, self.planets, self.zodiac, self.settings.settings["astrocfg"])
				mdata = ephemeris.ephData(t_year, t_month, t_day, t_hour, t_geolon_new, t_geolat, t_altitude, self.planets,
									  self.zodiac, self.settings.settings["astrocfg"])
				# _dprint("localToSolar: new sun #2 %s" % (mdata.planets_degree_ut[planet_index]))
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
			# self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d:%02d UTC)" % (self.__class__.label["solar"],self.s_year,self.s_month,self.s_day,dt_new.hour,dt_new.minute,dt_new.second)
			self.__class__.transit = False
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

			_dprint("localToSProgression: got UTC %s-%s-%s %s:%s:%s"%(
				dt_new.year,dt_new.month,dt_new.day,dt_new.hour,dt_new.minute,dt_new.second))

			# self.type = "SProgression"
			self.type = "Transit"
			self.__class__.charttype="%s (%s-%02d-%02d %02d:%02d)" % ("SProgression",dt.year,dt.month,dt.day,dt.hour,dt.minute)
			self.__class__.transit=False
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
			# _dprint("localToSProgression: got UTC %s-%s-%s %s:%s:%s" % (
			# 	dt_new.year, dt_new.month, dt_new.day, dt_new.hour, dt_new.minute, dt_new.second))
			#
			# # self.type = "SProgression"
			# self.type = "Transit"
			# self.__class__.charttype = "%s (%s-%02d-%02d %02d:%02d)" % (
			# "SProgression", dt.year, dt.month, dt.day, dt.hour, dt.minute)
			# self.__class__.transit = False
			return
