from skyfield.api import load, wgs84
from skyfield.framelib import ICRS
from skyfield.positionlib import build_position
from skyfield.framelib import ecliptic_frame


def get_fixar_ecliptic_latlon(eph, planet_name, t1, t2, lat, lon):
    earth, sun, planet = eph['earth'], eph['sun'], eph[planet_name]
    # ts = load.timescale()
    # t1 = ts.utc(2001, 3, 19, 10, 32)
    # t2 = ts.utc(2002, 3, 19, 10, 31)
    m1 = earth.at(t1).observe(planet).frame_xyz(ICRS).au
    s1 = earth.at(t1).observe(sun).frame_xyz(ICRS).au
    s2 = earth.at(t2).observe(sun).frame_xyz(ICRS).au
    e21 = s2 - s1
    m0 = m1 + e21
    position1 = build_position(m1, t=t1)
    # print(position1.frame_latlon(ecliptic_frame))
    # lat1, lon1, distance1 = position1.frame_latlon(ecliptic_frame)
    # print(' {:.4f} latitude'.format(lat1.degrees))
    # print(' {:.4f} longitude'.format(lon1.degrees))
    # print(' {:.3f} au distant'.format(distance1.au))

    position0 = build_position(m0, t=t1)
    # print(position0.frame_latlon(ecliptic_frame))
    lat0, lon0, distance0 = position0.frame_latlon(ecliptic_frame)
    #
    # position0 = build_position(m0, t=t2)
    # print(position0.frame_latlon(ecliptic_frame))
    return [lat0.degrees, lon0.degrees, distance0.km]


def get_fixar_earth_ecliptic_latlon(eph, planet_name, t1, t2, lat, lon):
    earth, sun, planet = eph['earth'], eph['sun'], eph[planet_name]
    # ts = load.timescale()
    # t1 = ts.utc(2001, 3, 19, 10, 32)
    # t2 = ts.utc(2002, 3, 19, 10, 31)
    s1 = earth.at(t1).observe(sun).frame_xyz(ICRS).au
    s2 = earth.at(t2).observe(sun).frame_xyz(ICRS).au
    e21 = s1 - s2
    m2 = earth.at(t2).observe(planet).frame_xyz(ICRS).au
    m22 = m2 + e21
    # position1 = build_position(m1, t=t1)
    # print(position1.frame_latlon(ecliptic_frame))
    # lat1, lon1, distance1 = position1.frame_latlon(ecliptic_frame)
    # print(' {:.4f} latitude'.format(lat1.degrees))
    # print(' {:.4f} longitude'.format(lon1.degrees))
    # print(' {:.3f} au distant'.format(distance1.au))

    position0 = build_position(m22, t=t1)
    # print(position0.frame_latlon(ecliptic_frame))
    lat0, lon0, distance0 = position0.frame_latlon(ecliptic_frame)
    #
    # position0 = build_position(m0, t=t2)
    # print(position0.frame_latlon(ecliptic_frame))
    return [lat0.degrees, lon0.degrees, distance0.km]



def get_fixar_ecliptic_latlon_arr(planet_name_dic, t1, t2, lat, lon):

    eph = load('de421.bsp')
    lat_arr = []
    lon_arr = []
    for planet_code, planet_name in planet_name_dic.items():
        # Получение объекта планеты по коду
        [p_lat, p_lon, p_dist] = get_fixar_ecliptic_latlon(eph, planet_code, t1, t2, lat, lon)
        lat_arr.append(p_lat)
        lon_arr.append(p_lon)

    return [lat_arr, lon_arr]


def get_fixar_earth_ecliptic_latlon_arr(planet_name_dic, t1, t2, lat, lon):

    eph = load('de421.bsp')
    lat_arr = []
    lon_arr = []
    for planet_code, planet_name in planet_name_dic.items():
        # Получение объекта планеты по коду
        [p_lat, p_lon, p_dist] = get_fixar_earth_ecliptic_latlon(eph, planet_code, t1, t2, lat, lon)
        lat_arr.append(p_lat)
        lon_arr.append(p_lon)

    return [lat_arr, lon_arr]