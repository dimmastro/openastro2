from typing import Tuple, List
import datetime

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
