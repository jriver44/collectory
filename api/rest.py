""" REST endpoints for Collectory API. 

This blueprint exposes a small, focused REST surface area around items
and lightweight analytics. It intentionally keeps business logic in 'api.services'
so the web layer stays thin and easy to test.

ROUTES
-----
GET /items/<int:item_id>        -> fetch a single item by id
GET /items                      -> list all items
POST /items                     -> create a new item (JSON body)
GET /items/search?keyword=...   -> search items by keyword (name)
GET /items/filter?category=...  -> filter items by exact category (case-insensitive)
GET /analytics/category         -> counts by category
GET /analytics/time             -> counts by time period
"""

from __future__ import annotations

from flask import Blueprint, request, jsonify
import api.services as services

rest = Blueprint("rest", __name__)

@rest.route("/items/<int:item_id>", methods=["GET"])
def get_item_rest(item_id):
    """Return a single item by ID.
    
    Args:
        item_id: Integer identifier of the item.
        
    Returns:
        200 + JSON item dict if found, else 404 + {"error": "Not found"}. 
    """
    item = services.get_item_by_id(item_id)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Not found"}), 404

@rest.route("/items", methods=["GET"])
def list_items_rest():
    """Return all items.

    Returns:
        200 + JSON array of items (possibly empty)
    """
    items = services.get_all_items()
    return jsonify(items), 200

@rest.route("/items", methods=["POST"])
def create_item_rest():
    """Create a new item:
    
    Expects JSON body with:
       - name: str
       - category: str
       - quantity: int

    Returns:
        201 | created item JSON.
        
    Notes:
        Validation is intentionally minimal here to keep the example concise.
        In production, we would layer in a schema and return 400 on invalid input
    """
    data = request.get_json() or {}
    new = services.create_item(
        data.get("name", ""),
        data.get("category", ""),
        data.get("quantity", 0),
    )
    return jsonify(new), 201

@rest.route("/items/search", methods=["GET"])
def search_items_rest():
    """Search items by keyword in the name field.
    
       Query Params:
            keyword: Substring match (case-insensitive).
            
        Returns:
            200 + JSON array of matching items.
    """
    keyword = request.args.get("keyword", "")
    return jsonify(services.search_items(keyword)), 200

@rest.route("/items/filter", methods=["GET"])
def filter_items_rest():
    """Filter items by category (case-insensitive exact match).
    
       Query Params:
            category: Target category name.

    Returns:
        200 + JSON array of filtered items.
    """
    category = request.args.get("category", "")
    return jsonify(services.filter_items(category)), 200

@rest.route("/analytics/category", methods=["GET"])
def category_dist_rest():
    """Aggregate: quantity per category.
    
        Returns:
            200 + JSON object mapping category -> quantity.
    """
    return jsonify(services.category_distribution()), 200

@rest.route("/analytics/time", methods=["GET"])
def time_dist_rest():
    """Aggregate: quantity per time period.

    Returns:
        200 + JSON object mapping period -> quantity.
    """
    return jsonify(services.time_distribution()), 200