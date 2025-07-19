import os, sys

from collectory.collector import load_items

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify
from ariadne import (
    QueryType,
    MutationType,
    make_executable_schema,
    graphql_sync
)
from ariadne.explorer import ExplorerGraphiQL

from api.rest import rest

import api.services as services

def get_item_by_id(item_id: int):
    return services.get_item_by_id(item_id)

def search_items(keyword: str):
    return services.search_items(keyword)

def filter_items(category: str):
    return services.filter_items(category)

def category_distribution():
    return services.category_distribution()

def time_distribution():
    return services.time_distribution()

def create_item(name: str, category: str, quantity: int):
    return services.create_item(name, category, quantity)

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

query = QueryType()
mutation = MutationType()

@query.field("getItem")
def resolve_get_item(_, info, id):
    return get_item_by_id(int(id))

@query.field("searchItems")
def resolve_search_items(_, info, keyword):
    return search_items(keyword)

@query.field("filterItems")
def resolve_filter_items(_, info, category):
    return filter_items(category)

@query.field("categoryDistribution")
def resolve_category_distribution(_, info):
    return category_distribution()

@query.field("timeDistribution")
def resolve_time_distribution(_, info):
    return time_distribution()

@mutation.field("createItem")
def resolve_create_item(_, info, name, category, quantity):
    return create_item(name, category, quantity)

schema = make_executable_schema(type_defs, query, mutation)
app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    html = ExplorerGraphiQL(title="Curation GraphQL").html(None)
    return html, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug,
    )
    status = 200 if success else 400
    return jsonify(result), status

app.register_blueprint(rest)

if __name__ == "__main__":
    app.run(debug=True, port=5000)