# run_app.py
# Starts the Streamlit app while loading project-local packages.

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_PACKAGES = os.path.join(BASE_DIR, ".python-packages")

if os.path.isdir(LOCAL_PACKAGES) and LOCAL_PACKAGES not in sys.path:
    sys.path.insert(0, LOCAL_PACKAGES)

sys.argv = [
    "streamlit",
    "run",
    "app.py",
    "--server.port",
    "8501",
    "--server.address",
    "localhost",
]

from streamlit.web.cli import main

main()
