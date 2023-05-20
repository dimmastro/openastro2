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
import os.path, sys, datetime, math
from pathlib import Path
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

class ephData:
	def __init__(self,year,month,day,hour,geolon,geolat,altitude,planets,zodiac,openastrocfg,houses_override=None):
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

		#compute a planet (longitude,latitude,distance,long.speed,lat.speed,speed)
		for i in range(23):
			ret_flag = swe.calc_ut(self.jul_day_UT,i,iflag)
			for x in range(len(zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if ret_flag[0][0] >= deg_low:
					if ret_flag[0][0] <= deg_high:
						self.planets_sign[i]=x
						self.planets_degree[i] = ret_flag[0][0] - deg_low
						self.planets_degree_ut[i] = ret_flag[0][0]
						#if latitude speed is negative, there is retrograde
						if ret_flag[0][3] < 0:
							self.planets_retrograde[i] = True
						else:
							self.planets_retrograde[i] = False

						# Вычислите часовой угол планеты в градусах
						# Calc hour_angle in degrees
						self.planet_longitude[i] = ret_flag[0][0]
						self.planet_latitude[i] = ret_flag[0][1]
						# Вычислите часовой угол планеты в градусах
						self.planet_hour_angle[i] = swe.degnorm(swe.sidtime(self.jul_day_UT) - self.planet_longitude[i] - geolon -11)
						print ('self.jul_day_UT')
						print (self.jul_day_UT)
						print ('swe.sidtime(self.jul_day_UT)')
						print (swe.sidtime(self.jul_day_UT))
						print ('self.planet_longitude[i]')
						print (self.planet_longitude[i])
						print ('geolon')
						print (geolon)
						print ('self.planet_hour_angle[i]')
						print (self.planet_hour_angle[i])
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
			geolat = 66.0
			# print("polar circle override for houses, using 66 degrees")
		elif geolat < -66.0:
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
		

		#compute additional points and angles
		#list index 23 is asc, 24 is Mc, 25 is Dsc, 26 is Ic
		self.planets_degree_ut[23] = self.houses_degree_ut[0]
		self.planets_degree_ut[24] = self.houses_degree_ut[1]
		self.planets_degree_ut[25] = self.houses_degree_ut[2]
		self.planets_degree_ut[26] = self.houses_degree_ut[3]
		self.planets_degree_ut[27] = self.houses_degree_ut[4]
		self.planets_degree_ut[28] = self.houses_degree_ut[5]
		self.planets_degree_ut[29] = self.houses_degree_ut[6]
		self.planets_degree_ut[30] = self.houses_degree_ut[7]
		self.planets_degree_ut[31] = self.houses_degree_ut[8]
		self.planets_degree_ut[32] = self.houses_degree_ut[9]
		self.planets_degree_ut[33] = self.houses_degree_ut[10]
		self.planets_degree_ut[34] = self.houses_degree_ut[11]

		#list index 27 is day pars
		self.planets_degree_ut[35] = asc + (moon - sun)
		#list index 28 is night pars
		self.planets_degree_ut[36] = asc + (sun - moon)
		#list index 29 is South Node
		self.planets_degree_ut[37] = self.planets_degree_ut[10] - 180.0
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
		for i in range(23,43):
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

def years_diff(y1, m1, d1, h1 , y2, m2, d2, h2):
		# swe.set_ephe_path(ephe_path)
		jd1 = swe.julday(y1,m1,d1,h1)
		jd2 = swe.julday(y2,m2,d2,h2)
		jd = jd1 + swe._years_diff(jd1, jd2)
		#jd = jd1 + ( (jd2-jd1) / 365.248193724 )
		y, mth, d, h, m, s = swe._revjul(jd, swe.GREG_CAL)
		return datetime.datetime(y,mth,d,h,m,s)
