from pathlib import Path
import sys
import os

DATA_DIR = Path.home() / ".collectory"
try:
    DATA_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"ERROR: Unable to create data directory {DATA_DIR}: {e}")
    sys.exit(1)
    
if not DATA_DIR.is_dir() or not os.access(DATA_DIR, os.W_OK):
    print(f"ERROR: Data directory {DATA_DIR} is not writable.")
    sys.exit(1)

DEFAULT_COLLECTION = "default"
BACKUP_SUFFIX = "_backup"
MAX_BACKUPS = 3 # Three backup saves

AUTOSAVE_ENABLED = True
AUTOSAVE_INTERVAL = 300 # 5 min delay

def collection_path(name: str | None = None) -> Path:
    fname = (name or DEFAULT_COLLECTION) + ".json"
    return DATA_DIR / fname