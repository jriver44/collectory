from flask import Blueprint, request, jsonify
import api.services as services

rest = Blueprint("rest", __name__)

@rest.route("/items/<int:item_id>", methods=["GET"])
def get_item_rest(item_id):
    item = services.get_item_by_id(item_id)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Not found"}), 404

@rest.route("/items", methods=["GET"])
def list_items_rest():
    items = services.get_all_items()
    return jsonify(items), 200

@rest.route("/items", methods=["POST"])
def create_item_rest():
    data = request.get_json() or {}
    new = services.create_item(
        data.get("name", ""),
        data.get("category", ""),
        data.get("quantity", 0),
    )
    return jsonify(new), 201

@rest.route("/items/search", methods=["GET"])
def search_items_rest():
    keyword = request.args.get("keyword", "")
    return jsonify(services.search_items(keyword)), 200

@rest.route("/items/filter", methods=["GET"])
def filter_items_rest():
    category = request.args.get("category", "")
    return jsonify(services.filter_items(category)), 200

@rest.route("/analytics/category", methods=["GET"])
def category_dist_rest():
    return jsonify(services.category_distribution()), 200

@rest.route("/analytics/time", methods=["GET"])
def time_dist_rest():
    return jsonify(services.time_distribution()), 200