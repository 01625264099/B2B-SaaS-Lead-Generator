import sys
from pathlib import Path


LOCAL_PACKAGES = Path(__file__).resolve().parent / ".python-packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))
