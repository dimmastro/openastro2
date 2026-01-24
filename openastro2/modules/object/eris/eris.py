from typing import Any, List, Tuple
from pathlib import Path
import shutil

from openastromod.skyfield_loader import load
from skyfield.constants import AU_KM
from skyfield.framelib import ecliptic_frame


class Eris:
    def __init__(self, bsp_path: str | None = None) -> None:
        self.bsp_path = bsp_path

    def process(self, *args: Any, **kwargs: Any) -> List[Tuple[Tuple[float, float, float, float, float, float], int]]:
        year = kwargs["year"]
        month = kwargs["month"]
        day = kwargs["day"]
        hour = kwargs["hour"]

        ts = load.timescale()
        t = ts.utc(year, month, day, *self._hour_to_hms(hour))

        try:
            eph = self._load_ephemeris()
            names = eph.names()
            if isinstance(names, dict):
                name_values = names.values()
            else:
                name_values = names
            name_map = {str(name).lower() for name in name_values}
            if "eris" not in name_map:
                print("Eris not present in loaded ephemeris.")
                return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]

            earth = eph["earth"]
            eris = eph["eris"]
            astrometric = earth.at(t).observe(eris)
            lon, lat, distance = astrometric.frame_latlon(ecliptic_frame)
            lon_deg = lon.degrees % 360.0
            lat_deg = lat.degrees
            dist_au = distance.au

            return [((lon_deg, lat_deg, dist_au, 0.0, 0.0, 0.0), 0)]
        except ValueError as exc:
            if "SPK data type" not in str(exc):
                raise
            return self._compute_with_spice(year, month, day, hour, t)

    def _compute_with_spice(self, year: int, month: int, day: int, hour: float, t) -> List[Tuple[Tuple[float, float, float, float, float, float], int]]:
        try:
            import spiceypy as spice
        except Exception as exc:
            print(f"spiceypy not available for Eris kernel: {exc}")
            return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]

        kernel_path = self._resolve_kernel_path()
        if kernel_path is None:
            print("Eris kernel not available for spiceypy.")
            return [((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)]

        leap_path = self._ensure_local_kernel("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls")
        de440_path = self._ensure_local_kernel("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp")
        spice.furnsh(str(leap_path))
        spice.furnsh(str(de440_path))
        spice.furnsh(str(kernel_path))
        try:
            et = spice.utc2et(f"{year:04d}-{month:02d}-{day:02d}T{self._hour_to_hms_str(hour)}")
            if not self._is_et_in_coverage(spice, str(kernel_path), 920136199, et):
                return self._compute_with_elements(spice, et, t)
            eris_state, _ = spice.spkgeo(920136199, et, "J2000", 0)
            eris_pos_km = eris_state[:3]
            earth_state, _ = spice.spkgeo(399, et, "J2000", 0)
            earth_pos_km = earth_state[:3]
        finally:
            spice.unload(str(kernel_path))
            spice.unload(str(de440_path))
            spice.unload(str(leap_path))

        geo_x = eris_pos_km[0] - earth_pos_km[0]
        geo_y = eris_pos_km[1] - earth_pos_km[1]
        geo_z = eris_pos_km[2] - earth_pos_km[2]

        lon_deg, lat_deg, dist_au = self._equatorial_to_ecliptic(geo_x, geo_y, geo_z)
        return [((lon_deg, lat_deg, dist_au, 0.0, 0.0, 0.0), 0)]

    def _load_ephemeris(self):
        if not self.bsp_path:
            return load("de440.bsp")

        if str(self.bsp_path).startswith(("http://", "https://")):
            kernel_path = self._ensure_local_kernel(self.bsp_path)
            return load(str(kernel_path))

        path = Path(self.bsp_path)
        if path.is_absolute():
            if path.exists():
                return load(str(path))
            return load("de440.bsp")

        module_root = Path(__file__).resolve().parents[3]
        repo_root = module_root.parent
        candidates = [
            module_root / self.bsp_path,
            repo_root / self.bsp_path,
        ]
        for candidate in candidates:
            if candidate.exists():
                return load(str(candidate))

        return load(self.bsp_path)

    def _resolve_kernel_path(self) -> Path | None:
        if not self.bsp_path:
            return None
        if str(self.bsp_path).startswith(("http://", "https://")):
            return self._ensure_local_kernel(self.bsp_path)

        path = Path(self.bsp_path)
        if path.is_absolute() and path.exists():
            return path

        module_root = Path(__file__).resolve().parents[3]
        repo_root = module_root.parent
        candidates = [
            module_root / self.bsp_path,
            repo_root / self.bsp_path,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _ensure_local_kernel(self, url: str) -> Path:
        filename = Path(url).name
        module_root = Path(__file__).resolve().parents[3]
        repo_root = module_root.parent
        for candidate in (module_root / filename, repo_root / filename):
            if candidate.exists():
                return candidate

        downloaded = Path(load.download(url))
        target = repo_root / filename
        try:
            shutil.copyfile(downloaded, target)
            return target
        except OSError:
            return downloaded

    def _equatorial_to_ecliptic(self, x_km: float, y_km: float, z_km: float) -> Tuple[float, float, float]:
        import math

        eps = math.radians(23.4392911)
        cos_eps = math.cos(eps)
        sin_eps = math.sin(eps)
        x = x_km
        y = y_km * cos_eps + z_km * sin_eps
        z = -y_km * sin_eps + z_km * cos_eps

        lon = math.degrees(math.atan2(y, x)) % 360.0
        hyp = math.hypot(x, y)
        lat = math.degrees(math.atan2(z, hyp))
        dist_au = math.sqrt(x * x + y * y + z * z) / AU_KM
        return lon, lat, dist_au

    def _compute_with_elements(self, spice, et: float, t) -> List[Tuple[Tuple[float, float, float, float, float, float], int]]:
        eris_au = self._eris_elements_to_au(t.tt)
        earth_state, _ = spice.spkgeo(399, et, "J2000", 10)
        earth_ecl_km = self._equatorial_to_ecliptic_xyz(*earth_state[:3])
        earth_ecl_au = tuple(coord / AU_KM for coord in earth_ecl_km)

        geo_x = eris_au[0] - earth_ecl_au[0]
        geo_y = eris_au[1] - earth_ecl_au[1]
        geo_z = eris_au[2] - earth_ecl_au[2]
        lon, lat, dist = self._xyz_to_lonlat(geo_x, geo_y, geo_z)
        return [((lon, lat, dist, 0.0, 0.0, 0.0), 0)]

    def _is_et_in_coverage(self, spice, kernel_path: str, body_id: int, et: float) -> bool:
        cover = spice.spkcov(kernel_path, body_id)
        for idx in range(0, len(cover), 2):
            if cover[idx] <= et <= cover[idx + 1]:
                return True
        return False

    def _eris_elements_to_au(self, jd_tt: float) -> Tuple[float, float, float]:
        import math

        # JPL#80 elements for Eris (system barycenter), epoch JED 2457709.5 (2016-11-17 TDB)
        a = 67.6533145827283
        e = 0.4422028467648986
        inc = math.radians(44.18677870482509)
        omega = math.radians(151.3771835065675)
        raan = math.radians(35.88579459831126)
        m0 = math.radians(204.6951495459583)
        n = math.radians(0.001771212)
        epoch = 2457709.5

        m = (m0 + n * (jd_tt - epoch)) % (2 * math.pi)
        e_anom = self._solve_kepler(m, e)
        true_anom = 2.0 * math.atan2(
            math.sqrt(1 + e) * math.sin(e_anom / 2.0),
            math.sqrt(1 - e) * math.cos(e_anom / 2.0),
        )
        r = a * (1.0 - e * math.cos(e_anom))
        arg = omega + true_anom
        cos_raan = math.cos(raan)
        sin_raan = math.sin(raan)
        cos_inc = math.cos(inc)
        sin_inc = math.sin(inc)
        cos_arg = math.cos(arg)
        sin_arg = math.sin(arg)

        x = r * (cos_raan * cos_arg - sin_raan * sin_arg * cos_inc)
        y = r * (sin_raan * cos_arg + cos_raan * sin_arg * cos_inc)
        z = r * (sin_arg * sin_inc)
        return x, y, z

    def _solve_kepler(self, m: float, e: float) -> float:
        import math

        e_anom = m if e < 0.8 else math.pi
        for _ in range(15):
            f = e_anom - e * math.sin(e_anom) - m
            f_prime = 1.0 - e * math.cos(e_anom)
            e_anom -= f / f_prime
        return e_anom

    def _equatorial_to_ecliptic_xyz(self, x_km: float, y_km: float, z_km: float) -> Tuple[float, float, float]:
        import math

        eps = math.radians(23.4392911)
        cos_eps = math.cos(eps)
        sin_eps = math.sin(eps)
        x = x_km
        y = y_km * cos_eps + z_km * sin_eps
        z = -y_km * sin_eps + z_km * cos_eps
        return x, y, z

    def _xyz_to_lonlat(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        import math

        lon = math.degrees(math.atan2(y, x)) % 360.0
        hyp = math.hypot(x, y)
        lat = math.degrees(math.atan2(z, hyp))
        dist = math.sqrt(x * x + y * y + z * z)
        return lon, lat, dist

    def _hour_to_hms(self, hour: float) -> Tuple[int, int, float]:
        h = int(hour)
        m_float = (hour - h) * 60.0
        m = int(m_float)
        s = (m_float - m) * 60.0
        return h, m, s

    def _hour_to_hms_str(self, hour: float) -> str:
        h, m, s = self._hour_to_hms(hour)
        return f"{h:02d}:{m:02d}:{s:06.3f}"
