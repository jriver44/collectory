"""
Curation configuration and data directory setup.

Responsibilities
-----------------
    - Define global configuration constants used by both CLI and GUI.
    - Establish the on-disk data directory under the user's home (~/.collectory).
    - Validate writeablility of the data directory at import time (fail fast).
    
Relationships
--------------
Used by:
    - CLI entrypoint for load/save paths and autosave/backup policy.
    - Any persistence helpers that need to resolve a collection path.
    
Persistence boundry
---------------------
    - This module *performs I/O at import time* (mkdir, permission check) to ensure
    the application has a writeable state directory before continuing.
    
Threading
---------
    - No threading primitives are defined here, constants are read concurrently.
    Writes to files are guarded elsewhere (e.g. CLI's '_save_lock').
    
Notes
------
    - Import side effects: importing this module may print errors and call 'sys.exit(1)' if the
    data directory cannot be created/written. This is intentional to fail
    fast early in the program's lifecycle.
    - Default paths are platform-agnostic via 'pathlib.Path.home()'.
"""

from pathlib import Path
import sys
import os

# Root directory for all Curation data (collections + backups).
DATA_DIR = Path.home() / ".collectory"
try:
    # Create the directory if it doesn't exist. Save to call repeatedly.
    DATA_DIR.mkdir(exist_ok=True)
except Exception as e:
    # Fast fail: continuing without a writable data directory would corrupt UX.
    print(f"ERROR: Unable to create data directory {DATA_DIR}: {e}")
    sys.exit(1)
    
# Verify that the path is a directory and is writeable by the current user.
if not DATA_DIR.is_dir() or not os.access(DATA_DIR, os.W_OK):
    print(f"ERROR: Data directory {DATA_DIR} is not writable.")
    sys.exit(1)

# -- Collection file / backup -----------------------------------------------------

# Default logical collection name (used when no name is supplied).
DEFAULT_COLLECTION = "default"

# Suffix used when writing timestamped backup files.
BACKUP_SUFFIX = "_backup"

# Maxiumum number of most-recent backups to retain during rotation.
MAX_BACKUPS = 3 # Three backup saves

# Autosave feature flags (consumed by the CLI's autosave loop).
AUTOSAVE_ENABLED = True
AUTOSAVE_INTERVAL = 300 # 5 min delay

# -- Path helpers --------------------------------------------------------------------

def collection_path(name: str | None = None) -> Path:
    """Return the full path to the JSON file for a given collection name.
    
    Args:
        name: logical collection name without extension, if None or empty, falls back
        to DEFAULT_COLLECTION.
        
    Returns:
        A 'Path' to the JSON file inside DATA_DIR.
        
    Examples:
        >>> collection_path("my_stuff").name
        'my_stuff.json'
        >>> collection_path(None).name
        'default.json'
    
    """
    fname = (name or DEFAULT_COLLECTION) + ".json"
    return DATA_DIR / fname