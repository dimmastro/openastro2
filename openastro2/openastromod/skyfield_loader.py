import os

from skyfield import api
from skyfield.api import Loader

# Centralized Skyfield loader to keep ephemeris downloads in one place.
CACHE_DIR = "/tmp/openastro2"
os.makedirs(CACHE_DIR, exist_ok=True)
load = Loader(CACHE_DIR)

# Ensure skyfield.api.load uses the same shared loader everywhere.
api.load = load
