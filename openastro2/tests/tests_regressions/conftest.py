from pathlib import Path

import skyfield.iokit

try:
    from openastro2.openastromod import skyfield_loader
except ModuleNotFoundError:
    from openastromod import skyfield_loader


def _blocked_download(url, path, verbose=None, blocksize=128 * 1024, backup=False):
    raise RuntimeError(
        "Skyfield download is disabled in regression tests. "
        f"Populate the shared cache first: {Path(skyfield_loader.CACHE_DIR) / Path(path).name}"
    )


skyfield.iokit.download = _blocked_download
