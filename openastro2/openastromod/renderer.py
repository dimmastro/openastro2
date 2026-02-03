from __future__ import annotations

import math
import os
from string import Template
from typing import Any, Callable, Optional, TYPE_CHECKING

from gettext import gettext as _

if TYPE_CHECKING:
	from openastro2.openastro2 import openAstro


class ChartRenderer:
	def __init__(self, context: "openAstro", debug_printer: Optional[Callable[[str], None]] = None) -> None:
		self.ctx = context
		self._debug_printer = debug_printer
		self._gettext = getattr(context.settings, "gettext", None)

	def _t(self, text: str) -> str:
		if callable(self._gettext):
			return self._gettext(text)
		return text

	def __setattr__(self, key: str, value: Any) -> None:
		"""
		Added __setattr__ so that any assignments like self.fire/self.tmpdir inside the renderer are proxied
		to the openAstro object; this ensures that the actual data (elements, etc.)
		remains on the instance itself after the graphics are generated.
		:param key:
		:param value:
		:return:
		"""
		if key in {"ctx", "_debug_printer"} or 'ctx' not in self.__dict__:
			super().__setattr__(key, value)
		elif hasattr(self.ctx, key):
			setattr(self.ctx, key, value)
		else:
			super().__setattr__(key, value)

	def __getattr__(self, item: str) -> Any:
		return getattr(self.ctx, item)

	def _debug(self, message: str) -> None:
		if self._debug_printer:
			self._debug_printer(message)

	def lat2str(self, coord):
		sign = self.settings.settings["label"]["north"]
		if coord < 0.0:
			sign = self.settings.settings["label"]["south"]
			coord = abs(coord)
		deg = int(coord)
		minute = int((float(coord) - deg) * 60)
		sec = int(round(float(((float(coord) - deg) * 60) - minute) * 60.0))
		return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': minute, '#3': sec, '#4': sign}

	def lon2str(self, coord):
		sign = self.settings.settings["label"]["east"]
		if coord < 0.0:
			sign = self.settings.settings["label"]["west"]
			coord = abs(coord)
		deg = int(coord)
		minute = int((float(coord) - deg) * 60)
		sec = int(round(float(((float(coord) - deg) * 60) - minute) * 60.0))
		return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': minute, '#3': sec, '#4': sign}

	def sliceToX(self, slice, r, offset):
		plus = (math.pi * offset) / 180
		radial = ((math.pi / 6) * slice) + plus
		return r * (math.cos(radial) + 1)

	def sliceToY(self, slice, r, offset):
		plus = (math.pi * offset) / 180
		radial = ((math.pi / 6) * slice) + plus
		return r * ((math.sin(radial) / -1) + 1)

	def drawAspect(self, r, ar, degA, degB, color):
		offset = (float(self.get_chart_start_point()) / -1) + float(degA)
		x1 = self.sliceToX(0, ar, offset) + (r - ar)
		y1 = self.sliceToY(0, ar, offset) + (r - ar)
		offset = (float(self.get_chart_start_point()) / -1) + float(degB)
		x2 = self.sliceToX(0, ar, offset) + (r - ar)
		y2 = self.sliceToY(0, ar, offset) + (r - ar)
		out = '			<line x1="' + str(x1) + '" y1="' + str(y1) + '" x2="' + str(x2) + '" y2="' + str(
			y2) + '" style="stroke: ' + color + '; stroke-width: 1.0; stroke-opacity: .5;"/>\n'
		return out

	def zodiacSlice(self, num, r, style, type):
		if self.settings.settings["astrocfg"]["houses_system"] == "G":
			offset = 360 - self.houses_degree_ut[18]
		else:
			offset = 360 - self.get_chart_start_point()
		if self.type == "Transit" or self.type == "Direction":
			dropin = 0
		else:
			dropin = self.c1
		slice_path = '<path d="M' + str(r) + ',' + str(r) + ' L' + str(dropin + self.sliceToX(num, r - dropin, offset)) + ',' + str(
			dropin + self.sliceToY(num, r - dropin, offset)) + ' A' + str(r - dropin) + ',' + str(
			r - dropin) + ' 0 0,0 ' + str(dropin + self.sliceToX(num + 1, r - dropin, offset)) + ',' + str(
			dropin + self.sliceToY(num + 1, r - dropin, offset)) + ' z" style="' + style + '"/>'
		offset = offset + 15
		dropin = self.c2 / 2
		sign_x = dropin + self.sliceToX(num, r - dropin, offset)
		sign_y = dropin + self.sliceToY(num, r - dropin, offset)
		scale = 0.3
		sign = '<g transform="translate(-' + str(16 * scale) + ',-' + str(16 * scale) + ')"><g transform="scale(' + str(
			scale) + ')"><use x="' + str(sign_x * (1 / scale)) + '" y="' + str(
			sign_y * (1 / scale)) + '" xlink:href="#' + type + '" stroke="black" fill="black" /></g></g>\n'
		return slice_path + '\n' + sign

	def makeZodiac(self, r):
		output = ""
		for i in range(len(self.zodiac)):
			output += self.zodiacSlice(i, r,
			                           "fill:" + self.settings.settings["color_codes"]["zodiac_bg_%s" % (i)] + "; fill-opacity: 0.5;",
			                           self.zodiac[i]) + '\n'
		return output

	def makeHouses(self, r):
		path = ""
		if self.settings.settings["astrocfg"]["houses_system"] == "G":
			xr = 36
		else:
			xr = 12
		for i in range(xr):
			if self.type == "Transit" or self.type == "Direction":
				dropin = self.c3
				roff = self.c1 - self.settings.settings["settings_svg"]['roff']
				t_roff = self.c1 - self.settings.settings["settings_svg"]['t_roff']
			else:
				dropin = self.c3
				roff = self.c1 - self.settings.settings["settings_svg"]['roff']

			offset = (float(self.get_chart_start_point()) / -1) + float(self.houses_degree_ut[i])
			x1 = self.sliceToX(0, (r - dropin), offset) + dropin
			y1 = self.sliceToY(0, (r - dropin), offset) + dropin
			x2 = self.sliceToX(0, r - roff, offset) + roff
			y2 = self.sliceToY(0, r - roff, offset) + roff

			if i < (xr - 1):
				text_offset = offset + int(self.degreeDiff(self.houses_degree_ut[(i)], self.houses_degree_ut[i]) / 1)
			else:
				text_offset = offset + int(self.degreeDiff(self.houses_degree_ut[0], self.houses_degree_ut[0]) / 1)

			default_house_color = self.settings.settings["color_codes"]['houses_radix_line']
			if self.is_angle_house_number(i):
				linecolor = self.get_house_color(i, default_house_color)
			else:
				linecolor = default_house_color
			if self.type == "Transit" or self.type == "Direction":
				linecolor = self.settings.settings["color_codes"]['houses_transit_line_1']

			if self.type == "Transit" or self.type == "Direction":
				zeropoint = 360 - self.get_chart_start_point()
				t_offset = zeropoint + self.t_houses_degree_ut[i]
				t_offset = zeropoint + self.t_houses_degree_ut[i]
				if t_offset > 360:
					t_offset = t_offset - 360
				t_x1 = self.sliceToX(0, (r - t_roff), t_offset) + t_roff
				t_y1 = self.sliceToY(0, (r - t_roff), t_offset) + t_roff
				t_x2 = self.sliceToX(0, r, t_offset)
				t_y2 = self.sliceToY(0, r, t_offset)
				if i < 11:
					t_text_offset = t_offset
				else:
					t_text_offset = t_offset
				if i == 0 or i == 9 or i == 6 or i == 3:
					t_linecolor = self.settings.settings["color_codes"]['houses_transit_line_2']
				else:
					t_linecolor = self.settings.settings["color_codes"]['houses_transit_line_2']
				dropin = self.c1 - self.settings.settings["settings_svg"]['t_roff_deg']
				h_text = str(i + 1)
				xtext = self.sliceToX(0, (r - dropin), t_text_offset) + dropin
				ytext = self.sliceToY(0, (r - dropin), t_text_offset) + dropin
				house_entry = self.get_house_planet_entry(i) or self._house_entry_by_number(i)
				show_transit_house = True
				if house_entry is not None:
					if 't_visible' in house_entry:
						show_transit_house = house_entry['t_visible'] == 1
					else:
						show_transit_house = house_entry.get('visible', 1) == 1
				house_planet_index = self.get_house_planet_index(i)
				if house_planet_index is not None:
					house_planet = self.planets[house_planet_index]
					if 't_visible' in house_planet or 'planet_orb' in house_planet:
						show_transit_house = show_transit_house and self.ifShowPlanetInTransit(house_planet_index)
				if show_transit_house:
					path = path + '<line x1="' + str(t_x1) + '" y1="' + str(t_y1) + '" x2="' + str(t_x2) + '" y2="' + str(
						t_y2) + '" style="stroke: ' + t_linecolor + '; stroke-width: 1px; stroke-dasharray:0; stroke-opacity:.4;"/>\n'
					path = path + '<text style="fill: ' + t_linecolor + '; fill-opacity: .6; font-size: 9px"><tspan x="' + str(
						xtext - 3) + '" y="' + str(ytext + 3) + '">' + h_text + '</tspan></text>\n'
					path = path + '<text text-anchor="start" x="' + str(
						xtext + self.settings.settings["settings_svg"]["offset_degree_planet_x"]) + '" y="' + str(
						ytext + self.settings.settings["settings_svg"]["offset_degree_planet_y"]) + '"  style="fill:' + t_linecolor + '; font-size: 7px;">' + self.dec2deg(
						self.t_houses_degree[(i)] + 1, type="0") + '</text>'

			if self.type == "Transit" or self.type == "Direction":
				dropin = self.c1 - self.settings.settings["settings_svg"]['roff_deg']
			elif self.settings.settings["astrocfg"]["chartview"] == "european":
				dropin = self.c1 - self.settings.settings["settings_svg"]['roff_deg']
			else:
				dropin = 48

			if i == 0:
				h_text = str(i + 1)
			elif i == 9:
				h_text = str(i + 1)
			elif i == 6:
				h_text = str(i + 1)
			elif i == 3:
				h_text = str(i + 1)
			else:
				h_text = str(i + 1)

			xtext = self.sliceToX(0, (r - dropin), text_offset) + dropin
			ytext = self.sliceToY(0, (r - dropin), text_offset) + dropin
			path = path + '<line x1="' + str(x1) + '" y1="' + str(y1) + '" x2="' + str(x2) + '" y2="' + str(
				y2) + '" style="stroke: ' + linecolor + '; stroke-width: 1px; stroke-dasharray:0; stroke-opacity:.4;"/>\n'
			path = path + '<text style="fill: ' + linecolor + '; fill-opacity: .6; font-size: 9px"><tspan x="' + str(
				xtext - 3) + '" y="' + str(ytext + 3) + '">' + h_text + '</tspan></text>\n'
			path = path + '<text text-anchor="start" x="' + str(
				xtext + self.settings.settings["settings_svg"]["offset_degree_planet_x"]) + '" y="' + str(
				ytext + self.settings.settings["settings_svg"]["offset_degree_planet_y"]) + '"  style="fill:' + linecolor + '; font-size: 7px;">' + self.dec2deg(
				self.houses_degree[(i)] + 1, type="0") + '</text>'

		return path

	def makePlanets( self , r ):

		planets_degut={}

		diff=range(len(self.planets))

		planets_degut = self.getPlanetsDegut(self.planets_degree_ut, flag_transit="Radix")

		for i in range(len(self.planets)):
			# if self.planets[i]['visible'] == 1:
			# 	if not (22 < i and i < 35): # exclude houses
			# 		#list of planets sorted by degree
			# 		planets_degut[self.planets_degree_ut[i]]=i

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
			if not self._is_house_index(i):
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


		planets_delta = self.getPlanetsDelta(self.planets_degree_ut)
		keys = list(planets_degut.keys())
		keys.sort()
		switch = 0
		for e in range(len(keys)):
			i=planets_degut[keys[e]]

			#coordinates
			if self.type == "Transit" or self.type == "Direction":
				if self._is_angle_index(i):
					rplanet = self.c2 - (self.c2-self.c3)/2
				elif switch == 1:
					rplanet = self.c2 - (self.c2-self.c3)/2
					switch = 0
				else:
					rplanet = self.c2 - (self.c2-self.c3)/2
					switch = 1
			else:
				#if angle houses (asc,mc,dsc,ic)
				#put on special line (rplanet is range from outer ring)
				amin,bmin,cmin=0,0,0
				if self.settings.settings["astrocfg"]["chartview"] == "european":
					amin=74-30
					bmin=94-30
					cmin=40-30

				if self._is_angle_index(i):
					rplanet = 50-cmin
				elif switch == 1:
					rplanet=84-amin
					switch = 0
				else:
					rplanet=104-bmin
					switch = 1

			# rtext=45
			if self.settings.settings["astrocfg"]['houses_system'] == "G":
				offset = (int(self.houses_degree_ut[18]) / -1) + float(self.planets_degree_ut[i])
				# trueoffset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i])
				trueoffset = (float(self.get_chart_start_point()) / -1) + float(self.planets_degree_ut[i])
			else:
				# offset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i]+planets_delta[e])
				offset = (float(self.get_chart_start_point()) / -1) + float(self.planets_degree_ut[i] + planets_delta[i])
				# trueoffset = (int(self.houses_degree_ut[6]) / -1) + int(self.planets_degree_ut[i])
				trueoffset = (float(self.get_chart_start_point()) / -1) + float(self.planets_degree_ut[i])
			planet_x = self.sliceToX( 0 , (r-rplanet) , offset ) + rplanet
			planet_y = self.sliceToY( 0 , (r-rplanet) , offset ) + rplanet

			# Paint inner radix planets for Transit
			if self.type == "Transit" or self.type == "Direction":
				if "t_planet_symbol_scale_1" in self.settings.settings["settings_svg"]:
					scale = self.settings.settings["settings_svg"]["t_planet_symbol_scale_1"]
				else:
					scale = 0.6
				#line1
				# x1=self.sliceToX( 0 , (r-self.c3) , trueoffset ) + self.c3
				# y1=self.sliceToY( 0 , (r-self.c3) , trueoffset ) + self.c3
				# x2=self.sliceToX( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				# y2=self.sliceToY( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				# color=self.planets[i]["color"]
				color=self.settings.settings["color_codes"]["color_transit_1"]
				# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
				#line2
				line_shift_start = self.c3 - 60 + 10
				x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
				x2=self.sliceToX( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				y2=self.sliceToY( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:0.5;"/>\n' % (x1,y1,x2,y2,color)

				x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['color_transit_1'])

			elif self.settings.settings["astrocfg"]["chartview"] == "european":
				if "planet_symbol_scale" in self.settings.settings["settings_svg"]:
					scale = self.settings.settings["settings_svg"]["planet_symbol_scale"]
				else:
					scale = 0.6
				#line1
				x1=self.sliceToX( 0 , (r-self.c3) , trueoffset ) + self.c3
				y1=self.sliceToY( 0 , (r-self.c3) , trueoffset ) + self.c3
				x2=self.sliceToX( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				y2=self.sliceToY( 0 , (r-rplanet-30) , trueoffset ) + rplanet + 30
				# color=self.planets[i]["color"]
				color=self.settings.settings["color_codes"]["color_radix"]
				# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
				#line2
				rplanet = self.c2 - (self.c2 - self.c3) / 2

				x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
				x2=self.sliceToX( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				y2=self.sliceToY( 0 , (r-rplanet-10) , offset ) + rplanet + 10
				if not self._is_house_index(i):
					output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.5;"/>\n' % (x1,y1,x2,y2,color)
					output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
						x1, y1, 1.5, self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['color_radix'])
			else:
				if "planet_symbol_scale" in self.settings.settings["settings_svg"]:
					scale = self.settings.settings["settings_svg"]["planet_symbol_scale"]
				else:
					scale = 1

			if not self._is_house_index(i):
				#output planet
				# output = output + '<g transform="translate(-'+str(12*scale)+',-'+str(12*scale)+')"><g transform="scale('+str(scale)+')"><use x="' + str(planet_x*(1/scale)) + '" y="' + str(planet_y*(1/scale)) + '" xlink:href="#' + self.planets[i]['name'] + '" /></g></g>\n'
				rplanet = self.c2 - (self.c2 - self.c3) / 2
				planet_x = self.sliceToX(0, (r - rplanet), offset) + rplanet
				planet_y = self.sliceToY(0, (r - rplanet), offset) + rplanet
				# output = output + '<g transform="translate(-6,-6)"><g transform="scale(0.5)"><use x="' + str(planet_x*2) + '" y="' + str(planet_y*2) + '" xlink:href="#' + self.planets[i]['name'] + '" /></g></g>\n'
				output = output + '<g transform="translate(-' + str(12 * scale) + ',-' + str(
					12 * scale) + ')"><g transform="scale(' + str(scale) + ')"><use x="' + str(
					planet_x * (1 / scale)) + '" y="' + str(planet_y * (1 / scale)) + '" xlink:href="#' + \
						 self.planets[i]['name'] + '" /></g></g>\n'

				# if i < (xr-1):
				# 	text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[(i)], self.houses_degree_ut[i] ) / 1 )
				# else:
				# 	# text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[(xr-1)] ) / 2 )
				# 	text_offset = offset + int(self.degreeDiff( self.houses_degree_ut[0], self.houses_degree_ut[0] ) / 1 )
				text_offset = offset
				# text_offset = 10
				dropin = rplanet
				xtext = self.sliceToX(0, (r - dropin), text_offset) + dropin  + self.settings.settings["settings_svg"]["offset_degree_planet_x"]
				ytext = self.sliceToY(0, (r - dropin), text_offset) + dropin  + self.settings.settings["settings_svg"]["offset_degree_planet_y"]
				output = output + '<text text-anchor="start" x="' + str(xtext + 2 * scale / 0.6) + '" y="' + str(ytext - 0) + '"  style="fill:' + self.settings.settings["color_codes"]['paper_0'] + '; font-size: ' + str(7 * scale / 0.6) + 'px;">' + self.dec2deg(self.planets_degree[(i)]+1, type="0") + '</text>'
				if self.planets_retrograde[i]:
					output = output + '<text text-anchor="start" x="' + str(xtext + 2 * scale / 0.6) + '" y="' + str(
						ytext + 10 * scale / 0.6) + '"  style="fill:' + self.settings.settings["color_codes"]['paper_0'] + '; font-size: ' + str(7 * scale / 0.6) + 'px;">' + 'r' + '</text>'
				output = output + ''

		# Paint outer transit planets for Transit
		#make transit degut and display planets
		if self.type == "Transit" or self.type == "Direction":

			if "t_planet_symbol_scale_2" in self.settings.settings["settings_svg"]:
				scale = self.settings.settings["settings_svg"]["t_planet_symbol_scale_2"]
			else:
				scale = 0.99
			# line1
			x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
			y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
			x2 = self.sliceToX(0, (r - rplanet - 30), trueoffset) + rplanet + 30
			y2 = self.sliceToY(0, (r - rplanet - 30), trueoffset) + rplanet + 30
			# color=self.planets[i]["color"]
			color = self.settings.settings["color_codes"]["color_transit_1"]
			# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.3;"/>\n' % (x1,y1,x2,y2,color)
			# line2
			x1 = self.sliceToX(0, (r - rplanet - 20), trueoffset) + rplanet + 20
			y1 = self.sliceToY(0, (r - rplanet - 20), trueoffset) + rplanet + 20
			x2 = self.sliceToX(0, (r - rplanet - 10), offset) + rplanet + 10
			y2 = self.sliceToY(0, (r - rplanet - 10), offset) + rplanet + 10
			# output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:0.2;"/>\n' % (
			# x1, y1, x2, y2, color)

			x1 = self.sliceToX(0, (r - self.c3), trueoffset) + self.c3
			y1 = self.sliceToY(0, (r - self.c3), trueoffset) + self.c3
			output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
				x1, y1, 1.5, self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['color_transit_1'])

			group_offset={}
			t_planets_degut={}
			for i in range(len(self.planets)):
				group_offset[i]=0
				# if self.planets[i]['visible'] == 1:
				if not self._is_house_index(i): # exclude houses
					if 't_visible' in self.planets[i]:
						# if self.planets[i]['t_visible'] == 1:
						# if ( (('planet_orb' in self.planets[i]
						# 	   and "visible2" in self.planets[i]['planet_orb'][self.type]
						# 	   and self.planets[i]['planet_orb'][self.type]["visible2"] == 1))
						# 		or self.planets[i]['t_visible'] == 1):
						if (self.ifShowPlanetInTransit(i)):
							t_planets_degut[self.t_planets_degree_ut[i]]=i
					elif self.planets[i]['visible'] == 1:
						t_planets_degut[self.t_planets_degree_ut[i]] = i

			t_planets_degut = self.getPlanetsDegut(self.t_planets_degree_ut, flag_transit="Transit")

			# t_keys = list(t_planets_degut.keys())
			# t_keys.sort()
			t_planets_delta = self.getPlanetsDelta(self.t_planets_degree_ut, flag_transit="Transit")




			t_keys = list(t_planets_degut.keys())
			t_keys.sort()

			switch=0
			for e in range(len(t_keys)):
				i=t_planets_degut[t_keys[e]]

				if self._is_angle_index(i):
					rplanet = self.c1 - 15
				elif switch == 1:
					rplanet=self.c1 - 15
					switch = 0
				else:
					rplanet=self.c1 - 15
					switch = 1

				# print(self.planets[i]['name'] )
				# print("self.t_planets_degree_ut[i]=",self.t_planets_degree_ut[i])
				# zeropoint = 360 - self.houses_degree_ut[6]
				zeropoint = 360 - self.get_chart_start_point()
				t_offset = zeropoint + self.t_planets_degree_ut[i]
				# if t_offset > 360:
				# 	t_offset = t_offset - 360
				# planet_x = self.sliceToX( 0 , (r-rplanet) , t_offset ) + rplanet
				# planet_y = self.sliceToY( 0 , (r-rplanet) , t_offset ) + rplanet
				if self.settings.settings["astrocfg"]['houses_system'] == "G":
					t_offset = (float(self.t_houses_degree_ut[18]) / -1) + float(self.t_planets_degree_ut[i])
					trueoffset = (float(self.t_houses_degree_ut[6]) / -1) + float(self.t_planets_degree_ut[i])
				else:
					offset = zeropoint + self.t_planets_degree_ut[i] + t_planets_delta[i]
					trueoffset = (float(self.t_houses_degree_ut[6]) / -1) + float(self.t_planets_degree_ut[i])

				# print(t_offset-360)
				x1 = self.sliceToX(0, (r - self.c3), t_offset) + self.c3
				y1 = self.sliceToY(0, (r - self.c3), t_offset) + self.c3
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]["color_transit_2"])

				x1 = self.sliceToX(0, (r - self.c1), t_offset) + self.c1
				y1 = self.sliceToY(0, (r - self.c1), t_offset) + self.c1
				output += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px; stroke-opacity: 0.5;"/>' % (
					x1, y1, 1.5, self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]["color_transit_2"])


				if not self._is_house_index(i):
					if "t_rplanet" in self.settings.settings["settings_svg"]:
						t_rplanet = self.settings.settings["settings_svg"]["t_rplanet"]
					else:
						t_rplanet = 20
					rplanet = self.c1 - t_rplanet
					planet_x = self.sliceToX(0, (r - rplanet), offset) + rplanet
					planet_y = self.sliceToY(0, (r - rplanet), offset) + rplanet
					# output = output + '<g transform="translate(-6,-6)"><g transform="scale(0.5)"><use x="' + str(planet_x*2) + '" y="' + str(planet_y*2) + '" xlink:href="#' + self.planets[i]['name'] + '" /></g></g>\n'
					output = output + '<g transform="translate(-' + str(12 * scale) + ',-' + str(
						12 * scale) + ')"><g transform="scale(' + str(scale) + ')"><use x="' + str(
						planet_x * (1 / scale)) + '" y="' + str(planet_y * (1 / scale)) + '" xlink:href="#' + \
							 self.planets[i]['name'] + '" /></g></g>\n'

					text_offset = offset
					# text_offset = 10
					dropin = rplanet
					xtext = self.sliceToX(0, (r - dropin), text_offset) + dropin + self.settings.settings["settings_svg"][
						"offset_degree_planet_x"]
					ytext = self.sliceToY(0, (r - dropin), text_offset) + dropin + self.settings.settings["settings_svg"][
						"offset_degree_planet_y"]
					output = output + '<text text-anchor="start" x="' + str(xtext + 2 * scale / 0.6) + '" y="' + str(
						ytext - 0) + '"  style="fill:' + self.settings.settings["color_codes"]["color_transit_2"] + '; font-size: ' + str(7 * scale / 0.6) + 'px;">' + self.dec2deg(
						self.t_planets_degree[(i)]+1, type="0") + '</text>'
					if self.t_planets_retrograde[i]:
						output = output + '<text text-anchor="start" x="' + str(xtext + 2 * scale / 0.6) + '" y="' + str(
							ytext + 10 * scale / 0.6) + '"  style="fill:' + self.settings.settings["color_codes"][
									 'paper_0'] + '; font-size: ' + str(7 * scale / 0.6) + 'px;">' + 'r' + '</text>'
					output = output + ''

					#line2
					x1 = self.sliceToX(0, (r - self.c1), t_offset) + self.c1
					y1 = self.sliceToY(0, (r - self.c1), t_offset) + self.c1
					x2=self.sliceToX( 0 , (r-rplanet-10) , offset ) + rplanet + 10
					y2=self.sliceToY( 0 , (r-rplanet-10) , offset ) + rplanet + 10
					# Transit planets lines
					output += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke-width:1px;stroke:%s;stroke-opacity:.2;"/>\n' % (x1,y1,x2,y2,self.settings.settings["color_codes"]["color_transit_2"])


		return output



	def getPlanetsDelta(self, temp_planets_degree_ut, flag_transit="Radix"):
		"""
		Compute angular offsets for visible planets to reduce overlap.

		Strategy:
		1) Sort bodies by their normalized longitudes (0..360).
		2) Run a symmetric spread pass that pushes neighbors apart to a minimum separation.
		   - forward pass enforces minimum spacing in ascending order
		   - backward pass enforces minimum spacing in descending order
		   - the final position is the average of both passes
		3) Convert adjusted positions to per-planet deltas (signed angular shifts).

		This keeps the original ordering (no swapping) and yields stable results.
		"""
		planets_degut = self.getPlanetsDegut(temp_planets_degree_ut, flag_transit=flag_transit)
		keys = list(planets_degut.keys())
		keys.sort()
		planet_drange = self.settings.settings["settings_svg"].get("planet_drange", 3.4)
		base_items = [(temp_planets_degree_ut[planets_degut[deg]] % 360.0, planets_degut[deg]) for deg in keys]
		if not base_items:
			return [0.0 for _ in range(len(self.planets))]

		def spread_degrees(angles, min_separation):
			"""
			Spread a sorted list of angles so adjacent values are at least min_separation apart.

			We compute two constraint-satisfying sequences:
			- advance: forward sweep, pushing each angle ahead if it is too close to its predecessor
			- retreat: backward sweep, pushing each angle backward if it is too close to its successor
			Then we average the two sequences to keep the result centered.
			"""
			step = min_separation + 0.1
			n = len(angles)
			advance = angles[:]
			retreat = angles[::-1]
			changed = True
			while changed:
				changed = False
				for i in range(n):
					prev_deg = advance[-1] - 360.0 if i == 0 else advance[i - 1]
					delta = advance[i] - prev_deg
					diff = min(delta, 360.0 - delta)
					# If too close to the previous angle, push forward by a small step.
					if (advance[i] < prev_deg) or (diff < min_separation):
						advance[i] = prev_deg + step
						changed = True
			changed = True
			while changed:
				changed = False
				for i in range(n):
					prev_deg = retreat[-1] + 360.0 if i == 0 else retreat[i - 1]
					delta = prev_deg - retreat[i]
					diff = min(delta, 360.0 - delta)
					# If too close to the next angle, push backward by a small step.
					if (prev_deg < retreat[i]) or (diff < min_separation):
						retreat[i] = prev_deg - step
						changed = True
			retreat.reverse()
			balanced = []
			for adv_deg, ret_deg in zip(advance, retreat):
				adv_deg %= 360.0
				ret_deg %= 360.0
				# Average with wrap-aware logic to avoid jumping across 0/360.
				if abs(adv_deg - ret_deg) < 180.0:
					avg = (adv_deg + ret_deg) / 2.0
				else:
					avg = ((adv_deg + ret_deg + 360.0) / 2.0) % 360.0
				balanced.append(avg)
			return balanced

		# Sort by original longitude (ascending) so order stays consistent.
		base_items.sort(key=lambda item: item[0])
		sorted_degrees = [deg for deg, _ in base_items]
		# Spread only if more than one body is present.
		adjusted = spread_degrees(sorted_degrees, planet_drange) if len(base_items) > 1 else sorted_degrees

		planets_delta = [0.0 for _ in range(len(self.planets))]
		for (orig_deg, idx), adj_deg in zip(base_items, adjusted):
			# Convert adjusted position to a signed delta (shortest angular direction).
			delta = adj_deg - orig_deg
			if delta > 180.0:
				delta -= 360.0
			elif delta < -180.0:
				delta += 360.0
			planets_delta[idx] = delta
		return planets_delta

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
			viewbox = f'0 0 {svgWidth} {svgHeight}'  # 297mm * 2.6 + 210mm * 2.6
		else:
			# sizeX = 546.0
			# sizeY = 970.7
			svgWidth = printing['width']
			svgHeight = printing['height']
			rotate = "0"
			# viewbox = '0 0 970.7 546.0'
			viewbox = f'0 0 {svgWidth} {svgHeight}'  # 297mm * 2.6 + 210mm * 2.6
			translate = "0"

		# template dictionary
		td = dict()
		r = self.settings.settings["settings_svg"]["r"]
		if (self.settings.settings["astrocfg"]['chartview'] == "european"):
			c1 = self.settings.settings["settings_svg"]["c1"]
			c2 = self.settings.settings["settings_svg"]['c2']
			c3 = self.settings.settings["settings_svg"]['c3']
		else:
			c1 = 0
			c2 = 36
			c3 = 120

		self.ctx.c1 = c1
		self.ctx.c2 = c2
		self.ctx.c3 = c3
		self.c1 = c1
		self.c2 = c2
		self.c3 = c3

		# make chart
		# transit
		if self.type == "Transit" or self.type == "Direction":
			# Ensure natal aspects populate planet_dict even for transit charts.
			self.makeAspects(r, (r - self.c3))
			for attr in ("planets_aspects", "planets_aspects_arr", "planets_aspects_arr_diff"):
				if hasattr(self.ctx, attr):
					delattr(self.ctx, attr)
			td['transitRing'] = self.transitRing(r)
			td['degreeRing'] = self.degreeTransitRing(r)
			# circles
			td['c1'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c1) + '"'
			td['c1style'] = 'fill: %s; stroke: %s;  fill-opacity:0.0; stroke-width: 0px; stroke-opacity:1.0;' % (
			self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['zodiac_transit_ring_2'])
			td['c2'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c2) + '"'
			td['c2style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-opacity:.4; stroke-width: 0px' % (
			self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['zodiac_transit_ring_1'])
			td['c3'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c3) + '"'
			td['c3style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 1px' % (
			self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['zodiac_transit_ring_0'])
			td['makeAspects'] = self.makeAspectsTransit(r, (r - self.c3))

			td['makeAspectGrid'] = ""
			if self.settings.settings["settings_svg"]["printAspectGrid"] == 1:
				td['makeAspectGrid'] = self.makeAspectGrid(r)
			td['makePatterns'] = ''
		else:
			td['transitRing'] = ""
			# td['degreeRing'] = self.degreeRing(r)
			td['degreeRing'] = ""
			# circles
			td['c1'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c1) + '"'
			td['c1style'] = 'fill: none; stroke: %s; stroke-width: 0.0px; ' % (self.settings.settings["color_codes"]['zodiac_radix_ring_2'])
			td['c2'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c2) + '"'
			td['c2style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-opacity:.3; stroke-width: 0.0px' % (
			self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['zodiac_radix_ring_1'])
			td['c3'] = 'cx="' + str(r) + '" cy="' + str(r) + '" r="' + str(r - self.c3) + '"'
			td['c3style'] = 'fill: %s; fill-opacity:1.0; stroke: %s; stroke-width: 0.5px' % (
			self.settings.settings["color_codes"]['paper_1'], self.settings.settings["color_codes"]['zodiac_radix_ring_0'])
			td['makeAspects'] = self.makeAspects(r, (r - self.c3))

			td['makeAspectGrid'] = ""
			if self.settings.settings["settings_svg"]["printAspectGrid"] == 1:
				td['makeAspectGrid'] = self.makeAspectGrid(r)

			td['makePatterns'] = self.makePatterns()

		td['circleX'] = str(self.settings.settings["settings_svg"]["circleX"])
		td['circleY'] = str(self.settings.settings["settings_svg"]["circleY"])
		td['svgWidth'] = str(svgWidth)
		td['svgHeight'] = str(svgHeight)
		td['viewbox'] = viewbox


		td['stringTitle'] = ""
		td['chartType'] = ""
		td['t_stringTitle'] = ""
		td['stringDateTime'] = ""
		td['t_stringDateTime'] = ""
		td['stringLocation'] = ""
		td['stringLat'] = ""
		td['stringLon'] = ""
		td['t_stringLocation'] = ""
		td['t_stringLat'] = ""
		td['t_stringLon'] = ""
		td['stringLat'] = ""
		td['stringLon'] = ""
		td['stringPosition'] = ""

		if self.settings.settings["settings_svg"]["printChartType"] == 1:
			td['chartType'] = self.charttype

		# Print Radix Chart description
		if self.settings.settings["settings_svg"]["printDescriptionRadix"] == 1:
			td['stringTitle'] = self.name
			# td['chartType'] = self.charttype
			td['stringDateTime'] = str(self.year_loc) + '.%(#1)02d.%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {
				'#1': self.month_loc, '#2': self.day_loc, '#3': self.hour_loc, '#4': self.minute_loc,
				'#5': self.second_loc}
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

			td['stringLat'] = "%s" % (self.lat2str(self.geolat))
			td['stringLon'] = "%s" % (self.lon2str(self.geolon))
			postype = {"geo": self.settings.settings["label"]["apparent_geocentric"], "truegeo": self.settings.settings["label"]["true_geocentric"],
					   "topo": self.settings.settings["label"]["topocentric"], "helio": self.settings.settings["label"]["heliocentric"]}
			# td['stringPosition'] = postype[self.settings.settings["astrocfg"]['postype']]
			td['stringPosition'] = self.settings.settings["astrocfg"]['postype']

		# Print Douuble-Chart description
		if self.type == "Transit" or self.type == "Direction":
			if self.settings.settings["settings_svg"]["printDescriptionDouble"] == 1:
				# td['chartType'] = self.charttype
				td['t_stringTitle'] = self.t_name
				td['t_stringDateTime'] = str(self.event2["year"]) + '.%(#1)02d.%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {
					'#1': self.event2["month"], '#2': self.event2["day"], '#3': self.event2["hour"], '#4': self.event2["minute"],
					'#5': self.event2["second"]}
				# td['stringLocation'] = td['stringLocation'] + " - " + self.t_location
				td['t_stringLocation'] = self.t_location + " " + self.decTzStr(self.t_timezone)
				# td['t_stringLat'] = "%s: %s" % (self.settings.settings["label"]['latitude'], self.lat2str(self.t_geolat))
				# td['t_stringLon'] = "%s: %s" % (self.settings.settings["label"]['longitude'], self.lon2str(self.t_geolon))
				td['t_stringLat'] = "%s" % (self.lat2str(self.t_geolat))
				td['t_stringLon'] = "%s" % (self.lon2str(self.t_geolon))

		# bottom left
		siderealmode_chartview = {
			"FAGAN_BRADLEY": self._t("Fagan Bradley"),
			"LAHIRI": self._t("Lahiri"),
			"DELUCE": self._t("Deluce"),
			"RAMAN": self._t("Ramanb"),
			"USHASHASHI": self._t("Ushashashi"),
			"KRISHNAMURTI": self._t("Krishnamurti"),
			"DJWHAL_KHUL": self._t("Djwhal Khul"),
			"YUKTESHWAR": self._t("Yukteshwar"),
			"JN_BHASIN": self._t("Jn Bhasin"),
			"BABYL_KUGLER1": self._t("Babyl Kugler 1"),
			"BABYL_KUGLER2": self._t("Babyl Kugler 2"),
			"BABYL_KUGLER3": self._t("Babyl Kugler 3"),
			"BABYL_HUBER": self._t("Babyl Huber"),
			"BABYL_ETPSC": self._t("Babyl Etpsc"),
			"ALDEBARAN_15TAU": self._t("Aldebaran 15Tau"),
			"HIPPARCHOS": self._t("Hipparchos"),
			"SASSANIAN": self._t("Sassanian"),
			"J2000": self._t("J2000"),
			"J1900": self._t("J1900"),
			"B1950": self._t("B1950")
		}

		if self.settings.settings["astrocfg"]['zodiactype'] == 'sidereal':
			td['bottomLeft1'] = self._t("Sidereal")
			td['bottomLeft2'] = siderealmode_chartview[self.settings.settings["astrocfg"]['siderealmode']]
		else:
			td['bottomLeft1'] = self._t("Tropical")
			td['bottomLeft2'] = '%s: %s (%s) %s (%s)' % (
			self._t("Lunar Phase"), self.lunar_phase['sun_phase'], self._t("Sun"), self.lunar_phase['moon_phase'], self._t("Moon"))

		td['bottomLeft3'] = '%s: %s' % (self._t("Lunar Phase"), self.dec2deg(self.lunar_phase['degrees']))
		td['bottomLeft4'] = ''

		# lunar phase
		deg = self.lunar_phase['degrees']

		if (deg < 90.0):
			maxr = deg
			if (deg > 80.0): maxr = maxr * maxr
			lfcx = 20.0 + (deg / 90.0) * (maxr + 10.0)
			lfr = 10.0 + (deg / 90.0) * maxr
			lffg, lfbg = self.settings.settings["color_codes"]["lunar_phase_0"], self.settings.settings["color_codes"]["lunar_phase_1"]

		elif (deg < 180.0):
			maxr = 180.0 - deg
			if (deg < 100.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 90.0) / 90.0 * (maxr + 10.0)) - (maxr + 10.0)
			lfr = 10.0 + maxr - ((deg - 90.0) / 90.0 * maxr)
			lffg, lfbg = self.settings.settings["color_codes"]["lunar_phase_1"], self.settings.settings["color_codes"]["lunar_phase_0"]

		elif (deg < 270.0):
			maxr = deg - 180.0
			if (deg > 260.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 180.0) / 90.0 * (maxr + 10.0))
			lfr = 10.0 + ((deg - 180.0) / 90.0 * maxr)
			lffg, lfbg = self.settings.settings["color_codes"]["lunar_phase_1"], self.settings.settings["color_codes"]["lunar_phase_0"]

		elif (deg < 361):
			maxr = 360.0 - deg
			if (deg < 280.0): maxr = maxr * maxr
			lfcx = 20.0 + ((deg - 270.0) / 90.0 * (maxr + 10.0)) - (maxr + 10.0)
			lfr = 10.0 + maxr - ((deg - 270.0) / 90.0 * maxr)
			lffg, lfbg = self.settings.settings["color_codes"]["lunar_phase_0"], self.settings.settings["color_codes"]["lunar_phase_1"]

		td['lunar_phase_fg'] = lffg
		td['lunar_phase_bg'] = lfbg
		td['lunar_phase_cx'] = '%s' % (lfcx)
		td['lunar_phase_r'] = '%s' % (lfr)
		td['lunar_phase_outline'] = self.settings.settings["color_codes"]["lunar_phase_2"]

		# rotation based on latitude
		td['lunar_phase_rotate'] = "%s" % (-90.0 - self.geolat)

		# paper_color_X
		td['paper_color_0'] = self.settings.settings["color_codes"]["paper_0"]
		td['paper_color_1'] = self.settings.settings["color_codes"]["paper_1"]

		# Planet color tokens for both numeric ids and names.
		planet_color_default = self.settings.settings["color_codes"]["planet_all"]
		for entry in self.settings.settings.get("settings_planet_dict", {}).values():
			if not isinstance(entry, dict):
				continue
			entry_id = entry.get("id")
			entry_name = entry.get("name")
			entry_color = entry.get("color", planet_color_default)
			if entry_id is not None:
				td[f"planets_color_{entry_id}"] = entry_color
			if entry_name:
				td[f"planets_color_{entry_name}"] = entry_color

		# zodiac_color_X
		for i in range(12):
			td['zodiac_color_%s' % (i)] = self.settings.settings["color_codes"]["zodiac_icon_%s" % (i)]

		# orb_color_X
		for i in range(len(self.settings.settings["settings_aspect"])):
			# td['orb_color_%s' % (self.settings.settings["settings_aspect"][i]['degree'])] = self.settings.settings["color_codes"]["aspect_%s" % (self.settings.settings["settings_aspect"][i]['degree'])]
			td['orb_color_%s' % (self.settings.settings["settings_aspect"][i]['degree'])] = self.settings.settings["settings_aspect"][i]['color']

		# config
		td['cfgZoom'] = str(self.zoom)
		td['cfgRotate'] = rotate
		td['cfgTranslate'] = translate

		# functions
		td['makeZodiac'] = self.makeZodiac(r)
		td['makeHouses'] = self.makeHouses(r)
		td['makePlanets'] = self.makePlanets(r)
		td['makeElements'] = self.makeElements(r)

		td['makePlanetGrid'] = ""
		if self.settings.settings["settings_svg"]["printPlanetGrid"] == 1:
			td['makePlanetGrid'] = self.makePlanetGrid()

		td['makeHousesGrid'] = ""
		if self.settings.settings["settings_svg"]["printHousesGrid"] == 1:
			td['makeHousesGrid'] = self.makeHousesGrid()


		td['makePlanetGrid_t'] = ""
		td['makeHousesGrid_t'] = ""
		if self.type == "Transit" or self.type == "Direction":
			if self.settings.settings["settings_svg"]["printPlanetGrid_t"] == 1:
				td['makePlanetGrid_t'] = self.makePlanetGrid_t()
			if self.settings.settings["settings_svg"]["printHousesGrid_t"] == 1:
				td['makeHousesGrid_t'] = self.makeHousesGrid_t()

		# read template
		# f=open(self.settings.xml_svg)
		class _TemplateDefaults(dict):
			def __init__(self, data, default_color):
				super().__init__(data)
				self._default_color = default_color

			def __missing__(self, key):
				if key.startswith("planets_color_"):
					return self._default_color
				raise KeyError(key)

		with open(self.settings.xml_svg2, "r", encoding="utf-8") as f:
			template = Template(f.read()).substitute(_TemplateDefaults(td, planet_color_default))

		if self.settings.settings["settings_svg"]["saveSwgFile"] == 1:
			try:
				# write template
				if printing:
					# f = open(cfg.tempfilenameprint, "w")
					f = open(os.path.join(self.settings.tmpdir, self.name + "-" + self.type + '.svg'), "w")
					self._debug("Printing SVG: lat=" + str(self.geolat) + ' lon=' + str(self.geolon) + ' loc=' + self.location)
				else:
					# f = open(self.settings.tempfilename, "w")
					f = open(os.path.join(self.settings.tmpdir, self.name + "-" + self.type + '.svg'), "w")
					self._debug("Creating SVG: lat=" + str(self.geolat) + ' lon=' + str(self.geolon) + ' loc=' + self.location)
				f.write(template)
				f.close()
			except PermissionError:
				self._debug("Unable to write SVG to %s" % self.settings.tmpdir)

		# #return filename
		# return self.settings.tempfilename
		# return SVG
		return template

	#draw transit ring
	def transitRing( self , r ):
		# out = '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:0.7; stroke: %s; stroke-width: 36px; stroke-opacity: 1.0;"/>' % (r,r,r-18,self.settings.settings["color_codes"]['paper_1'] ,self.settings.settings["color_codes"]['paper_1'])
		# out += '<circle cx="%s" cy="%s" r="%s" style="fill: %s; fill-opacity:0.7; stroke: %s; stroke-width: 1px; stroke-opacity: .6;"/>' % (r,r,r,self.settings.settings["color_codes"]['paper_1'] ,self.settings.settings["color_codes"]['zodiac_transit_ring_3'])
		# return out
		return

	#draw degree ring
	def degreeRing( self , r ):
		out=''
		for i in range(72):
			# offset = float(i*5) - self.houses_degree_ut[6]
			offset = float(i*5) - self.get_chart_start_point()
			if offset < 0:
				offset = offset + 360.0
			elif offset > 360:
				offset = offset - 360.0
			x1 = self.sliceToX( 0 , r-self.c1 , offset ) + self.c1
			y1 = self.sliceToY( 0 , r-self.c1 , offset ) + self.c1
			x2 = self.sliceToX( 0 , r+2-self.c1 , offset ) - 2 + self.c1
			y2 = self.sliceToY( 0 , r+2-self.c1 , offset ) - 2 + self.c1
			out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: 1px; stroke-opacity:.9;"/>\n' % (
				x1,y1,x2,y2,self.settings.settings["color_codes"]['paper_0'] )
		return out

	def degreeTransitRing( self , r ):
		out=''
		# for i in range(72):
		# 	offset = float(i*5) - self.houses_degree_ut[6]
		# 	offset = float(i*5) - self.get_chart_start_point()
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

	def makePlanetGrid_t(self):
		out = ''
		li = 10
		offset = 10
		for i in range(len(self.planets)):
			if not self._is_house_index(i):
				if self.planets[i]['visible'] == 1:
					out = out + '<g transform="translate(%s,%s)">' % (offset, li)
					out = out + '<g transform="translate(5,-8)"><use transform="scale(0.4)" xlink:href="#' + \
						  self.planets[i]['name'] + '" /></g>'
					out = out + '<text text-anchor="start" x="16" style="fill:%s; font-size: 10px;">%s</text>' % (
						self.settings.settings["color_codes"]['paper_0'], self.dec2deg(self.t_planets_degree[i]))
					out = out + '<g transform="translate(64,-8)"><use transform="scale(0.3)" xlink:href="#' + self.zodiac[
						self.t_planets_sign[i]] + '" /></g>'
					if self.t_planets_retrograde[i]:
						out = out + '<g transform="translate(76,-6)"><use transform="scale(.5)" xlink:href="#retrograde" /></g>'
					out = out + '</g>\n'
					li = li + 14

		out = out + '\n'
		return out

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
				xa = float(self.settings.settings["settings_aspect"][10]['degree']) - float(self.settings.settings["settings_aspect"][10]['orb'])
				xb = float(self.settings.settings["settings_aspect"][10]['degree']) + float(self.settings.settings["settings_aspect"][10]['orb'])
				if( xa <= delta <= xb ):
					opp[i][j]=True
				#check for conjunction
				xa = float(self.settings.settings["settings_aspect"][0]['degree']) - float(self.settings.settings["settings_aspect"][0]['orb'])
				xb = float(self.settings.settings["settings_aspect"][0]['degree']) + float(self.settings.settings["settings_aspect"][0]['orb'])
				if( xa <= delta <= xb ):
					conj[i][j]=True
				#check for squares
				xa = float(self.settings.settings["settings_aspect"][5]['degree']) - float(self.settings.settings["settings_aspect"][5]['orb'])
				xb = float(self.settings.settings["settings_aspect"][5]['degree']) + float(self.settings.settings["settings_aspect"][5]['orb'])
				if( xa <= delta <= xb ):
					sq[i][j]=True
				#check for qunicunxes
				xa = float(self.settings.settings["settings_aspect"][9]['degree']) - float(self.settings.settings["settings_aspect"][9]['orb'])
				xb = float(self.settings.settings["settings_aspect"][9]['degree']) + float(self.settings.settings["settings_aspect"][9]['orb'])
				if( xa <= delta <= xb ):
					qc[i][j]=True
				#check for sextiles
				xa = float(self.settings.settings["settings_aspect"][3]['degree']) - float(self.settings.settings["settings_aspect"][3]['orb'])
				xb = float(self.settings.settings["settings_aspect"][3]['degree']) + float(self.settings.settings["settings_aspect"][3]['orb'])
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
				out += '<text y="%s" style="fill:%s; font-size: 12px;">%s</text>\n' % (y,self.settings.settings["color_codes"]['paper_0'],self._t("Yot"))

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

	def makeAspectTransitGrid( self , r ):
		out = ''
		out += '<text y="-15" x="0" style="fill:%s; font-size: 12px;">%s</text>\n' % (self.settings.settings["color_codes"]['paper_0'],self._t("Planets in Transit"))
		line = 0
		nl = 0
		def _visible_natal(idx):
			return self.planets[idx].get('visible', 1) == 1
		def _visible_transit(idx):
			return self.planets[idx].get('t_visible', self.planets[idx].get('visible', 1)) == 1

		order_natal = [i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_natal(i)]
		order_natal.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_natal(i)])
		order_transit = [i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_transit(i)]
		order_transit.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_transit(i)])
		order_natal_index = {pid: idx for idx, pid in enumerate(order_natal)}
		order_transit_index = {pid: idx for idx, pid in enumerate(order_transit)}

		atgrid_filtered = [
			item for item in self.atgrid
			if _visible_natal(item.get('p1', -1)) and _visible_transit(item.get('p2', -1))
		]
		atgrid_sorted = sorted(
			atgrid_filtered,
			key=lambda item: (
				order_transit_index.get(item.get('p2'), len(order_transit)),
				order_natal_index.get(item.get('p1'), len(order_natal)),
				item.get('aid', 0),
				item.get('diff', 0),
			),
		)
		for i in range(len(atgrid_sorted)):
			if i == 12:
				nl = 100
				if len(atgrid_sorted) > 24:
					line = -1 * ( len(atgrid_sorted) - 24) * 14
				else:
					line = 0
			out += '<g transform="translate(%s,%s)">' % (nl,line)
			#first planet symbol
			out += '<use transform="scale(0.4)" x="0" y="3" xlink:href="#%s" />\n' % (
				self.planets[atgrid_sorted[i]['p2']]['name'])
			#aspect symbol
			out += '<use  x="15" y="0" xlink:href="#orb%s" />\n' % (
				self.settings.settings["settings_aspect"][atgrid_sorted[i]['aid']]['degree'])
			#second planet symbol
			out += '<g transform="translate(30,0)">'
			out += '<use transform="scale(0.4)" x="0" y="3" xlink:href="#%s" />\n' % (
				self.planets[atgrid_sorted[i]['p1']]['name'])
			out += '</g>'
			#difference in degrees
			out += '<text y="8" x="45" style="fill:%s; font-size: 10px;">%s</text>' % (
				self.settings.settings["color_codes"]['paper_0'],
				self.dec2deg(atgrid_sorted[i]['diff']) )
			#line
			out += '</g>'
			line = line + 14
		out += ''
		return out

	def makeAspectGrid( self , r ):
		self.planets_aspects_list = []
		out=""
		style='stroke:%s; stroke-width: 0.25px; stroke-opacity:.6; fill:none' % (self.settings.settings["color_codes"]['paper_0'])
		def _visible_natal(idx):
			return self.planets[idx].get('visible', 1) == 1 and self.planets[idx].get('visible_aspect_grid', 1) == 1
		def _visible_transit(idx):
			return self.planets[idx].get('t_visible', self.planets[idx].get('visible', 1)) == 1 and self.planets[idx].get('visible_aspect_grid', 1) == 1

		box=14
		if self.type == "Radix":
			xindent = 380
			yindent = 468
			revr=[i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_natal(i)]
			revr.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_natal(i)])
			revr.reverse()
			for idx_a, a in enumerate(revr):
				if self.planets[a]['visible_aspect_grid'] == 1:
					start=self.planets_degree_ut[a]
					#first planet
					out = out + '<rect x="'+str(xindent)+'" y="'+str(yindent)+'" width="'+str(box)+'" height="'+str(box)+'" style="'+style+'"/>\n'
					out = out + '<use transform="scale(0.4)" x="'+str((xindent+2)*2.5)+'" y="'+str((yindent+1)*2.5)+'" xlink:href="#'+self.planets[a]['name']+'" />\n'
					xindent = xindent + box
					yindent = yindent - box
					revr2 = revr[idx_a + 1:]
					xorb=xindent
					yorb=yindent + box
					for b in revr2:
						if self.planets[b]['visible_aspect_grid'] == 1:
							end=self.planets_degree_ut[b]
							diff=self.degreeDiff(start,end)
							out = out + '<rect x="'+str(xorb)+'" y="'+str(yorb)+'" width="'+str(box)+'" height="'+str(box)+'" style="'+style+'"/>\n'
							xorb=xorb+box
							for z in range(len(self.settings.settings["settings_aspect"])):
								#
								# orb = self.settings.settings["settings_aspect"][z]['orb']
								# orb1 = self.settings.settings["settings_aspect"][z]['orb']
								# orb2 = self.settings.settings["settings_aspect"][z]['orb']
								# i=a
								# x=b
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
								# # check if we want to display this aspect
								# # if	( float(self.settings.settings["settings_aspect"][z]['degree']) - orb_before ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + 1.0 ):
								# if (float(self.settings.settings["settings_aspect"][z]['degree']) - orb) <= diff <= (
								# 		float(self.settings.settings["settings_aspect"][z]['degree']) + orb):
								if(self.planetsInAspect(diff, z, a, b)):
								# if	( float(self.settings.settings["settings_aspect"][z]['degree']) - float(self.settings.settings["settings_aspect"][z]['orb']) ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + float(self.settings.settings["settings_aspect"][z]['orb']) ) and self.settings.settings["settings_aspect"][z]['visible_grid'] == 1:
									out = out + '<use  x="'+str(xorb-box+1)+'" y="'+str(yorb+1)+'" xlink:href="#orb'+str(self.settings.settings["settings_aspect"][z]['degree'])+'" />\n'
									# asp_orb = round(abs(float(diff - float(self.settings.settings["settings_aspect"][z]['degree']))),1)
									# asp_str = f"{self.planets[a]['name']} {self.settings.settings["settings_aspect"][z]['degree']} {self.planets[b]['name']} (orbis: {asp_orb})"
									# self.planets_aspects_list.append(asp_str)



			# Make self.planets_aspects_list and add aspects in self.planets_dict, self.houses_dict
			self.aspect_all_str=""
			revr=[i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_natal(i)]
			revr.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_natal(i)])
			i=0
			hi=0
			# revr.reverse()
			for idx_a, a in enumerate(revr):
				if self.planets[a]['visible_aspect_grid'] == 1:
					start=self.planets_degree_ut[a]
					#first planet
					revr2 = revr[idx_a + 1:]
					# revr2.reverse()
					for b in revr2:
						if self.planets[b]['visible_aspect_grid'] == 1:
							end=self.planets_degree_ut[b]
							diff=self.degreeDiff(start,end)
							for z in range(len(self.settings.settings["settings_aspect"])):
								if(self.planetsInAspect(diff, z, a, b)):
									aspects_degree_id = self.settings.settings["settings_aspect"][z]['id']
									aspect_weight = self.settings.settings["settings_aspect_dic"].get(aspects_degree_id, {}).get("weight", 1)
									asp_orb = abs(float(diff - float(self.settings.settings["settings_aspect"][z]['degree'])))
									asp_orb_deg = self.dec2deg_str(asp_orb, type='2')
									asp_str = f"{self.planets[a]['name']} {self.settings.settings['settings_aspect_dic'][aspects_degree_id]['label']} {self.planets[b]['name']} orb={asp_orb_deg}"
									orb1, orb2, aspect_orb_default = self.getAspectOrbs(z, a, b)
									aspect_accuracy = None
									aspect_score = None
									if aspect_orb_default and aspect_orb_default != 0:
										aspect_accuracy = asp_orb / aspect_orb_default
										aspect_score = 1 - aspect_accuracy
									asp_dict_a = {
										'aspect_str': asp_str,
										'planet_name1': self.planets[a]['name'],
										'planet_name2': self.planets[b]['name'],
										'planet_id1': a,
										'planet_id2': b,
										'aspect_degree': self.settings.settings["settings_aspect"][z]['degree'],
										'aspect_diff': diff,
										'aspect_orbis': asp_orb,
										'aspect_label': self.settings.settings["settings_aspect_dic"][aspects_degree_id].get('label'),
										'aspect_id': aspects_degree_id,
										'aspect_orbis_calc': aspect_orb_default,
										'aspect_orbis_accuracy': aspect_accuracy,
										'aspect_orbis_score': aspect_score,
										'aspect_orbis_planet': orb2,
										'aspect_orbis_deg': asp_orb_deg,
										'aspect_weight': aspect_weight,
									}
									asp_dict_b = dict(asp_dict_a)
									asp_dict_b['aspect_orbis_planet'] = orb1

									self.planets_aspects_list.append(asp_dict_a)

									if ('visible_json' in self.planets[a] and self.planets[a]['visible_json'] == 1):
										if ('visible_json' in self.planets[b] and self.planets[b]['visible_json'] == 1):
											if ('visible_json' in self.settings.settings["settings_aspect_dic"][aspects_degree_id] and self.settings.settings["settings_aspect_dic"][aspects_degree_id]['visible_json'] == 1):
												self.aspect_all_str = self.aspect_all_str + asp_str + """
"""

									# planets_dict is populated in makeAspects now
									# astro_dict is populated in makeAspects now
									# planets_dict is populated in makeAspects now
									# astro_dict is populated in makeAspects now

									# Houses aspects
									if (22 < a and a < 35):
										if 'aspects' not in self.houses_dict[a]:
											self.houses_dict[a]['aspects'] = {}
										self.houses_dict[a]['aspects'][b] = asp_dict_a
									# Houses aspects
									if (22 < b and b < 35):
										if 'aspects' not in self.houses_dict[b]:
											self.houses_dict[b]['aspects'] = {}
										self.houses_dict[b]['aspects'][a] = asp_dict_b

		if self.type == "Transit" or self.type == "Direction":
			box = 12
			xstart = 500
			ystart = 280
			xindent = xstart
			yindent = ystart
			revr_natal = [i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_natal(i)]
			revr_natal.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_natal(i)])
			revr_transit = [i for i in range(len(self.planets)) if not self._is_house_index(i) and _visible_transit(i)]
			revr_transit.extend([i for i in range(len(self.planets)) if self._is_house_index(i) and _visible_transit(i)])
			# revr.reverse()
			ii=0
			# Make self.planets_aspects_list and add aspects in self.planets_dict, self.houses_dict
			self.t_aspect_all_str=""
			self.t_planets_aspects_list=[]
			for a in revr_natal:
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
					for b in revr_transit:
						if self.planets[b]['visible_aspect_grid'] == 1:
							end = self.t_planets_degree_ut[b]
							diff = self.degreeDiff(start, end)
							out = out + '<rect x="' + str(xorb) + '" y="' + str(yorb) + '" width="' + str(
								box) + '" height="' + str(box) + '" style="' + style + '"/>\n'
							xorb = xorb + box
							for z in range(len(self.settings.settings["settings_aspect"])):
								#
								# orb = self.settings.settings["settings_aspect"][z]['orb']
								# orb1 = self.settings.settings["settings_aspect"][z]['orb']
								# orb2 = self.settings.settings["settings_aspect"][z]['orb']
								# i = a
								# x = b
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
								# # check if we want to display this aspect
								# # if	( float(self.settings.settings["settings_aspect"][z]['degree']) - orb_before ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + 1.0 ):
								# if (float(self.settings.settings["settings_aspect"][z]['degree']) - orb) <= diff <= (
								# 		float(self.settings.settings["settings_aspect"][z]['degree']) + orb):
								# 	# if	( float(self.settings.settings["settings_aspect"][z]['degree']) - float(self.settings.settings["settings_aspect"][z]['orb']) ) <= diff <= ( float(self.settings.settings["settings_aspect"][z]['degree']) + float(self.settings.settings["settings_aspect"][z]['orb']) ) and self.settings.settings["settings_aspect"][z]['visible_grid'] == 1:
								if(self.planetsInAspect(diff, z, a, b)):
									out = out + '<use  x="' + str(xorb - box + 1) + '" y="' + str(
										yorb + 1) + '" xlink:href="#orb' + str(self.settings.settings["settings_aspect"][z]['degree']) + '" />\n'

									aspects_degree_id = self.settings.settings["settings_aspect"][z]['id']
									aspect_weight = self.settings.settings["settings_aspect_dic"].get(aspects_degree_id, {}).get("weight", 1)
									asp_orb = abs(float(diff - float(self.settings.settings["settings_aspect"][z]['degree'])))
									asp_orb_deg = self.dec2deg_str(asp_orb, type='2')
									asp_str = f"{self.planets[a]['name']} {self.settings.settings['settings_aspect'][z]['degree']} {self.planets[b]['name']} orb={asp_orb_deg}"
									orb1, orb2, aspect_orb_default = self.getAspectOrbs(z, a, b)
									aspect_accuracy = None
									aspect_score = None
									if aspect_orb_default and aspect_orb_default != 0:
										aspect_accuracy = asp_orb / aspect_orb_default
										aspect_score = 1 - aspect_accuracy
									asp_dict_a = {
										'aspect_str': asp_str,
										'planet_name1': self.planets[a]['name'],
										'planet_name2': self.planets[b]['name'],
										'planet_id1': a,
										'planet_id2': b,
										'aspect_degree': self.settings.settings["settings_aspect"][z]['degree'],
										'aspect_diff': diff,
										'aspect_orbis': asp_orb,
										'aspect_label': self.settings.settings["settings_aspect_dic"][aspects_degree_id].get('label'),
										'aspect_id': aspects_degree_id,
										'aspect_orbis_calc': aspect_orb_default,
										'aspect_orbis_accuracy': aspect_accuracy,
										'aspect_orbis_score': aspect_score,
										'aspect_orbis_planet': orb2,
										'aspect_orbis_deg': asp_orb_deg,
										'aspect_weight': aspect_weight,
									}
									asp_dict_b = dict(asp_dict_a)
									asp_dict_b['aspect_orbis_planet'] = orb1

									self.t_planets_aspects_list.append(asp_dict_a)
									if ('visible_json' in self.planets[a] and self.planets[a]['visible_json'] == 1):
										if ('t_visible_json' in self.planets[b] and self.planets[b]['t_visible_json'] == 1):
											if ('visible_json' in self.settings.settings["settings_aspect_dic"][
												aspects_degree_id] and
													self.settings.settings["settings_aspect_dic"][aspects_degree_id][
														'visible_json'] == 1):
												self.t_aspect_all_str = self.t_aspect_all_str + asp_str + """
"""
									# Add transit aspects to natal->transit dictionary.
									# planets_dict_t is populated in makeAspectsTransit now
									# astro_dict is populated in makeAspectsTransit now

		return out

	def makeElements( self , r ):
		total = self.fire + self.earth + self.air + self.water
		pf = int(round(100*self.fire/total))
		pe = int(round(100*self.earth/total))
		pa = int(round(100*self.air/total))
		pw = int(round(100*self.water/total))
		out = '<g transform="translate(-30,79)">\n'
		out = out + '<text y="0" style="fill:#ff6600; font-size: 10px;">'+self.settings.settings["label"]['fire']+'  '+str(pf)+'%</text>\n'
		out = out + '<text y="12" style="fill:#6a2d04; font-size: 10px;">'+self.settings.settings["label"]['earth']+' '+str(pe)+'%</text>\n'
		out = out + '<text y="24" style="fill:#6f76d1; font-size: 10px;">'+self.settings.settings["label"]['air']+'   '+str(pa)+'%</text>\n'
		out = out + '<text y="36" style="fill:#630e73; font-size: 10px;">'+self.settings.settings["label"]['water']+' '+str(pw)+'%</text>\n'
		out = out + '</g>\n'
		return out

	def makePlanetGrid(self):
		out = ''
		# loop over all planets
		li = 10
		offset = 10
		for i in range(len(self.planets)):
			# if i == 27:
			# 	li = 10
			# 	offset = -120
			if not self._is_house_index(i):
				if self.planets[i]['visible'] == 1:
					# start of line
					out = out + '<g transform="translate(%s,%s)">' % (offset, li)
					# planet text
					# out = out + '<text text-anchor="end" style="fill:%s; font-size: 10px;">%s</text>' % (self.settings.settings["color_codes"]['paper_0'],self.planets[i]['label'])
					# planet symbol
					out = out + '<g transform="translate(5,-8)"><use transform="scale(0.4)" xlink:href="#' + \
						  self.planets[i]['name'] + '" /></g>'
					# planet degree
					out = out + '<text text-anchor="start" x="16" style="fill:%s; font-size: 10px;">%s</text>' % (
					self.settings.settings["color_codes"]['paper_0'], self.dec2deg(self.planets_degree[i]))
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

	def makeHousesGrid( self ):
		out = ''
		li=10
		offset=10
		for i in range(12):
			if i < 9:
				cusp = '&#160;&#160;'+str(i+1)
			else:
				cusp = str(i+1)
			# out += '<g transform="translate(0,'+str(li)+')">'
			out = out + '<g transform="translate(%s,%s)">' % (offset, li)
			# out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s %s:</text>' % (self.settings.settings["color_codes"]['paper_0'],self.settings.settings["label"]['cusp'],cusp)
			out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s:</text>' % (self.settings.settings["color_codes"]['paper_0'],cusp)
			out += '<g transform="translate(40,-8)"><use transform="scale(0.3)" xlink:href="#'+self.zodiac[self.houses_sign[i]]+'" /></g>'
			out += '<text x="53" style="fill:%s; font-size: 10px;"> %s</text>' % (self.settings.settings["color_codes"]['paper_0'],self.dec2deg(self.houses_degree[i]))
			out += '</g>\n'
			li = li + 14
		out += '\n'
		return out
	def makeHousesGrid_t( self ):
		out = ''
		li=10
		offset=10
		for i in range(12):
			if i < 9:
				cusp = '&#160;&#160;'+str(i+1)
			else:
				cusp = str(i+1)
			# out += '<g transform="translate(0,'+str(li)+')">'
			out = out + '<g transform="translate(%s,%s)">' % (offset, li)
			# out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s %s:</text>' % (self.settings.settings["color_codes"]['paper_0'],self.settings.settings["label"]['cusp'],cusp)
			out += '<text text-anchor="end" x="40" style="fill:%s; font-size: 10px;">%s:</text>' % (self.settings.settings["color_codes"]['paper_0'],cusp)
			out += '<g transform="translate(40,-8)"><use transform="scale(0.3)" xlink:href="#'+self.zodiac[self.t_houses_sign[i]]+'" /></g>'
			out += '<text x="53" style="fill:%s; font-size: 10px;"> %s</text>' % (self.settings.settings["color_codes"]['paper_0'],self.dec2deg(self.t_houses_degree[i]))
			out += '</g>\n'
			li = li + 14
		out += '\n'
		return out
