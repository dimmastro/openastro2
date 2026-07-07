import os
import shutil
from pathlib import Path

from skyfield import api
from skyfield.api import Loader

# Centralized Skyfield loader to keep ephemeris downloads in one place.
# По умолчанию используем каталог внутри пакета `openastro2`, потому что
# он уже включен в проект и не зависит от текущей рабочей директории pytest.
REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_CACHE_DIR = PACKAGE_ROOT / "skyfield_cache"
LEGACY_CACHE_DIR = REPO_ROOT / "skyfield_cache"
PACKAGE_DE421_PATH = PACKAGE_ROOT / "de421.bsp"


def _choose_cache_dir() -> Path:
    override = os.environ.get("OPENASTRO2_SKYFIELD_CACHE_DIR")
    if override:
        return Path(override).expanduser()

    if any(PACKAGE_CACHE_DIR.iterdir()) if PACKAGE_CACHE_DIR.exists() else False:
        return PACKAGE_CACHE_DIR

    if any(LEGACY_CACHE_DIR.iterdir()) if LEGACY_CACHE_DIR.exists() else False:
        return LEGACY_CACHE_DIR

    return PACKAGE_CACHE_DIR


def _bootstrap_ephemeris(cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_de421_path = cache_dir / "de421.bsp"

    if cache_de421_path.exists():
        return

    if PACKAGE_DE421_PATH.exists():
        shutil.copy2(PACKAGE_DE421_PATH, cache_de421_path)


CACHE_DIR = _choose_cache_dir()
_bootstrap_ephemeris(CACHE_DIR)
load = Loader(str(CACHE_DIR))

# Ensure skyfield.api.load uses the same shared loader everywhere.
api.load = load
