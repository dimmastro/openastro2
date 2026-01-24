#!/usr/bin/env python
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
from typing import List, Dict, Any, Tuple, Optional, Union
import importlib
import os.path, sys, datetime, math
from pathlib import Path
from skyfield.api import wgs84

from openastromod.skyfield_loader import load
from openastromod.utils import decHour
# #swiss ephemeris files directory
# swissDir = os.path.join(sys.prefix,'share','swisseph')
#local swiss ephemeris files directory
# home=os.path.expanduser("~")
# oa=os.path.join(home, '.openastro.org')
# swissLocalDir=os.path.join(oa, 'swiss_ephemeris')
#
# #swiss ephemeris path
# ephe_path=swissDir+':'+swissLocalDir

DATADIR = Path(__file__).parent.parent
ephe_path = str(DATADIR) + '/swiss_ephemeris'

import swisseph as swe
from openastromod.fixar import get_fixar_ecliptic_latlon_arr, get_fixar_earth_ecliptic_latlon_arr

class ephData:
	def __init__(self, year: int, month: int, day: int, hour: float, geolon: float, geolat: float, altitude: int, planets: List[Any], zodiac: List[str], openastrocfg: Dict[str, Any], houses_override: Optional[Any] = None) -> None:
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.geolon = geolon
		self.geolat = geolat
		self.altitude = altitude
		h, m, s = decHour(self.hour)
		self.h = h
		self.m = m
		self.s = s
		#ephemeris path (default "/usr/share/swisseph:/usr/local/share/swisseph")
		swe.set_ephe_path(ephe_path)
		# print (ephe_path)
		#basic location		
		self.jul_day_UT=swe.julday(year,month,day,hour)
		self.geo_loc = swe.set_topo(geolon,geolat,altitude)

		#output variables
		self.planets_sign = list(range(len(planets)))
		self.planets_degree = list(range(len(planets)))
		self.planets_degree_ut = list(range(len(planets)))
		self.planets_info_string = list(range(len(planets)))
		self.planets_retrograde = list(range(len(planets)))
		self.planet_longitude = list(range(len(planets)))
		self.planet_latitude = list(range(len(planets)))
		self.planet_hour_angle = list(range(len(planets)))
		self.planet_azimuth = list(range(len(planets)))
		self.planet_true_altitude = list(range(len(planets)))
		self.planet_apparent_altitude = list(range(len(planets)))
		self._set_planet_metadata(planets)
		self._set_planet_metadata(planets)
		self.planet_apparent_altitude = list(range(len(planets)))
		self.planet_lat_speed = list(range(len(planets)))
		self.planet_lon_speed = list(range(len(planets)))
		self.planet_distance = list(range(len(planets)))

		self.openastrocfg = openastrocfg
		self._set_planet_metadata(planets)


		#iflag
		"""
		#define SEFLG_JPLEPH         1L     // use JPL ephemeris
		#define SEFLG_SWIEPH         2L     // use SWISSEPH ephemeris, default
		#define SEFLG_MOSEPH         4L     // use Moshier ephemeris
		#define SEFLG_HELCTR         8L     // return heliocentric position
		#define SEFLG_TRUEPOS        16L     // return true positions, not apparent
		#define SEFLG_J2000          32L     // no precession, i.e. give J2000 equinox
		#define SEFLG_NONUT          64L     // no nutation, i.e. mean equinox of date
		#define SEFLG_SPEED3         128L     // speed from 3 positions (do not use it, SEFLG_SPEED is // faster and preciser.)
		#define SEFLG_SPEED          256L     // high precision speed (analyt. comp.)
		#define SEFLG_NOGDEFL        512L     // turn off gravitational deflection
		#define SEFLG_NOABERR        1024L     // turn off 'annual' aberration of light
		#define SEFLG_EQUATORIAL     2048L     // equatorial positions are wanted
		#define SEFLG_XYZ            4096L     // cartesian, not polar, coordinates
		#define SEFLG_RADIANS        8192L     // coordinates in radians, not degrees
		#define SEFLG_BARYCTR        16384L     // barycentric positions
		#define SEFLG_TOPOCTR      (32*1024L)     // topocentric positions
		#define SEFLG_SIDEREAL     (64*1024L)     // sidereal positions 		
		"""

		self.houses_system_polar_list = ['A', 'D', 'E', 'H', 'M', 'N', 'O', 'U', 'V', 'W', 'X']
		"""
		    https://www.astro.com/faq/fq_fh_owhouse_e.htm
		    https://www.astro.com/swisseph/swisseph.htm#_Toc112511764

		    https://www.astro.com/swisseph/swephprg.htm#_Toc112949022
		    The complete list of house methods in alphabetical order is:

		hsys =   ‘B’        Alcabitus
		        ‘Y’        APC houses
		        ‘X’        Axial rotation system / Meridian system / Zariel
		        ‘H’        Azimuthal or horizontal system
		        ‘C’        Campanus
		        ‘F’        Carter "Poli-Equatorial"
		        ‘A’ or ‘E’ Equal (cusp 1 is Ascendant)
		        ‘D’        Equal MC (cusp 10 is MC)
		        ‘N’        Equal/1=Aries
		        ‘G’        Gauquelin sector
		                   Goelzer -> Krusinski
		                   Horizontal system -> Azimuthal system
		        ‘I’        Sunshine (Makransky, solution Treindl)
		        ‘i’        Sunshine (Makransky, solution Makransky)
		        ‘K’        Koch
		        ‘U’        Krusinski-Pisa-Goelzer
		                   Meridian system -> axial rotation
		        ‘M’        Morinus
		                   Neo-Porphyry -> Pullen SD
		                   Pisa -> Krusinski
		        ‘P’        Placidus
		                   Poli-Equatorial -> Carter
		        ‘T’        Polich/Page (“topocentric” system)
		        ‘O’        Porphyrius
		        ‘L’        Pullen SD (sinusoidal delta) – ex Neo-Porphyry
		        ‘Q’        Pullen SR (sinusoidal ratio)
		        ‘R’        Regiomontanus
		        ‘S’        Sripati
		                   “Topocentric” system -> Polich/Page
		        ‘V’        Vehlow equal (Asc. in middle of house 1)
		        ‘W’        Whole sign
		                   Zariel -> Axial rotation system
		    """

		#check for apparent geocentric (default), true geocentric, topocentric or heliocentric
		iflag=swe.FLG_SWIEPH+swe.FLG_SPEED
		if(openastrocfg['postype']=="truegeo"):
			iflag += swe.FLG_TRUEPOS
		elif(openastrocfg['postype']=="topo"):
			iflag += swe.FLG_TOPOCTR
		elif(openastrocfg['postype']=="helio"):
			iflag += swe.FLG_HELCTR

		#sidereal
		if(openastrocfg['zodiactype']=="sidereal"):
			iflag += swe.FLG_SIDEREAL
			mode="SIDM_"+openastrocfg['siderealmode']
			swe.set_sid_mode(getattr(swe,mode))

		len_planets = 43

		planet_pos_list = self.modules_append_data_in_lists(year=year, month=month, day=day, hour=hour, h=h, m=m, s=s, geolon=geolon, geolat=geolat, altitude=altitude, openastrocfg=openastrocfg)
		# print(planet_pos_list)
		len_planets_from_modules = len(planet_pos_list)
		len_planets_total = len_planets + len_planets_from_modules
		if len_planets_from_modules > 0:
			self.planets_sign = list(range(len_planets_total))
			self.planets_degree = list(range(len_planets_total))
			self.planets_degree_ut = list(range(len_planets_total))
			self.planets_info_string = list(range(len_planets_total))
			self.planets_retrograde = list(range(len_planets_total))
			self.planet_longitude = list(range(len_planets_total))
			self.planet_latitude = list(range(len_planets_total))
			self.planet_hour_angle = list(range(len_planets_total))
			self.planet_azimuth = list(range(len_planets_total))
			self.planet_true_altitude = list(range(len_planets_total))
			self.planet_apparent_altitude = list(range(len_planets_total))
			self.planet_apparent_altitude = list(range(len_planets_total))
			self.planet_lat_speed = list(range(len_planets_total))
			self.planet_lon_speed = list(range(len_planets_total))
			self.planet_distance = list(range(len_planets_total))


		# print(planet_pos_list)
		#compute a planet (longitude,latitude,distance,long.speed,lat.speed,speed)
		for i in range(len_planets_total):
			if 22 < i and i < len_planets:
				continue
			if i >= len_planets:
				ret_flag = planet_pos_list[i-len_planets]
				# print (i-len_planets)
				# print(ret_flag)
			else:
				if(i==15 and ( self.jul_day_UT < 1967601.5 or 3419437.5 < self.jul_day_UT )): # Chiron limit
					ret_flag = swe.calc_ut(1967601.5, i, iflag)
				else:
					ret_flag = swe.calc_ut(self.jul_day_UT,i,iflag)
			for x in range(len(zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if ret_flag[0][0] >= deg_low:
					if ret_flag[0][0] <= deg_high:
						self.planets_sign[i]=x
						self.planets_degree[i] = ret_flag[0][0] - deg_low
						self.planets_degree_ut[i] = ret_flag[0][0]
						self.planet_distance[i] = ret_flag[0][2] # distance
						self.planet_lon_speed[i] = ret_flag[0][3] # ???
						self.planet_lat_speed[i] = ret_flag[0][4] # ???
						#if latitude speed is negative, there is retrograde
						if ret_flag[0][3] < 0:
							self.planets_retrograde[i] = True
						else:
							self.planets_retrograde[i] = False

						# Calc hour_angle in degrees
						self.planet_longitude[i] = ret_flag[0][0]
						self.planet_latitude[i] = ret_flag[0][1]

						# self.planet_hour_angle[i] = swe.degnorm(swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon -10.5)
						self.planet_hour_angle[i] = swe.degnorm(swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon)

						observer_latitude = geolat
						observer_longitude = geolon

						# swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
						planet_pos = ret_flag
						# azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.EQU2HOR,
						azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.ECL2HOR,
																			  [observer_longitude, observer_latitude, 287], 0, 0,
																			  [planet_pos[0][0], planet_pos[0][1], planet_pos[0][2], planet_pos[0][3], planet_pos[0][4], planet_pos[0][5]])

						azimuth = azimuth + 180
						if (azimuth > 360):
							azimuth = azimuth - 360
						self.planet_azimuth[i] = azimuth
						self.planet_true_altitude[i] = true_altitude
						self.planet_apparent_altitude[i] = apparent_altitude
		#available house systems:
		"""
		hsys= 		‘P’     Placidus
				‘K’     Koch
				‘O’     Porphyrius
				‘R’     Regiomontanus
				‘C’     Campanus
				‘A’ or ‘E’     Equal (cusp 1 is Ascendant)
				‘V’     Vehlow equal (Asc. in middle of house 1)
				‘X’     axial rotation system
				‘H’     azimuthal or horizontal system
				‘T’     Polich/Page (“topocentric” system)
				‘B’     Alcabitus
				‘G’     Gauquelin sectors
				‘M’     Morinus
		"""
		#houses calculation (hsys=P for Placidus)
		#check for polar circle latitude < -66 > 66
		if houses_override:
			self.jul_day_UT = swe.julday(houses_override[0],houses_override[1],houses_override[2],houses_override[3])
			
		if geolat > 66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = 66.0
				# print("polar circle override for houses, using 66 degrees")
		elif geolat < -66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = -66.0
				# print("polar circle override for houses, using -66 degrees")

		#sidereal houses
		if(openastrocfg['zodiactype']=="sidereal"):
			sh = swe.houses_ex(self.jul_day_UT,geolat,geolon,openastrocfg['houses_system'].encode("ascii"),swe.FLG_SIDEREAL)
		else:
			sh = swe.houses(self.jul_day_UT,geolat,geolon,openastrocfg['houses_system'].encode("ascii"))

		self.houses_degree_ut = list(sh[0])

		#arabic parts
		sun,moon,asc = self.planets_degree_ut[0],self.planets_degree_ut[1],self.houses_degree_ut[0]
		dsc,venus = self.houses_degree_ut[6],self.planets_degree_ut[3]	

		#offset
		offset = moon - sun
		
		#if planet degrees is greater than 360 substract 360 or below 0 add 360
		for i in range(len(self.houses_degree_ut)):
			#add offset
			#self.houses_degree_ut[i] += offset
			
			if self.houses_degree_ut[i] > 360.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] - 360.0
			elif self.houses_degree_ut[i] < 0.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] + 360.0		
		

		self.houses_degree = list(range(len(self.houses_degree_ut)))
		self.houses_sign = list(range(len(self.houses_degree_ut)))
		for i in range(12):
			for x in range(len(zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if self.houses_degree_ut[i] >= deg_low:
					if self.houses_degree_ut[i] <= deg_high:
						self.houses_sign[i]=x
						self.houses_degree[i] = self.houses_degree_ut[i] - deg_low

		self._assign_house_positions()
		
		
		#mean apogee
		bm=self.planets_degree_ut[12]
		#mean north node
		mn=self.planets_degree_ut[10]
		#perigee lunaire moyen
		pl=self.planets_degree_ut[22]
		#perigee solaire moyen
		#define SE_NODBIT_MEAN          1
		#define SE_NODBIT_OSCU          2
		#define SE_NODBIT_OSCU_BAR     4
		#define SE_NODBIT_FOPOINT     256
		#Return: 4 tuples of 6 float (asc, des, per, aph)
		ps=swe.nod_aps_ut(self.jul_day_UT,0,swe.NODBIT_MEAN,iflag)
		pl=swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_MEAN,iflag)
		ps=ps[2][0]
		pl=pl[2][0]
		#print mn
		#print sun
		#print ps
		#print moon
		#print pl
		
		c= 1.517 * math.sin(2*math.radians(sun-mn))
		c+= -0.163 * math.sin(math.radians(sun-ps))
		c+= -0.128 * math.sin(2*math.radians(moon-sun))
		c+= 0.120 * math.sin(2*math.radians(moon-mn))
		c+= 0.107 * math.sin(2*math.radians(pl-mn))
		c+= 0.063 * math.sin(math.radians(3*sun-ps-2*mn))
		c+= 0.040 * math.sin(math.radians(moon+pl-2*sun))
		c+= -0.040 * math.sin(math.radians(moon+pl-2*mn))
		c+= 0.027 * math.sin(math.radians(moon-pl))
		c+= -0.027 * math.sin(math.radians(sun+ps-2*mn))
		c+= 0.015 * math.sin(2*math.radians(sun-pl))
		c+= -0.013 * math.sin(math.radians(moon+2*mn-pl-2*sun))
		c+= -0.013 * math.sin(math.radians(moon-2*mn-pl+2*sun))
		c+= -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		c+= 0.005 * math.sin(math.radians(3*moon-pl-2*mn))
		c+= -0.005 * math.sin(math.radians(3*moon-pl-2*sun))
		#print c
		
		sbm=sun-bm
		if sbm < 0: sbm += 360
		if sbm > 180.0: sbm -= 180
		# print("sun %s black moon %s sun-bm %s=%s" % (sun,bm,sun-bm,sbm))

		q=12.333
		if sbm < 60.0:
			# print('sbm<60')
			c= q * math.sin(1.5*math.radians(sbm))
		elif sbm > 120.0:
			# print('sbm>120')
			c= q * math.cos(1.5*math.radians(sbm))
		else:
			# print('sbm 60-120')
			c= -q * math.cos(3.0*math.radians(sbm))

		true_lilith=c

		def true_lilith_calc(sun,lilith):
			deg=sun-lilith
			q=12.333
			if deg < 0.0: deg+=360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0: return q * math.sin(1.5*math.radians(deg)) - 1.892 * math.sin(3*math.radians(deg))
			elif deg > 120.0: return q * math.cos(1.5*math.radians(deg)) + 1.892 * math.sin(3*math.radians(deg))
			elif deg < 100.0: return -q * math.cos(3.0*math.radians(deg)) + 0.821 * math.cos(4.5*math.radians(deg))
			else: return -q * math.cos(3.0*math.radians(deg))

		def true_lilith_calc2(sun,lilith):
			deg=sun-lilith
			q=12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0: return q * math.sin(1.5*math.radians(deg))
			elif deg > 120.0: return q * math.cos(1.5*math.radians(deg))
			else: return -q * math.cos(3.0*math.radians(deg))

		true_lilith=true_lilith_calc2(sun,bm)
		#print c
		"""
		if sbm < 60.0:
			print 'sbm 0-60'
			c=  q * math.sin(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 60.0 and sbm < 120.0:
			print 'sbm 60-120'
			c= -q * math.cos(3*math.radians(sbm)) - 0.0917
		elif sbm >= 120.0 and sbm < 240.0:
			print 'sbm 120-240'
			c= q * math.cos(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 240.0 and sbm < 300.0:
			print 'sbm 240-300'
			c= q * math.cos(3*math.radians(sbm)) - 0.0917
		else:
			print 'sbm 300-360'
			c= -q * math.sin(1.5*math.radians(sbm)) - 0.0917
		"""
		c+= - 0.117 * math.sin(math.radians(sun-ps))
		#print c
		
		#c+= x * -0.163 * math.sin(math.radians(sun-ps))
		#c+= x * -0.128 * math.sin(2*math.radians(moon-sun))
		#c+= x * 0.120 * math.sin(2*math.radians(moon-bm))
		#c+= x * 0.107 * math.sin(2*math.radians(pl-bm))
		#c+= x * 0.063 * math.sin(math.radians(3*sun-ps-2*bm))
		#c+= x * 0.040 * math.sin(math.radians(moon+pl-2*sun))
		#c+= x * -0.040 * math.sin(math.radians(moon+pl-2*bm))
		#c+= x * 0.027 * math.sin(math.radians(moon-pl))
		#c+= x * -0.027 * math.sin(math.radians(sun+ps-2*bm))
		#c+= x * 0.015 * math.sin(2*math.radians(sun-pl))
		#c+= x * -0.013 * math.sin(math.radians(moon+2*bm-pl-2*sun))
		#c+= x * -0.013 * math.sin(math.radians(moon-2*bm-pl+2*sun))
		#c+= x * -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		#c+= x * 0.005 * math.sin(math.radians(3*moon-pl-2*bm))
		#c+= x * -0.005 * math.sin(math.radians(3*moon-pl-2*sun))
		

		#list index 27 is day pars
		self.planets_degree_ut[35] = asc + (moon - sun)
		#list index 28 is night pars
		self.planets_degree_ut[36] = asc + (sun - moon)
		#list index 29 is South Node
		# self.planets_degree_ut[37] = self.planets_degree_ut[10] - 180.0
		self.planets_degree_ut[37] = self.planets_degree_ut[11] - 180.0
		#list index 30 is marriage pars
		self.planets_degree_ut[38] = (asc+dsc)-venus
		#list index 31 is black sun
		self.planets_degree_ut[39] = swe.nod_aps_ut(self.jul_day_UT,0,swe.NODBIT_MEAN,swe.FLG_SWIEPH)[3][0]
		#list index 32 is vulcanus
		self.planets_degree_ut[40] = 31.1 + (self.jul_day_UT-2425246.5) * 0.00150579
		#list index 33 is persephone
		self.planets_degree_ut[41] = 240.0 + (self.jul_day_UT-2425246.5) * 0.002737829
		#list index 34 is true lilith (own calculation)
		self.planets_degree_ut[42] = self.planets_degree_ut[12] + true_lilith
		#swiss ephemeris version of true lilith
		#self.planets_degree_ut[34] = swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_OSCU,swe.FLG_SWIEPH)[3][0]

		#adjust list index 32 and 33
		for i in range(self._extended_body_start_index(), len_planets_total):
			while ( self.planets_degree_ut[i] < 0 ): self.planets_degree_ut[i]+=360.0
			while ( self.planets_degree_ut[i] > 360.0): self.planets_degree_ut[i]-=360.0
	
			#get zodiac sign
			for x in range(12):
				deg_low=float(x*30.0)
				deg_high=float((x+1.0)*30.0)
				if self.planets_degree_ut[i] >= deg_low:
					if self.planets_degree_ut[i] <= deg_high:
						self.planets_sign[i]=x
						self.planets_degree[i] = self.planets_degree_ut[i] - deg_low
						self.planets_retrograde[i] = False

		#lunar phase, anti-clockwise degrees between sun and moon
		ddeg=moon-sun
		if ddeg<0: ddeg+=360.0
		step=360.0 / 28.0
		# print(moon,sun,ddeg)
		for x in range(28):
			low=x*step
			high=(x+1)*step
			if ddeg >= low and ddeg < high: mphase=x+1
		sunstep=[0,30,40,50,60,70,80,90,120,130,140,150,160,170,180,210,220,230,240,250,260,270,300,310,320,330,340,350]
		for x in range(len(sunstep)):
			low=sunstep[x]
			#ToDo Fix 27
			if x == 27: high=360
			else: high=sunstep[x+1]
			if ddeg >= low and ddeg < high: sphase=x+1
		self.lunar_phase={
					"degrees":ddeg,
					"moon_phase":mphase,
					"sun_phase":sphase
		}
		
		#close swiss ephemeris
		swe.close()

	def _set_planet_metadata(self, planets: List[Any]) -> None:
		self._planets_meta = planets or []
		mappings: List[Tuple[int, Optional[int]]] = []
		if isinstance(self._planets_meta, list):
			for idx, entry in enumerate(self._planets_meta):
				if isinstance(entry, dict) and entry.get("_is_house"):
					house_number = entry.get("_house_number")
					if house_number is None:
						try:
							house_number = int(entry.get("id"))
						except (TypeError, ValueError):
							house_number = None
					mappings.append((idx, house_number))
		self._house_body_mappings = mappings
		self._first_house_start_index = min((idx for idx, _ in mappings), default=len(self._planets_meta))

	def _extended_body_start_index(self) -> int:
		return getattr(self, "_first_house_start_index", len(getattr(self, "_planets_meta", [])))

	def _assign_house_positions(self) -> None:
		if not hasattr(self, "planets_degree_ut") or not hasattr(self, "_house_body_mappings"):
			return
		if not hasattr(self, "houses_degree_ut"):
			return
		for idx, house_number in self._house_body_mappings:
			if house_number is None or house_number >= len(self.houses_degree_ut):
				continue
			if idx >= len(self.planets_degree_ut):
				continue
			self.planets_degree_ut[idx] = self.houses_degree_ut[house_number]
			if hasattr(self, "houses_degree") and idx < len(self.planets_degree):
				self.planets_degree[idx] = self.houses_degree[house_number]
			if hasattr(self, "houses_sign") and idx < len(self.planets_sign):
				self.planets_sign[idx] = self.houses_sign[house_number]
			if hasattr(self, "planets_retrograde") and idx < len(self.planets_retrograde):
				self.planets_retrograde[idx] = False

	def modules_append_data_in_lists(self, *args, **kwargs):
		"""
		Add data from planet_pos_list from all modules to one list ret_flag_list
		:param args:
		:param kwargs:
		:return:
		"""
		year = kwargs['year']
		month = kwargs['month']
		day = kwargs['day']
		hour = kwargs['hour']
		h = kwargs['h']
		m = kwargs['m']
		s = kwargs['s']
		geolat = kwargs['geolat']
		geolon = kwargs['geolon']
		altitude = kwargs['altitude']
		openastrocfg = kwargs['openastrocfg']
		ret_flag_list = []
		results = self.load_modules(year=year, month = month, day=day, hour=hour, h=h, m=m, s=s, geolon=geolon, geolat=geolat, altitude=altitude, openastrocfg=openastrocfg)
		for module_name, planet_pos_list in results.items():
			# len = len(results[module_name])
			for ret_flag in planet_pos_list:
				ret_flag_list.append(ret_flag)
		return ret_flag_list






	def load_modules(self, *args, **kwargs):
		"""
		Run all modules and add data to dict

		:param args:
		:param kwargs:
		:return:
		"""
		year = kwargs['year']
		month = kwargs['month']
		day = kwargs['day']
		hour = kwargs['hour']
		h = kwargs['h']
		m = kwargs['m']
		s = kwargs['s']
		geolat = kwargs['geolat']
		geolon = kwargs['geolon']
		altitude = kwargs['altitude']
		openastrocfg = kwargs['openastrocfg']
		results = {}
		planet_pos_list = []
		if "modules" in self.openastrocfg:
			for module_name, module_config in self.openastrocfg["modules"]["object"].items():
				if module_config["enabled"]:
					# module_path = f"openastro2.modules.object.{module_name}.{module_name}"
					module_path = f"modules.object.{module_name}.{module_name}"
					try:
						# Динамически импортируем модуль
						module = importlib.import_module(module_path)
						# Инициализируем класс с аргументами из конфигурации
						module_class = getattr(module, module_name.capitalize())
						module_instance = module_class(**module_config["params"])
						# Вызываем метод `process` и сохраняем результат
						# planet_pos_list = module_instance.process(self.year,self.month,self.day,self.hour,h,m,s,self.geolon,self.geolat,self.altitude,self.openastrocfg)
						results[module_name] = module_instance.process(year=year, month = month, day=day, hour=hour, h=h, m=m, s=s, geolon=geolon, geolat=geolat, altitude=altitude, openastrocfg=openastrocfg)
						# print('results=',results)
					except ImportError as e:
						print(f"Can't load module {module_name}: {e}")
					except AttributeError as e:
						print(f"Class {module_name.capitalize()} not found in module {module_name}: {e}")
		return results

	def ephData_fixar(self, year, month, day, hour, t_year, t_month, t_day, t_hour, geolon, geolat, altitude, planets, zodiac, openastrocfg,
			 houses_override=None):
		# ephemeris path (default "/usr/share/swisseph:/usr/local/share/swisseph")
		swe.set_ephe_path(ephe_path)
		# print (ephe_path)
		# basic location
		self.jul_day_UT = swe.julday(year, month, day, hour)
		self.geo_loc = swe.set_topo(geolon, geolat, altitude)

		# output variables
		self.planets_sign = list(range(len(planets)))
		self.planets_degree = list(range(len(planets)))
		self.planets_degree_ut = list(range(len(planets)))
		self.planets_info_string = list(range(len(planets)))
		self.planets_retrograde = list(range(len(planets)))
		self.planet_longitude = list(range(len(planets)))
		self.planet_latitude = list(range(len(planets)))
		self.planet_hour_angle = list(range(len(planets)))
		self.planet_azimuth = list(range(len(planets)))
		self.planet_true_altitude = list(range(len(planets)))
		self.planet_apparent_altitude = list(range(len(planets)))

		# iflag
		"""
		#define SEFLG_JPLEPH         1L     // use JPL ephemeris
		#define SEFLG_SWIEPH         2L     // use SWISSEPH ephemeris, default
		#define SEFLG_MOSEPH         4L     // use Moshier ephemeris
		#define SEFLG_HELCTR         8L     // return heliocentric position
		#define SEFLG_TRUEPOS        16L     // return true positions, not apparent
		#define SEFLG_J2000          32L     // no precession, i.e. give J2000 equinox
		#define SEFLG_NONUT          64L     // no nutation, i.e. mean equinox of date
		#define SEFLG_SPEED3         128L     // speed from 3 positions (do not use it, SEFLG_SPEED is // faster and preciser.)
		#define SEFLG_SPEED          256L     // high precision speed (analyt. comp.)
		#define SEFLG_NOGDEFL        512L     // turn off gravitational deflection
		#define SEFLG_NOABERR        1024L     // turn off 'annual' aberration of light
		#define SEFLG_EQUATORIAL     2048L     // equatorial positions are wanted
		#define SEFLG_XYZ            4096L     // cartesian, not polar, coordinates
		#define SEFLG_RADIANS        8192L     // coordinates in radians, not degrees
		#define SEFLG_BARYCTR        16384L     // barycentric positions
		#define SEFLG_TOPOCTR      (32*1024L)     // topocentric positions
		#define SEFLG_SIDEREAL     (64*1024L)     // sidereal positions 		
		"""
		# check for apparent geocentric (default), true geocentric, topocentric or heliocentric
		iflag = swe.FLG_SWIEPH + swe.FLG_SPEED
		if (openastrocfg['postype'] == "truegeo"):
			iflag += swe.FLG_TRUEPOS
		elif (openastrocfg['postype'] == "topo"):
			iflag += swe.FLG_TOPOCTR
		elif (openastrocfg['postype'] == "helio"):
			iflag += swe.FLG_HELCTR

		# sidereal
		if (openastrocfg['zodiactype'] == "sidereal"):
			iflag += swe.FLG_SIDEREAL
			mode = "SIDM_" + openastrocfg['siderealmode']
			swe.set_sid_mode(getattr(swe, mode))


		h, m, s = self.decHour(hour)
		t_h, t_m, t_s = self.decHour(t_hour)
		ts = load.timescale()
		t1 = ts.utc(year, month, day, h, m, s)
		t2 = ts.utc(t_year, t_month, t_day, t_h, t_m, t_s)
		planet_name_dic = {10: 'sun', 301: 'moon', 1: 'mercury', 2: 'venus', 4: 'mars', 5: 'jupiter', 6: 'saturn',
						   7: 'uran',
						   8: 'neptun',
						   9: 'pluton'}
		[lat_arr, lon_arr] = get_fixar_ecliptic_latlon_arr(planet_name_dic, t1, t2, 0, 0)


		# compute a planet (longitude,latitude,distance,long.speed,lat.speed,speed)
		for i in range(23):
			ret_flag = swe.calc_ut(self.jul_day_UT, i, iflag)
			if(i<10):
				ret_flag_0_0 = lon_arr[i]
				ret_flag_0_1 = lat_arr[i]
			else:
				ret_flag_0_0 = ret_flag[0][0]
				ret_flag_0_1 = ret_flag[0][1]

			for x in range(len(zodiac)):
				deg_low = float(x * 30)
				deg_high = float((x + 1) * 30)
				if ret_flag_0_0 >= deg_low:
					if ret_flag_0_0 <= deg_high:
						self.planets_sign[i] = x
						self.planets_degree[i] = ret_flag_0_0 - deg_low
						self.planets_degree_ut[i] = ret_flag_0_0
						# if latitude speed is negative, there is retrograde
						if ret_flag[0][3] < 0:
							self.planets_retrograde[i] = True
						else:
							self.planets_retrograde[i] = False

						# Calc hour_angle in degrees
						self.planet_longitude[i] = ret_flag_0_0
						self.planet_latitude[i] = ret_flag_0_1

						# self.planet_hour_angle[i] = swe.degnorm(swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon -10.5)
						self.planet_hour_angle[i] = swe.degnorm(
							swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon)

						observer_latitude = geolat
						observer_longitude = geolon

						# swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
						planet_pos = ret_flag
						# azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.EQU2HOR,
						azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.ECL2HOR,
																			  [observer_longitude, observer_latitude,
																			   287], 0, 0,
																			  [planet_pos[0][0], planet_pos[0][1],
																			   planet_pos[0][2], planet_pos[0][3],
																			   planet_pos[0][4], planet_pos[0][5]])

						azimuth = azimuth + 180
						if (azimuth > 360):
							azimuth = azimuth - 360
						self.planet_azimuth[i] = azimuth
						self.planet_true_altitude[i] = true_altitude
						self.planet_apparent_altitude[i] = apparent_altitude
		# available house systems:
		"""
		hsys= 		‘P’     Placidus
				‘K’     Koch
				‘O’     Porphyrius
				‘R’     Regiomontanus
				‘C’     Campanus
				‘A’ or ‘E’     Equal (cusp 1 is Ascendant)
				‘V’     Vehlow equal (Asc. in middle of house 1)
				‘X’     axial rotation system
				‘H’     azimuthal or horizontal system
				‘T’     Polich/Page (“topocentric” system)
				‘B’     Alcabitus
				‘G’     Gauquelin sectors
				‘M’     Morinus
		"""
		# houses calculation (hsys=P for Placidus)
		# check for polar circle latitude < -66 > 66
		if houses_override:
			self.jul_day_UT = swe.julday(houses_override[0], houses_override[1], houses_override[2], houses_override[3])

		if geolat > 66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = 66.0
				# print("polar circle override for houses, using 66 degrees")
		elif geolat < -66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = -66.0
				# print("polar circle override for houses, using -66 degrees")

		# sidereal houses
		if (openastrocfg['zodiactype'] == "sidereal"):
			sh = swe.houses_ex(self.jul_day_UT, geolat, geolon, openastrocfg['houses_system'].encode("ascii"),
							   swe.FLG_SIDEREAL)
		else:
			sh = swe.houses(self.jul_day_UT, geolat, geolon, openastrocfg['houses_system'].encode("ascii"))

		self.houses_degree_ut = list(sh[0])

		# arabic parts
		sun, moon, asc = self.planets_degree_ut[0], self.planets_degree_ut[1], self.houses_degree_ut[0]
		dsc, venus = self.houses_degree_ut[6], self.planets_degree_ut[3]

		# offset
		offset = moon - sun

		# if planet degrees is greater than 360 substract 360 or below 0 add 360
		for i in range(len(self.houses_degree_ut)):
			# add offset
			# self.houses_degree_ut[i] += offset

			if self.houses_degree_ut[i] > 360.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] - 360.0
			elif self.houses_degree_ut[i] < 0.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] + 360.0

		self.houses_degree = list(range(len(self.houses_degree_ut)))
		self.houses_sign = list(range(len(self.houses_degree_ut)))
		for i in range(12):
			for x in range(len(zodiac)):
				deg_low = float(x * 30)
				deg_high = float((x + 1) * 30)
				if self.houses_degree_ut[i] >= deg_low:
					if self.houses_degree_ut[i] <= deg_high:
						self.houses_sign[i] = x
						self.houses_degree[i] = self.houses_degree_ut[i] - deg_low

		if hasattr(self, "_apply_house_positions_to_planets"):
			self._apply_house_positions_to_planets()

		# mean apogee
		bm = self.planets_degree_ut[12]
		# mean north node
		mn = self.planets_degree_ut[10]
		# perigee lunaire moyen
		pl = self.planets_degree_ut[22]
		# perigee solaire moyen
		# define SE_NODBIT_MEAN          1
		# define SE_NODBIT_OSCU          2
		# define SE_NODBIT_OSCU_BAR     4
		# define SE_NODBIT_FOPOINT     256
		# Return: 4 tuples of 6 float (asc, des, per, aph)
		ps = swe.nod_aps_ut(self.jul_day_UT, 0, swe.NODBIT_MEAN, iflag)
		pl = swe.nod_aps_ut(self.jul_day_UT, 1, swe.NODBIT_MEAN, iflag)
		ps = ps[2][0]
		pl = pl[2][0]
		# print mn
		# print sun
		# print ps
		# print moon
		# print pl

		c = 1.517 * math.sin(2 * math.radians(sun - mn))
		c += -0.163 * math.sin(math.radians(sun - ps))
		c += -0.128 * math.sin(2 * math.radians(moon - sun))
		c += 0.120 * math.sin(2 * math.radians(moon - mn))
		c += 0.107 * math.sin(2 * math.radians(pl - mn))
		c += 0.063 * math.sin(math.radians(3 * sun - ps - 2 * mn))
		c += 0.040 * math.sin(math.radians(moon + pl - 2 * sun))
		c += -0.040 * math.sin(math.radians(moon + pl - 2 * mn))
		c += 0.027 * math.sin(math.radians(moon - pl))
		c += -0.027 * math.sin(math.radians(sun + ps - 2 * mn))
		c += 0.015 * math.sin(2 * math.radians(sun - pl))
		c += -0.013 * math.sin(math.radians(moon + 2 * mn - pl - 2 * sun))
		c += -0.013 * math.sin(math.radians(moon - 2 * mn - pl + 2 * sun))
		c += -0.007 * math.sin(math.radians(2 * moon + pl - 3 * sun))
		c += 0.005 * math.sin(math.radians(3 * moon - pl - 2 * mn))
		c += -0.005 * math.sin(math.radians(3 * moon - pl - 2 * sun))
		# print c

		sbm = sun - bm
		if sbm < 0: sbm += 360
		if sbm > 180.0: sbm -= 180
		# print("sun %s black moon %s sun-bm %s=%s" % (sun,bm,sun-bm,sbm))

		q = 12.333
		if sbm < 60.0:
			# print('sbm<60')
			c = q * math.sin(1.5 * math.radians(sbm))
		elif sbm > 120.0:
			# print('sbm>120')
			c = q * math.cos(1.5 * math.radians(sbm))
		else:
			# print('sbm 60-120')
			c = -q * math.cos(3.0 * math.radians(sbm))

		true_lilith = c

		def true_lilith_calc(sun, lilith):
			deg = sun - lilith
			q = 12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0:
				return q * math.sin(1.5 * math.radians(deg)) - 1.892 * math.sin(3 * math.radians(deg))
			elif deg > 120.0:
				return q * math.cos(1.5 * math.radians(deg)) + 1.892 * math.sin(3 * math.radians(deg))
			elif deg < 100.0:
				return -q * math.cos(3.0 * math.radians(deg)) + 0.821 * math.cos(4.5 * math.radians(deg))
			else:
				return -q * math.cos(3.0 * math.radians(deg))

		def true_lilith_calc2(sun, lilith):
			deg = sun - lilith
			q = 12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0:
				return q * math.sin(1.5 * math.radians(deg))
			elif deg > 120.0:
				return q * math.cos(1.5 * math.radians(deg))
			else:
				return -q * math.cos(3.0 * math.radians(deg))

		true_lilith = true_lilith_calc2(sun, bm)
		# print c
		"""
		if sbm < 60.0:
			print 'sbm 0-60'
			c=  q * math.sin(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 60.0 and sbm < 120.0:
			print 'sbm 60-120'
			c= -q * math.cos(3*math.radians(sbm)) - 0.0917
		elif sbm >= 120.0 and sbm < 240.0:
			print 'sbm 120-240'
			c= q * math.cos(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 240.0 and sbm < 300.0:
			print 'sbm 240-300'
			c= q * math.cos(3*math.radians(sbm)) - 0.0917
		else:
			print 'sbm 300-360'
			c= -q * math.sin(1.5*math.radians(sbm)) - 0.0917
		"""
		c += - 0.117 * math.sin(math.radians(sun - ps))
		# print c

		# c+= x * -0.163 * math.sin(math.radians(sun-ps))
		# c+= x * -0.128 * math.sin(2*math.radians(moon-sun))
		# c+= x * 0.120 * math.sin(2*math.radians(moon-bm))
		# c+= x * 0.107 * math.sin(2*math.radians(pl-bm))
		# c+= x * 0.063 * math.sin(math.radians(3*sun-ps-2*bm))
		# c+= x * 0.040 * math.sin(math.radians(moon+pl-2*sun))
		# c+= x * -0.040 * math.sin(math.radians(moon+pl-2*bm))
		# c+= x * 0.027 * math.sin(math.radians(moon-pl))
		# c+= x * -0.027 * math.sin(math.radians(sun+ps-2*bm))
		# c+= x * 0.015 * math.sin(2*math.radians(sun-pl))
		# c+= x * -0.013 * math.sin(math.radians(moon+2*bm-pl-2*sun))
		# c+= x * -0.013 * math.sin(math.radians(moon-2*bm-pl+2*sun))
		# c+= x * -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		# c+= x * 0.005 * math.sin(math.radians(3*moon-pl-2*bm))
		# c+= x * -0.005 * math.sin(math.radians(3*moon-pl-2*sun))

		# list index 27 is day pars
		self.planets_degree_ut[35] = asc + (moon - sun)
		# list index 28 is night pars
		self.planets_degree_ut[36] = asc + (sun - moon)
		# list index 29 is South Node
		# self.planets_degree_ut[37] = self.planets_degree_ut[10] - 180.0
		self.planets_degree_ut[37] = self.planets_degree_ut[11] - 180.0
		# list index 30 is marriage pars
		self.planets_degree_ut[38] = (asc + dsc) - venus
		# list index 31 is black sun
		self.planets_degree_ut[39] = swe.nod_aps_ut(self.jul_day_UT, 0, swe.NODBIT_MEAN, swe.FLG_SWIEPH)[3][0]
		# list index 32 is vulcanus
		self.planets_degree_ut[40] = 31.1 + (self.jul_day_UT - 2425246.5) * 0.00150579
		# list index 33 is persephone
		self.planets_degree_ut[41] = 240.0 + (self.jul_day_UT - 2425246.5) * 0.002737829
		# list index 34 is true lilith (own calculation)
		self.planets_degree_ut[42] = self.planets_degree_ut[12] + true_lilith
		# swiss ephemeris version of true lilith
		# self.planets_degree_ut[34] = swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_OSCU,swe.FLG_SWIEPH)[3][0]

		# adjust list index 32 and 33
		if hasattr(self, "_first_house_planet_index"):
			start_index = self._first_house_planet_index()
		else:
			start_index = len(self.planets_degree_ut)
		for i in range(start_index, len(self.planets_degree_ut)):
			while (self.planets_degree_ut[i] < 0): self.planets_degree_ut[i] += 360.0
			while (self.planets_degree_ut[i] > 360.0): self.planets_degree_ut[i] -= 360.0

			# get zodiac sign
			for x in range(12):
				deg_low = float(x * 30.0)
				deg_high = float((x + 1.0) * 30.0)
				if self.planets_degree_ut[i] >= deg_low:
					if self.planets_degree_ut[i] <= deg_high:
						self.planets_sign[i] = x
						self.planets_degree[i] = self.planets_degree_ut[i] - deg_low
						self.planets_retrograde[i] = False

		# lunar phase, anti-clockwise degrees between sun and moon
		ddeg = moon - sun
		if ddeg < 0: ddeg += 360.0
		step = 360.0 / 28.0
		# print(moon,sun,ddeg)
		for x in range(28):
			low = x * step
			high = (x + 1) * step
			if ddeg >= low and ddeg < high: mphase = x + 1
		sunstep = [0, 30, 40, 50, 60, 70, 80, 90, 120, 130, 140, 150, 160, 170, 180, 210, 220, 230, 240, 250, 260, 270,
				   300, 310, 320, 330, 340, 350]
		for x in range(len(sunstep)):
			low = sunstep[x]
			# ToDo Fix 27
			if x == 27:
				high = 360
			else:
				high = sunstep[x + 1]
			if ddeg >= low and ddeg < high: sphase = x + 1
		self.lunar_phase = {
			"degrees": ddeg,
			"moon_phase": mphase,
			"sun_phase": sphase
		}

		# close swiss ephemeris
		swe.close()
		return self
	def ephData_fixar_earth(self, year, month, day, hour, t_year, t_month, t_day, t_hour, geolon, geolat, altitude, planets, zodiac, openastrocfg,
			 houses_override=None):
		# ephemeris path (default "/usr/share/swisseph:/usr/local/share/swisseph")
		swe.set_ephe_path(ephe_path)
		# print (ephe_path)
		# basic location
		self.jul_day_UT = swe.julday(t_year, t_month, t_day, t_hour)
		self.geo_loc = swe.set_topo(geolon, geolat, altitude)

		# output variables
		self.planets_sign = list(range(len(planets)))
		self.planets_degree = list(range(len(planets)))
		self.planets_degree_ut = list(range(len(planets)))
		self.planets_info_string = list(range(len(planets)))
		self.planets_retrograde = list(range(len(planets)))
		self.planet_longitude = list(range(len(planets)))
		self.planet_latitude = list(range(len(planets)))
		self.planet_hour_angle = list(range(len(planets)))
		self.planet_azimuth = list(range(len(planets)))
		self.planet_true_altitude = list(range(len(planets)))
		self.planet_apparent_altitude = list(range(len(planets)))

		# iflag
		"""
		#define SEFLG_JPLEPH         1L     // use JPL ephemeris
		#define SEFLG_SWIEPH         2L     // use SWISSEPH ephemeris, default
		#define SEFLG_MOSEPH         4L     // use Moshier ephemeris
		#define SEFLG_HELCTR         8L     // return heliocentric position
		#define SEFLG_TRUEPOS        16L     // return true positions, not apparent
		#define SEFLG_J2000          32L     // no precession, i.e. give J2000 equinox
		#define SEFLG_NONUT          64L     // no nutation, i.e. mean equinox of date
		#define SEFLG_SPEED3         128L     // speed from 3 positions (do not use it, SEFLG_SPEED is // faster and preciser.)
		#define SEFLG_SPEED          256L     // high precision speed (analyt. comp.)
		#define SEFLG_NOGDEFL        512L     // turn off gravitational deflection
		#define SEFLG_NOABERR        1024L     // turn off 'annual' aberration of light
		#define SEFLG_EQUATORIAL     2048L     // equatorial positions are wanted
		#define SEFLG_XYZ            4096L     // cartesian, not polar, coordinates
		#define SEFLG_RADIANS        8192L     // coordinates in radians, not degrees
		#define SEFLG_BARYCTR        16384L     // barycentric positions
		#define SEFLG_TOPOCTR      (32*1024L)     // topocentric positions
		#define SEFLG_SIDEREAL     (64*1024L)     // sidereal positions 		
		"""
		# check for apparent geocentric (default), true geocentric, topocentric or heliocentric
		iflag = swe.FLG_SWIEPH + swe.FLG_SPEED
		if (openastrocfg['postype'] == "truegeo"):
			iflag += swe.FLG_TRUEPOS
		elif (openastrocfg['postype'] == "topo"):
			iflag += swe.FLG_TOPOCTR
		elif (openastrocfg['postype'] == "helio"):
			iflag += swe.FLG_HELCTR

		# sidereal
		if (openastrocfg['zodiactype'] == "sidereal"):
			iflag += swe.FLG_SIDEREAL
			mode = "SIDM_" + openastrocfg['siderealmode']
			swe.set_sid_mode(getattr(swe, mode))


		h, m, s = self.decHour(hour)
		t_h, t_m, t_s = self.decHour(t_hour)
		ts = load.timescale()
		t1 = ts.utc(year, month, day, h, m, s)
		t2 = ts.utc(t_year, t_month, t_day, t_h, t_m, t_s)
		planet_name_dic = {10: 'sun', 301: 'moon', 1: 'mercury', 2: 'venus', 4: 'mars', 5: 'jupiter', 6: 'saturn',
						   7: 'uran',
						   8: 'neptun',
						   9: 'pluton'}
		[lat_arr, lon_arr] = get_fixar_earth_ecliptic_latlon_arr(planet_name_dic, t1, t2, 0, 0)


		# compute a planet (longitude,latitude,distance,long.speed,lat.speed,speed)
		for i in range(23):
			ret_flag = swe.calc_ut(self.jul_day_UT, i, iflag)
			if(i<10):
				ret_flag_0_0 = lon_arr[i]
				ret_flag_0_1 = lat_arr[i]
			else:
				ret_flag_0_0 = ret_flag[0][0]
				ret_flag_0_1 = ret_flag[0][1]

			for x in range(len(zodiac)):
				deg_low = float(x * 30)
				deg_high = float((x + 1) * 30)
				if ret_flag_0_0 >= deg_low:
					if ret_flag_0_0 <= deg_high:
						self.planets_sign[i] = x
						self.planets_degree[i] = ret_flag_0_0 - deg_low
						self.planets_degree_ut[i] = ret_flag_0_0
						# if latitude speed is negative, there is retrograde
						if ret_flag[0][3] < 0:
							self.planets_retrograde[i] = True
						else:
							self.planets_retrograde[i] = False

						# Calc hour_angle in degrees
						self.planet_longitude[i] = ret_flag_0_0
						self.planet_latitude[i] = ret_flag_0_1

						# self.planet_hour_angle[i] = swe.degnorm(swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon -10.5)
						self.planet_hour_angle[i] = swe.degnorm(
							swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon)

						observer_latitude = geolat
						observer_longitude = geolon

						# swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
						planet_pos = ret_flag
						# azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.EQU2HOR,
						azimuth, true_altitude, apparent_altitude = swe.azalt(self.jul_day_UT, swe.ECL2HOR,
																			  [observer_longitude, observer_latitude,
																			   287], 0, 0,
																			  [planet_pos[0][0], planet_pos[0][1],
																			   planet_pos[0][2], planet_pos[0][3],
																			   planet_pos[0][4], planet_pos[0][5]])
						azimuth = azimuth + 180
						if (azimuth > 360):
							azimuth = azimuth - 360
						self.planet_azimuth[i] = azimuth
						self.planet_true_altitude[i] = true_altitude
						self.planet_apparent_altitude[i] = apparent_altitude
		# available house systems:
		"""
		hsys= 		‘P’     Placidus
				‘K’     Koch
				‘O’     Porphyrius
				‘R’     Regiomontanus
				‘C’     Campanus
				‘A’ or ‘E’     Equal (cusp 1 is Ascendant)
				‘V’     Vehlow equal (Asc. in middle of house 1)
				‘X’     axial rotation system
				‘H’     azimuthal or horizontal system
				‘T’     Polich/Page (“topocentric” system)
				‘B’     Alcabitus
				‘G’     Gauquelin sectors
				‘M’     Morinus
		"""
		# houses calculation (hsys=P for Placidus)
		# check for polar circle latitude < -66 > 66
		if houses_override:
			self.jul_day_UT = swe.julday(houses_override[0], houses_override[1], houses_override[2], houses_override[3])

		if geolat > 66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = 66.0
				# print("polar circle override for houses, using 66 degrees")
		elif geolat < -66.0:
			if 'houses_system_polar' in openastrocfg and openastrocfg['houses_system_polar'] in self.houses_system_polar_list:
				openastrocfg['houses_system'] = openastrocfg['houses_system_polar']
			else:
				geolat = -66.0
				# print("polar circle override for houses, using -66 degrees")

		# sidereal houses
		if (openastrocfg['zodiactype'] == "sidereal"):
			sh = swe.houses_ex(self.jul_day_UT, geolat, geolon, openastrocfg['houses_system'].encode("ascii"),
							   swe.FLG_SIDEREAL)
		else:
			sh = swe.houses(self.jul_day_UT, geolat, geolon, openastrocfg['houses_system'].encode("ascii"))

		self.houses_degree_ut = list(sh[0])

		# arabic parts
		sun, moon, asc = self.planets_degree_ut[0], self.planets_degree_ut[1], self.houses_degree_ut[0]
		dsc, venus = self.houses_degree_ut[6], self.planets_degree_ut[3]

		# offset
		offset = moon - sun

		# if planet degrees is greater than 360 substract 360 or below 0 add 360
		for i in range(len(self.houses_degree_ut)):
			# add offset
			# self.houses_degree_ut[i] += offset

			if self.houses_degree_ut[i] > 360.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] - 360.0
			elif self.houses_degree_ut[i] < 0.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] + 360.0

		self.houses_degree = list(range(len(self.houses_degree_ut)))
		self.houses_sign = list(range(len(self.houses_degree_ut)))
		for i in range(12):
			for x in range(len(zodiac)):
				deg_low = float(x * 30)
				deg_high = float((x + 1) * 30)
				if self.houses_degree_ut[i] >= deg_low:
					if self.houses_degree_ut[i] <= deg_high:
						self.houses_sign[i] = x
						self.houses_degree[i] = self.houses_degree_ut[i] - deg_low

		# mean apogee
		bm = self.planets_degree_ut[12]
		# mean north node
		mn = self.planets_degree_ut[10]
		# perigee lunaire moyen
		pl = self.planets_degree_ut[22]
		# perigee solaire moyen
		# define SE_NODBIT_MEAN          1
		# define SE_NODBIT_OSCU          2
		# define SE_NODBIT_OSCU_BAR     4
		# define SE_NODBIT_FOPOINT     256
		# Return: 4 tuples of 6 float (asc, des, per, aph)
		ps = swe.nod_aps_ut(self.jul_day_UT, 0, swe.NODBIT_MEAN, iflag)
		pl = swe.nod_aps_ut(self.jul_day_UT, 1, swe.NODBIT_MEAN, iflag)
		ps = ps[2][0]
		pl = pl[2][0]
		# print mn
		# print sun
		# print ps
		# print moon
		# print pl

		c = 1.517 * math.sin(2 * math.radians(sun - mn))
		c += -0.163 * math.sin(math.radians(sun - ps))
		c += -0.128 * math.sin(2 * math.radians(moon - sun))
		c += 0.120 * math.sin(2 * math.radians(moon - mn))
		c += 0.107 * math.sin(2 * math.radians(pl - mn))
		c += 0.063 * math.sin(math.radians(3 * sun - ps - 2 * mn))
		c += 0.040 * math.sin(math.radians(moon + pl - 2 * sun))
		c += -0.040 * math.sin(math.radians(moon + pl - 2 * mn))
		c += 0.027 * math.sin(math.radians(moon - pl))
		c += -0.027 * math.sin(math.radians(sun + ps - 2 * mn))
		c += 0.015 * math.sin(2 * math.radians(sun - pl))
		c += -0.013 * math.sin(math.radians(moon + 2 * mn - pl - 2 * sun))
		c += -0.013 * math.sin(math.radians(moon - 2 * mn - pl + 2 * sun))
		c += -0.007 * math.sin(math.radians(2 * moon + pl - 3 * sun))
		c += 0.005 * math.sin(math.radians(3 * moon - pl - 2 * mn))
		c += -0.005 * math.sin(math.radians(3 * moon - pl - 2 * sun))
		# print c

		sbm = sun - bm
		if sbm < 0: sbm += 360
		if sbm > 180.0: sbm -= 180
		# print("sun %s black moon %s sun-bm %s=%s" % (sun,bm,sun-bm,sbm))

		q = 12.333
		if sbm < 60.0:
			# print('sbm<60')
			c = q * math.sin(1.5 * math.radians(sbm))
		elif sbm > 120.0:
			# print('sbm>120')
			c = q * math.cos(1.5 * math.radians(sbm))
		else:
			# print('sbm 60-120')
			c = -q * math.cos(3.0 * math.radians(sbm))

		true_lilith = c

		def true_lilith_calc(sun, lilith):
			deg = sun - lilith
			q = 12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0:
				return q * math.sin(1.5 * math.radians(deg)) - 1.892 * math.sin(3 * math.radians(deg))
			elif deg > 120.0:
				return q * math.cos(1.5 * math.radians(deg)) + 1.892 * math.sin(3 * math.radians(deg))
			elif deg < 100.0:
				return -q * math.cos(3.0 * math.radians(deg)) + 0.821 * math.cos(4.5 * math.radians(deg))
			else:
				return -q * math.cos(3.0 * math.radians(deg))

		def true_lilith_calc2(sun, lilith):
			deg = sun - lilith
			q = 12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0:
				return q * math.sin(1.5 * math.radians(deg))
			elif deg > 120.0:
				return q * math.cos(1.5 * math.radians(deg))
			else:
				return -q * math.cos(3.0 * math.radians(deg))

		true_lilith = true_lilith_calc2(sun, bm)
		# print c
		"""
		if sbm < 60.0:
			print 'sbm 0-60'
			c=  q * math.sin(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 60.0 and sbm < 120.0:
			print 'sbm 60-120'
			c= -q * math.cos(3*math.radians(sbm)) - 0.0917
		elif sbm >= 120.0 and sbm < 240.0:
			print 'sbm 120-240'
			c= q * math.cos(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 240.0 and sbm < 300.0:
			print 'sbm 240-300'
			c= q * math.cos(3*math.radians(sbm)) - 0.0917
		else:
			print 'sbm 300-360'
			c= -q * math.sin(1.5*math.radians(sbm)) - 0.0917
		"""
		c += - 0.117 * math.sin(math.radians(sun - ps))
		# print c

		# c+= x * -0.163 * math.sin(math.radians(sun-ps))
		# c+= x * -0.128 * math.sin(2*math.radians(moon-sun))
		# c+= x * 0.120 * math.sin(2*math.radians(moon-bm))
		# c+= x * 0.107 * math.sin(2*math.radians(pl-bm))
		# c+= x * 0.063 * math.sin(math.radians(3*sun-ps-2*bm))
		# c+= x * 0.040 * math.sin(math.radians(moon+pl-2*sun))
		# c+= x * -0.040 * math.sin(math.radians(moon+pl-2*bm))
		# c+= x * 0.027 * math.sin(math.radians(moon-pl))
		# c+= x * -0.027 * math.sin(math.radians(sun+ps-2*bm))
		# c+= x * 0.015 * math.sin(2*math.radians(sun-pl))
		# c+= x * -0.013 * math.sin(math.radians(moon+2*bm-pl-2*sun))
		# c+= x * -0.013 * math.sin(math.radians(moon-2*bm-pl+2*sun))
		# c+= x * -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		# c+= x * 0.005 * math.sin(math.radians(3*moon-pl-2*bm))
		# c+= x * -0.005 * math.sin(math.radians(3*moon-pl-2*sun))

		# compute additional points and angles
		# list index 27 is day pars
		self.planets_degree_ut[35] = asc + (moon - sun)
		# list index 28 is night pars
		self.planets_degree_ut[36] = asc + (sun - moon)
		# list index 29 is South Node
		# self.planets_degree_ut[37] = self.planets_degree_ut[10] - 180.0
		self.planets_degree_ut[37] = self.planets_degree_ut[11] - 180.0
		# list index 30 is marriage pars
		self.planets_degree_ut[38] = (asc + dsc) - venus
		# list index 31 is black sun
		self.planets_degree_ut[39] = swe.nod_aps_ut(self.jul_day_UT, 0, swe.NODBIT_MEAN, swe.FLG_SWIEPH)[3][0]
		# list index 32 is vulcanus
		self.planets_degree_ut[40] = 31.1 + (self.jul_day_UT - 2425246.5) * 0.00150579
		# list index 33 is persephone
		self.planets_degree_ut[41] = 240.0 + (self.jul_day_UT - 2425246.5) * 0.002737829
		# list index 34 is true lilith (own calculation)
		self.planets_degree_ut[42] = self.planets_degree_ut[12] + true_lilith
		# swiss ephemeris version of true lilith
		# self.planets_degree_ut[34] = swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_OSCU,swe.FLG_SWIEPH)[3][0]

		# adjust list index 32 and 33
		if hasattr(self, "_first_house_planet_index"):
			start_index = self._first_house_planet_index()
		else:
			start_index = len(self.planets_degree_ut)
		for i in range(start_index, len(self.planets_degree_ut)):
			while (self.planets_degree_ut[i] < 0): self.planets_degree_ut[i] += 360.0
			while (self.planets_degree_ut[i] > 360.0): self.planets_degree_ut[i] -= 360.0

			# get zodiac sign
			for x in range(12):
				deg_low = float(x * 30.0)
				deg_high = float((x + 1.0) * 30.0)
				if self.planets_degree_ut[i] >= deg_low:
					if self.planets_degree_ut[i] <= deg_high:
						self.planets_sign[i] = x
						self.planets_degree[i] = self.planets_degree_ut[i] - deg_low
						self.planets_retrograde[i] = False

		# lunar phase, anti-clockwise degrees between sun and moon
		ddeg = moon - sun
		if ddeg < 0: ddeg += 360.0
		step = 360.0 / 28.0
		# print(moon,sun,ddeg)
		for x in range(28):
			low = x * step
			high = (x + 1) * step
			if ddeg >= low and ddeg < high: mphase = x + 1
		sunstep = [0, 30, 40, 50, 60, 70, 80, 90, 120, 130, 140, 150, 160, 170, 180, 210, 220, 230, 240, 250, 260, 270,
				   300, 310, 320, 330, 340, 350]
		for x in range(len(sunstep)):
			low = sunstep[x]
			# ToDo Fix 27
			if x == 27:
				high = 360
			else:
				high = sunstep[x + 1]
			if ddeg >= low and ddeg < high: sphase = x + 1
		self.lunar_phase = {
			"degrees": ddeg,
			"moon_phase": mphase,
			"sun_phase": sphase
		}

		# close swiss ephemeris
		swe.close()
		return self


		# Use decHour from utils instead of local implementation
		# Removed duplicate function - imported from utils.py

def years_diff(y1: int, m1: int, d1: int, h1: float, y2: int, m2: int, d2: int, h2: float) -> datetime.datetime:
	# swe.set_ephe_path(ephe_path)
	jd1 = swe.julday(y1,m1,d1,h1)
	jd2 = swe.julday(y2,m2,d2,h2)
	# jd = jd1 + swe._years_diff(jd1, jd2)
	jd = jd1 + ( (jd2-jd1) / 365.248193724 )
	# y, mth, d, h, m, s = swe.revjul(jd, swe.GREG_CAL)
	y, mth, d, hour = swe.revjul(jd, swe.GREG_CAL)
	h, m, s = decHour(hour)  # Use imported decHour function
	return datetime.datetime(y,mth,d,h,m,s)
