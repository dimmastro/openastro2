# openastro2/modules/object/zemletochki/zemletochki.py
import json
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth


class Zemletochki:
    """
    Модуль Теории землеточек Дмитрия Мирцева
    Вычисляет фиксированную проекцию неба на землю по методам:
    - Землеточки
    - Землеточки от Гринвича
    - Сефариал
    """
    def __init__(self, server_url, server_endpoint, user, password, x_token, zt_type):
        self.server_url = server_url
        self.server_endpoint = server_endpoint
        self.user = user
        self.password = password
        self.x_token = x_token
        self.zt_type = zt_type

    # def process(self, year,month,day,hour,h,m,s,geolon,geolat,altitude,openastrocfg,):
    def process(self, *args, **kwargs):
        year = kwargs['year']
        month = kwargs['month']
        day = kwargs['day']
        hour = kwargs['hour']
        h = kwargs['h']
        m = kwargs['m']
        s = kwargs['s']
        geolat = kwargs['geolat']
        geolon = kwargs['geolon']
        openastrocfg = kwargs['openastrocfg']
        zt_type = 1
        if openastrocfg['type'] == "Zemletochki": # Землеточки
            zt_type = 1
        elif openastrocfg['type'] == "ZemletochkiG": # Землеточки от Гринвича
            zt_type = 2
        elif openastrocfg['type'] == "Sefarial": # Сефариал
            zt_type = 3

        try:
            planet_pos=[]
            zt_degree_ut = self.zt_request(year, month, day, h, m, s, geolat, geolon, zt_type)
            planet_pos.append(((zt_degree_ut[0], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[1], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[2], 0, 0, 0, 0, 0),0))
            planet_pos.append(((zt_degree_ut[3], 0, 0, 0, 0, 0),0))

        except Exception as _ex:
            print(_ex)
            planet_pos = []
        return planet_pos


    def zt_request(self, year, month, day, h, m, s, geolat, geolon, zt_type):
        dt = datetime(year, month, day, h, m, s)
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        request_payload = {
            "dt_str": dt_str,
            "geolat": geolat,
            "geolon": geolon,
            "type": zt_type,
        }
        headers = {
            'X-Token': self.x_token,  # Replace 'your_x_token_value' with the actual token
            'Content-Type': 'application/json'
        }
        auth = HTTPBasicAuth(self.user, self.password)

        server_url = self.server_url + self.server_endpoint
        response = requests.get(server_url, auth=auth, headers=headers, params=request_payload)
        result = response.json()
        return result
