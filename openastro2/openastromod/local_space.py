from __future__ import annotations

import copy
import math
from typing import Any

import numpy as np
import pandas as pd
import pydeck as pdk
import swisseph as swe
from geographiclib.geodesic import Geodesic
from skyfield import api, framelib
from skyfield.api import N, E, load, wgs84
from skyfield.positionlib import Apparent


class LocalSpaceMixin:
	def _settings_planet_entry(self, index):
		key = str(index)
		settings_payload = getattr(self, "settings", None)
		if settings_payload is not None:
			if isinstance(settings_payload, dict):
				planet_dict = settings_payload.get("settings_planet_dict", {})
				house_dict = settings_payload.get("settings_house_dict", {})
				planet_list = settings_payload.get("settings_planet")
				house_list = settings_payload.get("settings_house")
			else:
				planet_dict = getattr(settings_payload, "settings_planet_dict", {})
				house_dict = getattr(settings_payload, "settings_house_dict", {})
				planet_list = getattr(settings_payload, "settings_planet", None)
				house_list = getattr(settings_payload, "settings_house", None)
			if key in planet_dict:
				return planet_dict[key]
			if key in house_dict:
				return house_dict[key]
			for source in (planet_list, house_list):
				if isinstance(source, list):
					for entry in source:
						entry_id = entry.get("id")
						if entry_id is not None and str(entry_id) == key:
							return entry
		try:
			idx = int(index)
		except (TypeError, ValueError):
			idx = None
		if idx is not None and hasattr(self, "planets") and 0 <= idx < len(self.planets):
			return self.planets[idx]
		if settings_payload is not None:
			for source in (planet_list, house_list):
				if isinstance(source, list) and idx is not None:
					try:
						return source[idx]
					except (IndexError, TypeError, ValueError):
						continue
		raise KeyError(f"settings_planet entry '{index}' not found")

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
	def makeLocalSpaceApiDataFrame(self, dt, lat, lon):

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
		return dfd


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
	def makeLocalSpaceEarthApiDataFrame(self, dt, lat, lon):

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
				astro = place.at(ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)).observe(planet)
				app = astro.apparent()
				alt, az, distance = app.altaz()
				azimuth = az.degrees

				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				# lons, lats = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# lons2, lats2 = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				dfdata= {
				  "from": {
					"lonlat": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					"lonlat": [
					  new_longitude,
					  new_latitude
					]
				  },
					"name": self.name + "/" + "+" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " alt=" + ")",
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					"lonlat": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					"lonlat": [
					  new_longitude2,
					  new_latitude2
					]
				  },
					"name": self.name + "/" + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
				}
				dfd.append(dfdata)
		return dfd




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
				try:
					planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				except Exception:
					get_house_number = getattr(self, "get_house_number_by_id", lambda _: None)
					h_i = get_house_number(planet_code)
					if h_i is None:
						continue
					houses_system = b'P'
					if self.settings.settings["astrocfg"].get('houses_system', None):
						houses_system = self.settings.settings["astrocfg"]['houses_system'].encode("ascii")
						print(houses_system)
					sh = swe.houses(jul_day_UT, lat, lon, houses_system)
					planet_pos = []
					planet_pos.append([sh[0][h_i], 0, 1, 1, 1, 1])
				# print (planet_pos)
				# lat = planet_pos[0][0]
				# lon = planet_pos[0][1]
				# planet_pos[0][0] = 0
				# print(self._settings_planet_entry(i)['name'] , lat, lon)
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
				# print(self._settings_planet_entry(i)['name'] , azimuth, true_altitude, apparent_altitude)
				# print (self._settings_planet_entry(i)['name'])
				# print("Азимут планеты:", azimuth)
				# print("Истинная высота:", true_altitude)
				# print("Видимая высота:", apparent_altitude)
				label_short = self._settings_planet_entry(i)['label_short']
				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				# lons, lats = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				# lons2, lats2 = slerp(A=[starting_longitude, starting_latitude], B=[new_longitude, new_latitude], dir=-1)
				dfdata= {
				  "from": {
					# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) +  ")",
					  "label_short": f"{label_short}",
					  "coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth)  + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth)  + ")",
					  "label_short": f"{label_short}",
					  "coordinates": [
					  new_longitude,
					  new_latitude
					]
				  }
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					  "label_short": f"{label_short}",
					  "coordinates": [
					  starting_longitude,
					  starting_latitude
					]
				  },
				  "to": {
					# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
					# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
					"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					  "label_short": f"{label_short}",
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
	def makeLocalSpaceSweApiLayer(self, dt, lat, lon, color1 =[150, 150, 150], color2=[150, 150, 150], num_planet=11):
		dfd = self.makeLocalSpaceSweApiDataFrame(dt, lat, lon, num_planet)
		df = pd.DataFrame(dfd)
		# print (color1)
		# Define a layer to display on a map
		layer = pdk.Layer(
		"GreatCircleLayer",
		df,
		pickable=True,
		get_stroke_width=12,
		get_source_position="from.lonlat",
		get_target_position="to.lonlat",
		get_source_color=color1,
		get_target_color=color2,
		auto_highlight=True,
		)
		return layer
	def makeLocalSpaceSweApiDataFrame(self, dt, lat, lon, num_planet=11):
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
				azimuth, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	  [lon, lat, 287], 0, 0,
																	  planet_pos[0])
				azimuth = azimuth + 180
				if(azimuth>360):
					azimuth = azimuth-360

				new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
				new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
				dfdata= {
				  "from": {
					"lonlat": [starting_longitude,starting_latitude]
				  },
				  "to": {
					"lonlat": [new_longitude,new_latitude]
				  },
					"name": self.name + "/" + "+" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					"azimuth": azimuth,
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					"lonlat": [starting_longitude,starting_latitude]
				  },
				  "to": {
					"lonlat": [new_longitude2,new_latitude2]
				  },
					"name": self.name + "/" + "-" + self._settings_planet_entry(i)['name'] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
					"azimuth": self.deg_180(azimuth),
				}
				dfd.append(dfdata)
		return dfd



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
				# planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				try:
					planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				except Exception:
					get_house_number = getattr(self, "get_house_number_by_id", lambda _: None)
					h_i = get_house_number(planet_code)
					if h_i is None:
						continue
					houses_system = b'P'
					if self.settings.settings["astrocfg"].get('houses_system', None):
						houses_system = self.settings.settings["astrocfg"]['houses_system'].encode("ascii")
						print(houses_system)
					sh = swe.houses(jul_day_UT, lat, lon, houses_system)
					planet_pos = []
					planet_pos.append([sh[0][h_i], 0, 1, 1, 1, 1])
				azimuth0, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	  [lon, lat, 287], 0, 0,
																	  planet_pos[0])
				# azimuth = azimuth -180
				# print(self._settings_planet_entry(i)['name'] , azimuth, true_altitude, apparent_altitude)
				# print (self._settings_planet_entry(i)['name'])
				# print("Азимут планеты:", azimuth)
				# print("Истинная высота:", true_altitude)
				# print("Видимая высота:", apparent_altitude)
				# aspects = [60, 90, 120]

				for aspect in aspects:
					label_short = self._settings_planet_entry(i)['label_short']
					azimuth = azimuth0 + aspect
					if (azimuth > 360):
						azimuth = azimuth - 360
					new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, distance2)
					new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude, starting_longitude, azimuth, -distance2)
					dfdata= {
					  "from": {
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						  "label_short": f"{label_short}-{aspect}",
						  "coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						  "label_short": f"{label_short}-{aspect}",
						  "coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df

	def makeLocalSpaceAspectSwePlanets(self, dt, lat, lon, planets=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, ],
									   aspects=[0, 180], aspect_type='azimuth'):
		"""
		Calc LocalSpace thru Swe with aspects list and planets list.
		Return list without dataframe.
		New best function.

		:param dt:
		:param lat:
		:param lon:
		:param planets:
		:param aspects:
		:return:
		"""

		starting_latitude = lat  # Начальная широта
		starting_longitude = lon  # Начальная долгота
		distance2 = 6371 * 3.1  # Расстояние (в километрах)
		sp_hour = self.decHourJoin(dt.hour, dt.minute, dt.second)
		jul_day_UT = swe.julday(dt.year, dt.month, dt.day, sp_hour)
		dfd = []
		for i in planets:
			if 1:
				planet_code = i
				try:
					planet_pos = swe.calc_ut(jul_day_UT, planet_code)
				except Exception:
					get_house_number = getattr(self, "get_house_number_by_id", lambda _: None)
					h_i = get_house_number(planet_code)
					if h_i is None:
						continue
					houses_system = b'P'
					if self.settings.settings["astrocfg"].get('houses_system', None):
						houses_system = self.settings.settings["astrocfg"]['houses_system'].encode("ascii")
						# print(houses_system)
					sh = swe.houses(jul_day_UT, lat, lon, houses_system)
					planet_pos = []
					planet_pos.append([sh[0][h_i], 0, 1, 1, 1, 1])

				azimuth0, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																	   [lon, lat, 287], 0, 0,
																	   planet_pos[0])
				azimuth0 = azimuth0 + 180
				if (azimuth0 > 360):
					azimuth0 = azimuth0 - 360

				for aspect in aspects:
					label_short = self._settings_planet_entry(i)['label_short']
					if aspect_type == 'ecliptic_parallel':
						deg_ut = planet_pos[0][0] - aspect # rotation is different for ecliptic and azimuth
						if (deg_ut < 0):
							deg_ut = deg_ut + 360
						# print(planet_pos)
						planet_pos_asp = list(planet_pos)
						planet_pos_0_list = list(planet_pos_asp[0])
						planet_pos_asp[0] = planet_pos_0_list
						planet_pos_asp[0][0] = deg_ut
						# print(planet_pos_asp)
						azimuth, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																			  [lon, lat, 287], 0, 0,
																			  planet_pos_asp[0])
						azimuth = azimuth + 180
						if (azimuth > 360):
							azimuth = azimuth - 360

					elif aspect_type == 'ecliptic_diagonal':
						deg_ut = planet_pos[0][0] - aspect # rotation is different for ecliptic and azimuth
						if (deg_ut < 0):
							deg_ut = deg_ut + 360
						# print(planet_pos)
						planet_pos_asp = list(planet_pos)
						planet_pos_0_list = list(planet_pos_asp[0])
						planet_pos_asp[0] = planet_pos_0_list
						planet_pos_asp[0][0] = deg_ut

						# Diagonal == cos(aspect) cos(0)==1, cos(180)==-1
						aspect_coef = math.cos(math.radians(aspect))
						# print(f"aspect={aspect}° → aspect_height={aspect_coef:.3f}")
						planet_pos_asp[0][1] = planet_pos[0][1] * aspect_coef

						# print(planet_pos_asp)
						azimuth, true_altitude, apparent_altitude = swe.azalt(jul_day_UT, swe.ECL2HOR,
																			  [lon, lat, 287], 0, 0,
																			  planet_pos_asp[0])
						azimuth = azimuth + 180
						if (azimuth > 360):
							azimuth = azimuth - 360

					else:
						azimuth = azimuth0 + aspect # rotation is different for ecliptic and azimuth
						if (azimuth > 360):
							azimuth = azimuth - 360


					new_latitude, new_longitude = self.compute_destination_point(starting_latitude, starting_longitude,
																				 azimuth, distance2)
					new_latitude2, new_longitude2 = self.compute_destination_point(starting_latitude,
																				   starting_longitude, azimuth,
																				   -distance2)
					dfdata = {
						"from": {
							"name": self.name + "/" + "+" + self._settings_planet_entry(i)['name'] + "-" + str(
								aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
							"label_short": f"{label_short}-{aspect}",
							"coordinates": [starting_longitude, starting_latitude]
						},
						"to": {
							"name": self.name + "/" + "+" + self._settings_planet_entry(i)['name'] + "-" + str(
								aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
							"label_short": f"{label_short}-{aspect}",
							"coordinates": [new_longitude, new_latitude]
						},
						"name": self.name + "/" + "+" + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"label_short": f"{label_short}-{aspect}",
						"azimuth": azimuth,
					}

					dfd.append(dfdata)

		# Добавляем поле "name" на верхний уровень (как в оригинальном DataFrame)
		for item in dfd:
			item["name"] = item["from"]["name"]
			item["label_short"] = item["from"]["label_short"]
		return dfd


	def makeLocalSpaceAspectSweApiDataFrame(self, dt, lat, lon, num_planet=11, aspects = [60, 90, 120]):

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
				# print(self._settings_planet_entry(i)['name'] , azimuth, true_altitude, apparent_altitude)
				# print (self._settings_planet_entry(i)['name'])
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
						"lonlat": [starting_longitude, starting_latitude]
					  },
					  "to": {
						"lonlat": [new_longitude, new_latitude]
					  },
						"name": self.name + "/" + "+" + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						"lonlat": [starting_longitude, starting_latitude]
					  },
					  "to": {
						"lonlat": [new_longitude2, new_latitude2]
					  },
						"name": self.name + "/" + "-" + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(
							self.deg_180(azimuth)) + ")",
					}
					dfd.append(dfdata)
		return dfd

	def makeLocalSpaceAntisZodiacDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [+1, -1]):
		# aspects = [+1, -1]

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
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
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df
	def makeLocalSpaceAntisZodiacApiDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [+1, -1]):
		# aspects = [+1, -1]

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
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
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		return dfd

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
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df
	def makeLocalSpaceAntisHouseApiDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [+1, -1]):

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
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "+" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"coordinates": [new_longitude, new_latitude]
					  }
					}

					dfd.append(dfdata)
					dfdata= {
					  "from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [starting_longitude, starting_latitude]
					  },
					  "to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/"  + "-" + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + ")",
						"coordinates": [new_longitude2, new_latitude2]
					  }
					}
					dfd.append(dfdata)
		return dfd

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

	def makeLocalSpaceAspectSkyDataFrame(self, type_tr, dt, lat, lon, num_planet=11,
										 aspects=[0, 60, 90, 120, 180, 240, 270, 300], local_aspects=False):
		"""
		Calculates Local Space directions via library.

		:param type_tr: Radix or Transit
		:param dt: date and time
		:param lat: latitude
		:param lon: longitude
		:param num_planet: number of planets
		:param aspects: list of aspects
		:param local_aspects: True - use local aspects by azimuths. False - aspects on the ecliptic
		:return: Dataframe with geographic coordinates of the planets and azimuths.
		"""

		print('dt=', dt)
		ts = api.load.timescale()
		t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

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

			label_short = self._settings_planet_entry(i)['label_short']
			azimuth0 = False
			for aspect in aspects:
				if (aspect <= 180):
					lat_angle = lat_angle0 * (90 - aspect) / 90.0
				if (aspect > 180):
					lat_angle = lat_angle0 * (aspect - 90 - 180) / 90.0
				true_altitude = lat_angle
				lon_angle = lon_angle0 + aspect

				[h_lat, h_lon] = self.eclips_to_geo([lon_angle], [lat_angle], t)
				alt0, az0, distance0 = self.eclips_to_gorizont([lon_angle], [lat_angle], dt, lat, lon)
				azimuth = az0.degrees[0]
				new_latitude = h_lat[0]
				new_longitude = h_lon[0]
				if aspect == 0:
					azimuth0 = azimuth
				if local_aspects == True and azimuth0:
					azimuth = azimuth0 + aspect

				dfdata = {
					"from": {
						# "name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
						"label_short": f"{label_short}-{aspect}",
						"coordinates": [starting_longitude, starting_latitude]
					},
					"to": {
						# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
						"label_short": f"{label_short}-{aspect}",
						"coordinates": [new_longitude, new_latitude]
					},
					"azimuth": azimuth
				}

				dfd.append(dfdata)
				dfdata = {
					"from": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(
							self.deg_180(azimuth)) + ")",
						"label_short": f"{label_short}-{aspect}",
						"coordinates": [starting_longitude - 180, -starting_latitude]
					},
					"to": {
						# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
						# "name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
						"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
							aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(
							self.deg_180(azimuth)) + ")",
						"label_short": f"{label_short}-{aspect}",
						"coordinates": [new_longitude, new_latitude]
					},
					# "azimuth": self.deg_180(azimuth)
					"azimuth": azimuth
				}
				dfd.append(dfdata)
		df = pd.DataFrame(dfd)
		# df["name"] = df["from"].apply(lambda f: f["name"])
		df["name"] = df["to"].apply(lambda t: t["name"])
		return df


	def makeLocalSpaceAspectSkyApiDataFrame(self, type_tr, dt, lat, lon, num_planet=11, aspects = [0, 60, 90, 120, 180, 240, 270, 300]):

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
					"lonlat": [starting_longitude, starting_latitude]
				  },
				  "to": {
					"lonlat": [new_longitude, new_latitude]
				  },
					"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
						aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + ")",
				}

				dfd.append(dfdata)
				dfdata= {
				  "from": {
					"lonlat": [starting_longitude-180, -starting_latitude]
				  },
				  "to": {
					"lonlat": [new_longitude, new_latitude]
				  },
					"name": self.name + "/" + " " + self._settings_planet_entry(i)['name'] + "-" + str(
						aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(
						self.deg_180(azimuth)) + ")",
				}
				dfd.append(dfdata)
		return dfd

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
		# 		# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
		# 		# 	"coordinates": [
		# 		# 	  starting_longitude,
		# 		# 	  starting_latitude
		# 		# 	]
		# 		#   },
		# 		#   "to": {
		# 		# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
				# 	"name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	# "name": self.name + "/"  + "-" + planet_names[i] + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(alt.degrees) +  " distance=" + str(distance) + ")",
				# 	"coordinates": [starting_longitude, starting_latitude]
				#   },
				#   "to": {
				# 	# "name": self.name + "/" + "-"  + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) +  " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	"coordinates": [new_longitude, new_latitude]
				#   }
				# }
				#
				# dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
				# 	"coordinates": [starting_longitude-180, -starting_latitude]
				#   },
				#   "to": {
				# 	# "name": self.name + "/ " + "+" + self._settings_planet_entry(i)['name'] + " (" + '{0:.1f}'.format(azimuth) + ")",
				# 	"name": self.name + "/"  + " " + self._settings_planet_entry(i)['name'] + "-" + str(aspect) + " (" + " az=" + '{0:.1f}'.format(azimuth) + " az180=" + '{0:.1f}'.format(self.deg_180(azimuth)) + " alt=" + '{0:.1f}'.format(true_altitude) + ")",
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
	def makeLocalSpaceAspectSkyHouseApiDataFrame(self, type_tr, dt, lat, lon, aspects = [0, 60, 90, 120, 180, 240, 270, 300]):
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
		return dfd

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
	def makeZenitApiDataFrame(self, dt, lat, lon):

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
		return dfd
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
			print (self._settings_planet_entry(i)['name'])
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
					"name": " K1 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K1 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
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
					"name": " K7 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K7 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
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
	def makeAscApiDataFrame(self, dt, lat, lon, num_planet=11):
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
			print (self._settings_planet_entry(i)['name'])
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
					"name": " K1 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K1 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
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
					"name": " K7 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i][0]) + " " + str(coord_arr[i][1]) + " " ,
					"coordinates": [coord_arr[i][0], coord_arr[i][1]]
				  },
				  "to": {
					"name": " K7 " + self._settings_planet_entry(planet_id)['name'] + " " + str(coord_arr[i+1][0]) + " " + str(coord_arr[i+1][1]) + " ",
					"coordinates": [coord_arr[i+1][0], coord_arr[i+1][1]]
				  }
				}
				dfd.append(dfdata)
		return dfd
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

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
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
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
	def makeLocalSpaceZodiakSkyApiDataFrame(self, dt, lat, lon):

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
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
		return dfd

	def eclips_to_gorizont0(self, eclips_arr, dt, lat, lon):
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
		# angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		angle = - np.array(eclips_arr)/360 * tau + 1/4.0 * tau

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

		# tau = api.tau
		# ts = api.load.timescale()
		# eph = api.load('de421.bsp')
		# bluffton = api.Topos(lat, lon)
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# # angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		# angle = - np.array(self.houses_degree_ut)/360 * tau + 1/4.0 * tau
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
				  },
				"azimuth": azimuth
				}

				dfd.append(dfdata)
				# dfdata= {
				#   "from": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
	def makeLocalSpaceHouseSkyApiDataFrame(self, dt, lat, lon):
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)

		# tau = api.tau
		# ts = api.load.timescale()
		# eph = api.load('de421.bsp')
		# bluffton = api.Topos(lat, lon)
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# # angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		# angle = - np.array(self.houses_degree_ut)/360 * tau + 1/4.0 * tau
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
		return dfd

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
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
	def makeLocalSpaceHouseSky2ApiDataFrame(self, dt, lat, lon):

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
		return dfd


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

		# tau = api.tau
		# ts = api.load.timescale()
		# eph = api.load('de421.bsp')
		# bluffton = api.Topos(lat, lon)
		# t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# # angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		# angle = - np.array(self.t_houses_degree_ut)/360 * tau + 1/4.0 * tau
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
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
	def makeLocalSpaceHouseTransitSkyApiDataFrame(self, dt, lat, lon):
		alt0, az0, distance0 = self.eclips_to_gorizont0(self.t_houses_degree_ut, dt, lat, lon)

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
		return dfd

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

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		angle = - np.array(self.houses_degree_ut)/360 * tau + 1/4.0 * tau

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
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
				# 	"coordinates": [
				# 	  starting_longitude,
				# 	  starting_latitude
				# 	]
				#   },
				#   "to": {
				# 	"name": self.name + "/"  + "zodiac-" + str(i) + " (" + " az=" + '{0:.1f}'.format(float(azimuth)) + " alt=" + '{0:.1f}'.format(float(alt)) +")",
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
	def makeLocalSpaceHouseEquatorialSkyApiDataFrame(self, dt, lat, lon):
		# print (self.houses_degree_ut)
		# https: // astronomy.stackexchange.com / questions / 41482 / how - to - find - the - local - azimuth - of - the - highest - point - of - the - ecliptic
		# https://astronomy.stackexchange.com/questions/41482/how-to-find-the-local-azimuth-of-the-highest-point-of-the-ecliptic
		# https: // rhodesmill.org / skyfield / api - position.html  # skyfield.positionlib.ICRF.from_time_and_frame_vectorshttps://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
		# classmethod from_time_and_frame_vectors(t, frame, distance, velocity)

		tau = api.tau
		ts = api.load.timescale()
		eph = api.load('de421.bsp')
		bluffton = api.Topos(lat, lon)
		t = ts.utc(dt.year,dt.month,dt.day,dt.hour,dt.minute, dt.second)
		# angle = - np.arange(12) / 12.0 * tau + 1/4.0 * tau
		angle = - np.array(self.houses_degree_ut)/360 * tau + 1/4.0 * tau

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
		return dfd




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

	def make_df_data2(self, data):
		df_data = []
		for item in data:
			id, lat, lon, dt_str, name = item
			data_entry = {"lat": lat, "lon": lon, "dt_str":dt_str, "name": name, "id": id}
			df_data.append(data_entry)
		return df_data
