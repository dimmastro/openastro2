# openastro2/modules/object/zemletochki/zemletochki.py
import json
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth


class Zemletochki:
    def __init__(self, server_url, user, password, x_token, zt_type):
        self.server_url = server_url
        self.user = user
        self.password = password
        self.x_token = x_token
        self.zt_type = zt_type

    # def process(self, year,month,day,hour,h,m,s,geolon,geolat,altitude,openastrocfg,):
    def process(self, *args, **kwargs):
        # Здесь можно добавить основную логику модуля
        # result = f"Zemletochki processed with {self.arg1} and {self.arg2}"
        year = kwargs['year']
        month = kwargs['month']
        day = kwargs['day']
        hour = kwargs['hour']
        h = kwargs['h']
        m = kwargs['m']
        s = kwargs['s']
        geolat = kwargs['geolat']
        geolon = kwargs['geolon']

        planets_degree_ut = 0
        planet_latitude = 0
        try:
            planet_pos=[]
            zt_degree_ut = self.zt_request(year, month, day, h, m, s, geolat, geolon)
            planet_pos.append(((zt_degree_ut[0], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[1], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[2], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[3], 0, 0, 0, 0, 0),0))

        except Exception as _ex:
            print(_ex)
            planet_pos = []
        # planet_pos = ((planets_degree_ut, planet_latitude, 0, 0, 0, 0),0)
        return planet_pos


    def zt_request(self, year, month, day, h, m, s, geolat, geolon):
        print (geolat, geolon)
        dt = datetime(year, month, day, h, m, s)
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        request_payload = {
            "dt_str": dt_str,
            "geolat": geolat,
            "geolon": geolon,
            "type": 3,
        }
        headers = {
            'X-Token': '123321456654789987',  # Replace 'your_x_token_value' with the actual token
            'Content-Type': 'application/json'
        }
        auth = HTTPBasicAuth('astroapi', 'A5hy72cs7b')

        server_url_dev = "http://cc85056373a8.vps.myjino.ru/api/v1/get_sefarial"
        # server_url_dev = "http://0.0.0.0:8068/api/v1/get_sefarial"
        response = requests.get(server_url_dev, auth=auth, headers=headers, params=request_payload)
        result = response.json()
        print(result)
        return result