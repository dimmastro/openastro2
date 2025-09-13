from typing import Tuple, List, Union, Optional
import datetime
import math


def utc_to_local(year: int, month: int, day: int, hour_decimal: float, timezone: float) -> Tuple[int, int, int, int, int, int]:
    """
    Convert UTC time to local time based on timezone offset.

    :param year: int
    :param month: int
    :param day: int
    :param hour_decimal: float (e.g., 13.75 for 13:45)
    :param timezone: float, timezone offset in hours (e.g., +3.0 for MSK, -5.0 for EST)
    :return: tuple (year, month, day, hour, minute, second)
    """

    # Convert decimal hour to h, m, s
    h, m, s = decHour(hour_decimal)

    # Create UTC datetime
    utc = datetime.datetime(year, month, day, h, m, s)

    # Apply timezone offset
    tz_offset = datetime.timedelta(seconds=timezone * 3600)
    loc = utc + tz_offset  # utc + tz_offset gives local time

    # Return as tuple
    return (loc.year, loc.month, loc.day, loc.hour, loc.minute, loc.second)


def local_to_utc(year: int, month: int, day: int, hour_decimal: float, timezone: float) -> Tuple[int, int, int, int, int, int]:
    """
    Convert local time to UTC time.

    :param year: int
    :param month: int
    :param day: int
    :param hour_decimal: float, local time in decimal hours (e.g., 15.5 = 15:30:00)
    :param timezone: float, timezone offset in hours (e.g., +3.0 for MSK, -5.0 for EST)
    :return: tuple (utc_year, utc_month, utc_day, utc_hour_decimal, utc_hour, utc_minute, utc_second)
    """

    # Parse local time
    h, m, s = decHour(hour_decimal)
    local_dt = datetime.datetime(year, month, day, h, m, s)

    # Subtract timezone to get UTC
    tz_offset = datetime.timedelta(seconds=timezone * 3600)
    utc_dt = local_dt - tz_offset

    # Convert UTC time to decimal hour
    utc_hour_decimal = decHourJoin(utc_dt.hour, utc_dt.minute, utc_dt.second)

    # Print info (if dprint is defined)
    # print(f'localToUtc: {local_dt} => {utc_dt} (TZ: {timezone:+.1f})')

    # Return extended tuple: (year, month, day, hour_decimal, h, m, s)
    return (
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        # utc_hour_decimal,
        utc_dt.hour,
        utc_dt.minute,
        utc_dt.second
    )


# decimal hour to minutes and seconds
def decHour(input: float) -> List[int]:
    hours = int(input)
    mands = (input - hours) * 60.0
    mands = round(mands, 5)
    minutes = int(mands)
    seconds = int(round((mands - minutes) * 60))
    return [hours, minutes, seconds]


# join hour, minutes, seconds, timezone integere to hour float
def decHourJoin(inH: int, inM: int, inS: int) -> float:
    dh = float(inH)
    dm = float(inM) / 60
    ds = float(inS) / 3600
    output = dh + dm + ds
    return output


# Datetime offset to float in hours
def offsetToTz(dtoffset: datetime.timedelta) -> float:
    dh = float(dtoffset.days * 24)
    sh = float(dtoffset.seconds / 3600.0)
    output = dh + sh
    return output


# decimal timezone string
def decTzStr(tz: float) -> str:
    if tz > 0:
        h = int(tz)
        m = int((float(tz) - float(h)) * float(60))
        return " +%(#1)02d:%(#2)02d" % {'#1': h, '#2': m}
    else:
        h = int(tz)
        m = int((float(tz) - float(h)) * float(60)) / -1
        return "-%(#1)02d:%(#2)02d" % {'#1': h / -1, '#2': m}


# degree difference
def degreeDiff(a: Union[int, float], b: Union[int, float], round_aspects: bool = False) -> float:
    if round_aspects:
        a = int(a)
        b = int(b)
    out = float()
    if a > b:
        out = a - b
    if a < b:
        out = b - a
    if out > 180.0:
        out = 360.0 - out
    return out


# degree difference (alternative version)
def degreeDiff2(a: Union[int, float], b: Union[int, float], round_aspects: bool = False) -> float:
    if round_aspects:
        a = int(a)
        b = int(b)
    out = float()
    if a > b:
        out = a - b
    if a < b:
        out = b - a
    if out > 360.0:
        out = 360.0 - out
    if out < -360.0:
        out = out + 360
    return out


