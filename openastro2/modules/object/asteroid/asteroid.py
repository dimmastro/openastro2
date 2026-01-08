from typing import Any, List, Tuple
from pathlib import Path

import swisseph as swe


class Asteroid:
    def __init__(self, asteroid_id: int, name: str = "") -> None:
        self.asteroid_id = int(asteroid_id)
        self.name = name

    def process(self, *args: Any, **kwargs: Any) -> List[Tuple[Tuple[float, float, float, float, float, float], int]]:
        year = kwargs["year"]
        month = kwargs["month"]
        day = kwargs["day"]
        hour = kwargs["hour"]
        geolon = kwargs["geolon"]
        geolat = kwargs["geolat"]
        altitude = kwargs["altitude"]
        openastrocfg = kwargs["openastrocfg"]

        ephe_path = self._ephe_path()
        asteroid_file = Path(ephe_path) / f"se{self.asteroid_id:05d}s.se1"
        if not asteroid_file.exists():
            print(f"Asteroid ephemeris file not found: {asteroid_file}")
            return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]
        if asteroid_file.stat().st_size < 1024:
            print(f"Asteroid ephemeris file looks invalid (too small): {asteroid_file}")
            return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]
        with asteroid_file.open("rb") as handle:
            header = handle.read(64)
        if header.lstrip().startswith(b"<"):
            print(f"Asteroid ephemeris file looks invalid (HTML content): {asteroid_file}")
            return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]

        swe.set_ephe_path(ephe_path)
        swe.set_topo(geolon, geolat, altitude)

        iflag = swe.FLG_SWIEPH + swe.FLG_SPEED
        if openastrocfg.get("postype") == "truegeo":
            iflag += swe.FLG_TRUEPOS
        elif openastrocfg.get("postype") == "topo":
            iflag += swe.FLG_TOPOCTR
        elif openastrocfg.get("postype") == "helio":
            iflag += swe.FLG_HELCTR

        if openastrocfg.get("zodiactype") == "sidereal":
            iflag += swe.FLG_SIDEREAL
            mode = f"SIDM_{openastrocfg.get('siderealmode')}"
            if hasattr(swe, mode):
                swe.set_sid_mode(getattr(swe, mode))

        jul_day_ut = swe.julday(year, month, day, hour)
        body_id = swe.AST_OFFSET + self.asteroid_id
        ret_flag = swe.calc_ut(jul_day_ut, body_id, iflag)
        return [ret_flag]

    def _ephe_path(self) -> str:
        data_dir = Path(__file__).resolve().parents[3]
        return str(data_dir / "swiss_ephemeris")
