from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import shutil
from typing import Any, Dict, Iterable, List, Optional, Tuple

from openastromod.skyfield_loader import load
from skyfield.constants import AU_KM
from skyfield.framelib import ecliptic_frame


@dataclass
class TnoElements:
    epoch: float
    a: float
    e: float
    inc_deg: float
    raan_deg: float
    argp_deg: float
    mean_anom_deg: float
    mean_motion_deg_per_day: float


class Tno:
    def __init__(self, objects: Iterable[Dict[str, Any]]) -> None:
        self.objects = list(objects)

    def process(self, *args: Any, **kwargs: Any) -> List[Tuple[Tuple[float, float, float, float, float, float], int]]:
        year = kwargs["year"]
        month = kwargs["month"]
        day = kwargs["day"]
        hour = kwargs["hour"]

        ts = load.timescale()
        t = ts.utc(year, month, day, *self._hour_to_hms(hour))

        results: List[Tuple[Tuple[float, float, float, float, float, float], int]] = []
        for entry in self.objects:
            results.append(self._compute_for_object(entry, t, year, month, day, hour))
        return results

    def _compute_for_object(
        self,
        entry: Dict[str, Any],
        t,
        year: int,
        month: int,
        day: int,
        hour: float,
    ) -> Tuple[Tuple[float, float, float, float, float, float], int]:
        kernel_url = entry.get("kernel_url")
        naif_id = entry.get("naif_id")
        elements = entry.get("elements")

        if kernel_url and naif_id is not None:
            try:
                return self._compute_with_spice(kernel_url, int(naif_id), t, year, month, day, hour)
            except Exception as exc:
                print(f"TNO kernel fallback ({entry.get('name', 'unknown')}): {exc}")

        if elements:
            elem = self._parse_elements(elements)
            return self._compute_with_elements(elem, t)

        return ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0)

    def _compute_with_spice(
        self,
        kernel_url: str,
        naif_id: int,
        t,
        year: int,
        month: int,
        day: int,
        hour: float,
    ) -> Tuple[Tuple[float, float, float, float, float, float], int]:
        try:
            import spiceypy as spice
        except Exception as exc:
            raise RuntimeError(f"spiceypy not available: {exc}") from exc

        kernel_path = self._ensure_local_kernel(kernel_url)
        leap_path = self._ensure_local_kernel("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls")
        de440_path = self._ensure_local_kernel("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp")

        spice.furnsh(str(leap_path))
        spice.furnsh(str(de440_path))
        spice.furnsh(str(kernel_path))
        try:
            et = spice.utc2et(f"{year:04d}-{month:02d}-{day:02d}T{self._hour_to_hms_str(hour)}")
            if not self._is_et_in_coverage(spice, str(kernel_path), naif_id, et):
                raise RuntimeError("date outside kernel coverage")
            body_state, _ = spice.spkgeo(naif_id, et, "J2000", 0)
            body_pos_km = body_state[:3]
            earth_state, _ = spice.spkgeo(399, et, "J2000", 0)
            earth_pos_km = earth_state[:3]
        finally:
            spice.unload(str(kernel_path))
            spice.unload(str(de440_path))
            spice.unload(str(leap_path))

        geo_x = body_pos_km[0] - earth_pos_km[0]
        geo_y = body_pos_km[1] - earth_pos_km[1]
        geo_z = body_pos_km[2] - earth_pos_km[2]
        lon, lat, dist = self._xyz_to_lonlat(geo_x / AU_KM, geo_y / AU_KM, geo_z / AU_KM)
        return ((lon, lat, dist, 0.0, 0.0, 0.0), 0)

    def _compute_with_elements(self, elements: TnoElements, t) -> Tuple[Tuple[float, float, float, float, float, float], int]:
        obj_helio = self._elements_to_xyz_au(elements, t.tt)
        earth_helio = self._earth_heliocentric_au(t)

        geo_x = obj_helio[0] - earth_helio[0]
        geo_y = obj_helio[1] - earth_helio[1]
        geo_z = obj_helio[2] - earth_helio[2]
        lon, lat, dist = self._xyz_to_lonlat(geo_x, geo_y, geo_z)
        return ((lon, lat, dist, 0.0, 0.0, 0.0), 0)

    def _earth_heliocentric_au(self, t) -> Tuple[float, float, float]:
        # Сначала используем локальный de440.bsp, чтобы не зависеть от сети.
        eph = self._load_de440_ephemeris()
        sun = eph["sun"]
        earth = eph["earth"]
        earth_helio = sun.at(t).observe(earth).frame_xyz(ecliptic_frame).au
        return (earth_helio[0], earth_helio[1], earth_helio[2])

    def _load_de440_ephemeris(self):
        de440_path = self._resolve_default_kernel_path("de440.bsp")
        if de440_path is not None:
            return load(str(de440_path))
        return load("de440.bsp")

    def _elements_to_xyz_au(self, elements: TnoElements, jd_tt: float) -> Tuple[float, float, float]:
        inc = math.radians(elements.inc_deg)
        raan = math.radians(elements.raan_deg)
        argp = math.radians(elements.argp_deg)
        mean_anom = math.radians(elements.mean_anom_deg)
        mean_motion = math.radians(elements.mean_motion_deg_per_day)

        m = (mean_anom + mean_motion * (jd_tt - elements.epoch)) % (2 * math.pi)
        e_anom = self._solve_kepler(m, elements.e)
        true_anom = 2.0 * math.atan2(
            math.sqrt(1 + elements.e) * math.sin(e_anom / 2.0),
            math.sqrt(1 - elements.e) * math.cos(e_anom / 2.0),
        )
        r = elements.a * (1.0 - elements.e * math.cos(e_anom))
        arg = argp + true_anom

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

    def _parse_elements(self, elements: Dict[str, Any]) -> TnoElements:
        return TnoElements(
            epoch=float(elements["epoch"]),
            a=float(elements["a"]),
            e=float(elements["e"]),
            inc_deg=float(elements["inc_deg"]),
            raan_deg=float(elements["raan_deg"]),
            argp_deg=float(elements["argp_deg"]),
            mean_anom_deg=float(elements["mean_anom_deg"]),
            mean_motion_deg_per_day=float(elements["mean_motion_deg_per_day"]),
        )

    def _solve_kepler(self, m: float, e: float) -> float:
        e_anom = m if e < 0.8 else math.pi
        for _ in range(15):
            f = e_anom - e * math.sin(e_anom) - m
            f_prime = 1.0 - e * math.cos(e_anom)
            e_anom -= f / f_prime
        return e_anom

    def _xyz_to_lonlat(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        lon = math.degrees(math.atan2(y, x)) % 360.0
        hyp = math.hypot(x, y)
        lat = math.degrees(math.atan2(z, hyp))
        dist = math.sqrt(x * x + y * y + z * z)
        return lon, lat, dist

    def _is_et_in_coverage(self, spice, kernel_path: str, body_id: int, et: float) -> bool:
        cover = spice.spkcov(kernel_path, body_id)
        for idx in range(0, len(cover), 2):
            if cover[idx] <= et <= cover[idx + 1]:
                return True
        return False

    def _ensure_local_kernel(self, url: str) -> Path:
        filename = Path(url).name
        for candidate in self._iter_default_kernel_candidates(filename):
            if candidate.exists():
                return candidate

        downloaded = Path(load.download(url))
        repo_root = Path(__file__).resolve().parents[3].parent
        target = repo_root / filename
        try:
            shutil.copyfile(downloaded, target)
            return target
        except OSError:
            return downloaded

    def _resolve_default_kernel_path(self, filename: str) -> Path | None:
        for candidate in self._iter_default_kernel_candidates(filename):
            if candidate.exists():
                return candidate
        return None

    def _iter_default_kernel_candidates(self, filename: str) -> Tuple[Path, ...]:
        module_root = Path(__file__).resolve().parents[3]
        repo_root = module_root.parent
        # Дополнительно проверяем cwd, потому что часть запусков кладёт bsp рядом с рабочим проектом.
        cwd_root = Path.cwd()
        return (
            module_root / filename,
            repo_root / filename,
            cwd_root / filename,
        )

    def _hour_to_hms(self, hour: float) -> Tuple[int, int, float]:
        h = int(hour)
        m_float = (hour - h) * 60.0
        m = int(m_float)
        s = (m_float - m) * 60.0
        return h, m, s

    def _hour_to_hms_str(self, hour: float) -> str:
        h, m, s = self._hour_to_hms(hour)
        return f"{h:02d}:{m:02d}:{s:06.3f}"
