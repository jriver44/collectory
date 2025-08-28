"""
Application services for Curation

Role
----
This module is a thin, stateless "service layer" that the web API (REST/GraphQL)
calls into. It centralizes reads/writes to the collection file and delegates domain
logic to 'collectory.collector' (write side: create) and 'collectory.analysis'
(read/compute-side: search, filter, aggregates).

Design choices
--------------
- **Stateless & simple I/O**: Each function loads the current items from 'default_path();
    on demand. This keeps call sites trivial and avoids caching bugs, at the cost of extra file
    I/O (fine for a desktop app and small datasets, see TODOs for scaling options).
- **Single source of truth**: Domain rules (IDs, timestamps, aggregates) live in the 'collectory.*'
    modules. Services orchestrate those calls

IMPORTANT / TODO
----------------
- **ID type alignment**: Items created by 'create_new_item' use UUID strings for 'id'. Here, 'get_item_by_id'
    takes and an 'int' and compares directly to 'item["id"]' (string). That will never match. Need to align the types.
    - Make REST route use <string:item_id>' and GraphQL resolver stop casting.
"""

from datetime import datetime
from api.utils import default_path
from collectory.collector import load_items, create_new_item
from collectory.analysis import (
    search_by_keyword,
    filter_by_category,
    get_category_distribution,
    get_time_distribution,
)

def get_item_by_id(item_id: int) -> dict | None:
    """
    Return a single item by ID or None if not found.
    
    NOTE/TODO: 'item_id' is typed as int, but items use UUID **stirng** for 'id'.
    This strict comparison will fail. 
    """
    items = load_items(default_path())
    return next((item for item in items if item["id"] == item_id), None)

def create_item(name: str, category: str, quantity: int) -> dict:
    """
    Create a new item and return it.

    Orchestrates:
        - Load current items from the default collection file.
        - Generate a timestamp (YYYY-MM-DD HH:MM:SS).
        - Delegate to 'create_new_item', which mutates the in-memory list and
            returns the created item (with UUID 'id' and 'time' set).

    NOTE: This function does **not** persist to disk. Persistence is handled by the 
    CLI's save flow or the GUI's explicit Save action.
    """
    items = load_items(default_path())
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return create_new_item(name, items, category, quantity, ts)

def search_items(keyword: str) -> list[dict]:
    """
    Case-insensitive substring search over item names.

    Delegates to 'collectory.analysis.search_by_keyword'.
    """
    items = load_items(default_path())
    return search_by_keyword(items, keyword)

def filter_items(category: str) -> list[dict]:
    """
    Exact, case-insensitive category filter.

    Delegates to 'collectory.analysis.filter_by_category'.
    """
    items = load_items(default_path())
    return filter_by_category(items, category)

def category_distribution() -> list[dict]:
    """
    Aggregate quantity per category.

    Returns a list of { "category": <str>, "count": <int> } objects,
    reshaped from the dict returned by 'get_category_distribution'.
    """
    dist = get_category_distribution(load_items(default_path()))
    return [{"category": k, "count": v} for k, v in dist.items()]

def time_distribution() -> list[dict]:
    """
    Aggregate quantity per time period (default period: YYYY-MM).

    Returns a list of {"period": <str>, "count": <int> } objects,
    reshaped from the dict returned by 'get_time_distribution'.
    """
    td = get_time_distribution(load_items(default_path()))
    return [{"period": k, "count": v} for k, v in td.items()]

def get_all_items() -> list[dict]:
    """
    Return the full list of items from teh default collection file.
    
    TODO: If we introduce a long lived in-memory model in the GUI,
    we need to pass that into services to avoid re-reading the file
    on every call.
    """
    return load_items(default_path())
