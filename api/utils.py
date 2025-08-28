"""
Utilities for locating the default colleciton file.

Purpose
-------
Centralizes how the app determines the on disk JSON file to use when a caller
doesn't specify a filename. This keeps all filesystem conventions in one place
and lets higher layers (REST/GraphQL/GUI) stay agnostic about paths.

Design
------
We delegate to 'collectory.config.collection_path', which owns where data lives
(e.g., app data dir, file naming, extensions). That way, if we ever change the 
layout, this module doesn't need to know the details because 'config' always remains
the single source of truth.
"""

from collectory import config

DEFAULT_FILE = "default_collection"

def default_path():
    """
    Return the absolute path to the default collection JSON file.
    
    Currently resolves to 'config.collection_path(DEFAULT_FILE)', which usually
    maps to something like <DATA_DIR>/default_collection.json (see 'config').
    
    Notes
    -----
    - No I/O happens here, this just computes a path
    - Good future options:
        * Enviroment variable override (e.g., CURATION_COLLECTIOn)
        * Remember the last opened file in user settings and prefer that
        * Pass explicit file names from the GUI/CLI instead of relying on a default.
    """
    return config.collection_path(DEFAULT_FILE)