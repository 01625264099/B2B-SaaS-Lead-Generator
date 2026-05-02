import os
import runpy
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PROJECT_DIR.parent
STREAMLIT_HOME = PROJECT_DIR / ".streamlit-home"
LOG_PATH = PROJECT_DIR / "streamlit.log"

os.chdir(PROJECT_DIR)
os.environ["PYTHONPATH"] = str(WORKSPACE_DIR / ".python-packages")
os.environ["USERPROFILE"] = str(STREAMLIT_HOME)
os.environ["HOME"] = str(STREAMLIT_HOME)
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

sys.path.insert(0, str(WORKSPACE_DIR / ".python-packages"))
sys.argv = [
    "streamlit",
    "run",
    "app.py",
    "--server.address",
    "0.0.0.0",
    "--server.port",
    "8501",
]

with LOG_PATH.open("w", encoding="utf-8") as log_file:
    sys.stdout = log_file
    sys.stderr = log_file
    runpy.run_module("streamlit", run_name="__main__")
