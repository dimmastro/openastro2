import os
from pathlib import Path

from skyfield import api
from skyfield.api import Loader

# Centralized Skyfield loader to keep ephemeris downloads in one place.
# Используем постоянный каталог внутри пакета openastro2, чтобы кэш не терялся при очистке /tmp.
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = str(PACKAGE_ROOT / "skyfield_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
load = Loader(CACHE_DIR)

# Ensure skyfield.api.load uses the same shared loader everywhere.
api.load = load
