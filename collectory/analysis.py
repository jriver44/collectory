import uuid
from datetime import datetime

def increment_quantity(item: dict, quantity: int):
    item['quantity'] += quantity
        
def remove_item(items, quantity, target):
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
    if not category:
        return items
    return [item for item in items if item["category"].lower() == category.lower()]

def search_by_keyword(items, keyword):
    keyword = keyword.lower()
    results = []
    for item in items:
        name = item['name'].lower()
        if keyword in name:
            results.append(item)
    return results

def create_new_item(name, items, category, quantity, timestamp):
    items.append({"id": str(uuid.uuid4()),
                 "name": name,
                 "category": category,
                 "quantity": quantity,
                 "time": timestamp
                 })
    
def get_category_distribution(items):
    dist = {}
    for item in items:
        category = item['category']
        quantity = item.get("quantity", 1)
        dist[category] = dist.get(category, 0) + quantity
    return dist

def get_time_distribution(items, fmt="%Y-%m"):
    dist = {}
    for item in items:
        timestamp = datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S")
        period = timestamp.strftime(fmt)
        dist[period] = dist.get(period, 0) + item.get("quantity", 1)
    return dist