"""
    Curation API server (Flask + Ariadne GraphQL)
    
    Design notes
    -------------
    - Keep the web layer *thin*: all domain logic lives in 'api.services'.
    - Expose **two** surfaces:
       1) REST (via 'api.rest' blueprint) for straightforward CRUD calls.
       2) GraphQL (via Ariadne) for flexible querying from richer clients.
    - Resolvers are intentionally "pass-through" to 'services' to avoid logic drift.
    
    This file also wires up the built-in GraphiQL explorer at GET /graphql.
 """

import os, sys

# --- Local path bootstrap -----------------------------------------------------
# Make project imports work when running 'python api/server.py' directly.
from collectory.collector import load_items
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# --- Web / GraphQL deps -------------------------------------------------------
from flask import Flask, request, jsonify
from ariadne import (
    QueryType,
    MutationType,
    make_executable_schema,
    graphql_sync
)
from ariadne.explorer import ExplorerGraphiQL

# --- REST blueprint (mounted below) ------------------------------------------
from api.rest import rest

# --- Domain services (single source of truth) --------------------------------
import api.services as services

# ---------------------------- Thin service wrappers ---------------------------
# These wrappers exist to keep resolvers tiny and to make this module readable.
def get_item_by_id(item_id: int):
    """Return a single item dict or None from services."""
    return services.get_item_by_id(item_id)

def search_items(keyword: str):
    """Return list of items whose name contain 'keyword' (case-insensitive)."""
    return services.search_items(keyword)

def filter_items(category: str):
    """Return list of items whose category matches exactly (case-insensitive)."""
    return services.filter_items(category)

def category_distribution():
    """Return mapping {category: quantity}."""
    return services.category_distribution()

def time_distribution():
    """Return mapping {period: quantity}, e.g. {'2025-07': 3}."""
    return services.time_distribution()

def create_item(name: str, category: str, quantity: int):
    """Create and return a new item dict (delegates to services)."""
    return services.create_item(name, category, quantity)

# ---------------------------- GraphQL schema (SDL) ----------------------------
# Kept minimal and explicit on purpose. When the domain grows we consider splitting
# SDL into its own module/file and generating an OpenAPI/SDL artifact.
type_defs = """
    type Item {
        id: ID!
        name: String!
        category: String!
        quantity: Int!
        time: String!
    }
    
    type Query {
        getItem(id: ID!): Item
        searchItems(keyword: String!): [Item!]!
        filterItems(category: String!): [Item!]!
        categoryDistribution: [ CategoryCount!]!
        timeDistribution: [TimeCount!]!
    }
    
    type Mutation {
        createItem(name: String!, category: String!, quantity: Int!): Item
    }
    
    type CategoryCount {
        category: String!,
        count: Int!
    }
    
    type TimeCount {
        period: String!,
        count: Int!
    }
"""

# ---------------------------- Resolvers ---------------------------------------
# Resolvers are thin pass throughs to the wrappers above. This keeps responsibilities
# obvious and makes it trivial to test the domain separately.
query = QueryType()
mutation = MutationType()

@query.field("getItem")
def resolve_get_item(_, info, id):
    """Fetch a single item by ID (ID is string in GraphQL, then cast to int)."""
    return get_item_by_id(int(id))

@query.field("searchItems")
def resolve_search_items(_, info, keyword):
    """Substring search on item name"""
    return search_items(keyword)

@query.field("filterItems")
def resolve_filter_items(_, info, category):
    """Exact (case-insensitve) category filter."""
    return filter_items(category)

@query.field("categoryDistribution")
def resolve_category_distribution(_, info):
    """Aggregate: quantity per category."""
    return category_distribution()

@query.field("timeDistribution")
def resolve_time_distribution(_, info):
    """Aggregate: quantity per time period (e.g., 'YYYY-MM')."""
    return time_distribution()

@mutation.field("createItem")
def resolve_create_item(_, info, name, category, quantity):
    """Create a new item"""
    return create_item(name, category, quantity)

# Build executable schema once at import time.
schema = make_executable_schema(type_defs, query, mutation)

# ---------------------------- Flask app wiring --------------------------------
app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    """Serve GraphiQL explorer for manual testing/development."""
    html = ExplorerGraphiQL(title="Curation GraphQL").html(None)
    return html, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    """Handle GraphQL POSTs from clients.

        Expects JSON payload shaped like:
            { "query": "...", "variables": { ... } }
    """
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug,
    )
    status = 200 if success else 400
    return jsonify(result), status

# Mount REST routes alongside GraphQL
app.register_blueprint(rest)

# Dev server
if __name__ == "__main__":
    app.run(debug=True, port=5000)