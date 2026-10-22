import sys
from pathlib import Path

# Automatically inject project venv site-packages so scripts run seamlessly
# even if the virtual environment was not explicitly activated in the shell.
_BASE_DIR = Path(__file__).resolve().parent.parent
_VENV_DIR = _BASE_DIR / "venv"
if _VENV_DIR.exists():
    for _site_pkg in _VENV_DIR.glob("lib*/python*/site-packages"):
        _site_pkg_str = str(_site_pkg)
        if _site_pkg_str not in sys.path:
            sys.path.insert(0, _site_pkg_str)

