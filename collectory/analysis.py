"""
Domain-level operations for collection items.

This module contains pure data operations used by both the CLI and GUI:
    - Mutations that update items or the item list in place.
    - Read-only analytics helpers (category/time aggregations)
    - Simple search/filter utilities
    
Data model (current assumptions)
--------------------------------
Each item is a dict with the following keys:
    id:       str # UUIDv4 string
    name:     str
    category: str
    quantity: int
    time:     str # timestamp formatted as "%Y-%m-%d %H:%M:%S"
    
Notes
-----
- Functions here intentionally avoid any file or UI I/O.
- Mutating functions document whether they modify arguemnts in place.
- Time parsing in 'get_time_distribution' expects exact format above.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Dict, Iterable

def increment_quantity(item: dict, quantity: int):
    """
    Increase an item's quantity in place.
    
    Parameters
    ----------
    item : dict
        Item to update (mutated in place). Must have an integer-like 'quantity'.
    quantity : int
        Amount to add (may be > 0, negatives are not validated here).
        
    Side Effects
    ------------
    Mutates 'item['quantity'].
    
    Complexity
    ----------
    O(1)
    """
    item['quantity'] += quantity
        
def remove_item(items, quantity, target):
    """
    Remove some or all of na item's quantity by name (case-insensitve).
    
    Behavior
    --------
    - Finds the *first* item whose 'name' matches 'target' (case-insensitive).
    - If current quantity > 'quantity', decrements and keeps the item.
    - Else (quantity <=  'quantity') removes the entire item from the list.
    
    Parameters
    ----------
    items : list[dict]
        Collection (mutated in place).
    quantity : int
        Amount to remove.
    target : str
        Name to match (case-insensitve, first match wins).
        
    Returns
    -------
    bool
        True if an item was decremented or removed, False if not found.
        
    Complexity
    ----------
    O(n) over 'items'.
    
    Caveats
    -------
    - Only affects the first matching item, duplicates by name are possible
    - No validation for negative 'quantity'
    """
    for item in items:
        if item['name'].lower() == target.lower():
            if item['quantity'] > quantity:
                item['quantity'] -= quantity
                return True
            else:
                items.remove(item)
                return True
    return False

def filter_by_category(items, category):
    """
    Return items matching a category (case-insensitive).
    
    Parameters
    ----------
    items : list[dict]
    category : str
        Category to match, if fase (e.g., ""), returns 'items' unchanged.
        
    Returns
    -------
    list[dict]
    
    Complexity
    ----------
    O(n)
    """
    if not category:
        return items
    return [item for item in items if item["category"].lower() == category.lower()]

def search_by_keyword(items, keyword):
    """
    Case-insensitive substring search on item names.
    
    Parameters
    ----------
    items : list[dict]
    keyword : str
    
    Returns
    --------
    list[dict]
        Items whose lowercased 'name' contains the lowercased 'keyword'.
        
    Complexity
    ----------
    O(n * m) where m is average name length.
    
    Note
    ----
    An empty keyword ("") with match *all* items because "" in name is True.
    That can be convenient but is worth remembering
    """
    keyword = keyword.lower()
    results = []
    for item in items:
        name = item['name'].lower()
        if keyword in name:
            results.append(item)
    return results

def create_new_item(name: str, items: list, category: str, quantity: int):
    """
    Create a new item and append it to the provided list.

    Parameters
    ----------
    name : str
    items : list[dict]
        Target collection (mutated in place).
    category : str
    quantity : int
    
    Returns
    -------
    dict
        The newly created item
        
    Side Effects
    ------------
    Appends to 'items'. Generates":
        -id: UUIDv4 string
        - time: current timestamp in "%Y-%m-%d %H:%M:%S"
        
    Complexity
    ----------
    O(1)
    
    Note
    -----
    This function does not check for duplicates. Callers that want de-duplication
    should search and increment instead of creating. Allows multiple additions of the same
    items but needs something to help differentiate them to the user. 
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = {"id": str(uuid.uuid4()),
                 "name": name,
                 "category": category,
                 "quantity": quantity,
                 "time": timestamp
            }
    items.append(item)
    return item
    
def get_category_distribution(items):
    """
    Aggregate quantities by category.

    Parameters
    ----------
    items iterable[dict]
    
    Returns
    -------
    dict[str, int]
        Mapping of category -> total quantity.
        
    Complexity
    ----------
    O(n)
    """
    dist = {}
    for item in items:
        category = item['category']
        quantity = item.get("quantity", 1)
        dist[category] = dist.get(category, 0) + quantity
    return dist

def get_time_distribution(items, fmt="%Y-%m"):
    """
    Aggregate quantities by time period.
    
    Parameters
    ----------
    items : iterable[dict]
    fmt : str, default "%Y-%m"
        Target bucketing format. The function first parses 'item["time"]'
        using "%Y-%m-%d %H:%M:%S, then formats into 'fmt' (e.g., month buckets).
        
    Returns
    -------
    dict[str, int]
        Mapping of period (as formatted stirng) -> total quantity.
        
    Complexity
    -----------
    O(n)
    
    Raises
    ------
    ValueError
        If an item's 'time' value does not match the expected input format.
        
    Example
    -------
    If items have times across 2025-06 and 2025-07, using the default 'fmt' returns
    something like: {"2025-06": 5, "2025-07": 1}
    """
    dist = {}
    for item in items:
        timestamp = datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S")
        period = timestamp.strftime(fmt)
        dist[period] = dist.get(period, 0) + item.get("quantity", 1)
    return dist