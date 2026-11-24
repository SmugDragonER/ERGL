"""
All file and folder locations of the project, in ONE place.

Running from source:  BASE_DIR = the project folder (where gui.py is)
Running as .exe:      BASE_DIR = the folder where the .exe is

Expected layout in both cases:
    BASE_DIR/
    ├── tournament_db.json      (created automatically)
    └── assets/
        ├── Leaderboard.png
        ├── layout.json
        └── fonts/Montserrat/static/...
"""
import sys
from pathlib import Path

if getattr(sys, "frozen", False):            # running as .exe (PyInstaller sets sys.frozen)
    BASE_DIR = Path(sys.executable).parent   # folder where the .exe is
else:
    BASE_DIR = Path(__file__).parent.parent  # normal project folder (src/ -> project root)

ASSET_DIR = BASE_DIR / "assets"
FONT_DIR = ASSET_DIR / "fonts" / "Montserrat" / "static"
MAIN_LAYOUT_PATH = ASSET_DIR / "layout_main.json"
MINI_LAYOUT_PATH = ASSET_DIR / "layout_mini.json"
DB_PATH = BASE_DIR / "tournament_db.json"