# decimal to degrees (a°b'c") for HTML
def dec2deg(dec: float, type: str = "3") -> str:
    dec = float(dec)
    a = int(dec)
    a_new = (dec - float(a)) * 60.0
    b_rounded = int(round(a_new))
    b = int(a_new)
    c = int(round((a_new - float(b)) * 60.0))
    out = ""
    if type == "3":
        out = '%(#1)02d&#176;%(#2)02d&#39;%(#3)02d&#34;' % {'#1': a, '#2': b, '#3': c}
    elif type == "2":
        out = '%(#1)02d&#176;%(#2)02d&#39;' % {'#1': a, '#2': b_rounded}
    elif type == "1":
        out = '%(#1)02d&#176;' % {'#1': a}
    elif type == "0":
        out = '%(#1)2d' % {'#1': a}
    return str(out)


# decimal to degrees (a°b'c") for plain text
def dec2deg_str(dec: float, type: str = "3") -> str:
    dec = float(dec)
    a = int(dec)
    a_new = (dec - float(a)) * 60.0
    b_rounded = int(round(a_new))
    b = int(a_new)
    c = int(round((a_new - float(b)) * 60.0))
    out = ""
    if type == "3":
        out = '%(#1)°%(#2)`%(#3)``' % {'#1': a, '#2': b, '#3': c}
    elif type == "2":
        out = f"{a}°{b_rounded}'"
    elif type == "1":
        out = '%(#1)°' % {'#1': a}
    elif type == "0":
        out = '%(#1)2d' % {'#1': a}
    return str(out)


# NEW UTILITY FUNCTIONS - Extracted from duplicated code

# Normalize degree value to 0-360 range
def normalize_degree(degree: float) -> float:
    """Normalize degree value to 0-360 range."""
    while degree < 0:
        degree += 360.0
    while degree >= 360.0:
        degree -= 360.0
    return degree


# Calculate zodiac sign from degree
def get_zodiac_sign(degree_ut: float) -> Tuple[int, float]:
    """Calculate zodiac sign and degree within sign from absolute degree.
    
    :param degree_ut: Absolute degree (0-360)
    :return: Tuple of (zodiac_sign_index, degree_within_sign)
    """
    normalized_degree = normalize_degree(degree_ut)
    
    for x in range(12):
        deg_low = float(x * 30)
        deg_high = float((x + 1) * 30)
        if normalized_degree >= deg_low and normalized_degree < deg_high:
            return x, normalized_degree - deg_low
    
    # Handle the special case where degree is exactly 360 (= 0)
    if normalized_degree == 0:
        return 0, 0.0
    
    # Fallback for edge cases
    return 0, normalized_degree


# Convert coordinates to X position in polar coordinates
def sliceToX(slice_num: int, radius: float, offset: float) -> float:
    """Convert slice number and offset to X coordinate in polar system."""
    plus = (math.pi * offset) / 180
    radial = ((math.pi / 6) * slice_num) + plus
    return radius * (math.cos(radial) + 1)


# Convert coordinates to Y position in polar coordinates  
def sliceToY(slice_num: int, radius: float, offset: float) -> float:
    """Convert slice number and offset to Y coordinate in polar system."""
    plus = (math.pi * offset) / 180
    radial = ((math.pi / 6) * slice_num) + plus
    return radius * ((math.sin(radial) / -1) + 1)


# Format latitude coordinate as string
def lat2str(coord: float, north_label: str = "N", south_label: str = "S") -> str:
    """Convert floating latitude to formatted string (DD°MM'SS" N/S)."""
    sign = north_label
    if coord < 0.0:
        sign = south_label
        coord = abs(coord)
    deg = int(coord)
    min_val = int((float(coord) - deg) * 60)
    sec = int(round(float(((float(coord) - deg) * 60) - min_val) * 60.0))
    return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': min_val, '#3': sec, '#4': sign}


# Format longitude coordinate as string
def lon2str(coord: float, east_label: str = "E", west_label: str = "W") -> str:
    """Convert floating longitude to formatted string (DD°MM'SS" E/W)."""
    sign = east_label
    if coord < 0.0:
        sign = west_label
        coord = abs(coord)
    deg = int(coord)
    min_val = int((float(coord) - deg) * 60)
    sec = int(round(float(((float(coord) - deg) * 60) - min_val) * 60.0))
    return "%(#1)02d°%(#2)02d'%(#3)02d\" %(#4)s" % {'#1': deg, '#2': min_val, '#3': sec, '#4': sign}
