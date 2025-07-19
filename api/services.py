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
    items = load_items(default_path())
    return next((item for item in items if item["id"] == item_id), None)

def create_item(name: str, category: str, quantity: int) -> dict:
    items = load_items(default_path())
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return create_new_item(name, items, category, quantity, ts)

def search_items(keyword: str) -> list[dict]:
    items = load_items(default_path())
    return search_by_keyword(items, keyword)

def filter_items(category: str) -> list[dict]:
    items = load_items(default_path())
    return filter_by_category(items, category)

def category_distribution() -> list[dict]:
    dist = get_category_distribution(load_items(default_path()))
    return [{"category": k, "count": v} for k, v in dist.items()]

def time_distribution() -> list[dict]:
    td = get_time_distribution(load_items(default_path()))
    return [{"period": k, "count": v} for k, v in td.items()]

def get_all_items() -> list[dict]:
    return load_items(default_path())
