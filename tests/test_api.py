import pytest
from api.server import app

import api.services as services

@pytest.fixture
def client():
    return app.test_client()

def graphql_request(client, query):
    return client.post("/graphql", json={"query": query})

def test_get_item_api(client, monkeypatch):
    SAMPLE = [{
        "id": 1, "name": "Test Item",
        "category": "Demo", "quantity": 3,
        "time": "2025-01-01T00:00:00"
    }]
    
    monkeypatch.setattr(
        services, "get_item_by_id",
        lambda item_id: SAMPLE[0] if item_id == 1 else None
    )
    
    query = '{ getItem(id:"1"){ name quantity } }'
    resp = graphql_request(client, query)
    data = resp.get_json()
    assert "errors" not in data
    assert data["data"]["getItem"]["name"] == SAMPLE[0]["name"]
    
def test_error_on_bad_query(client):
    resp = graphql_request(client, " { badField }")
    data = resp.get_json()
    assert "errors" in data
    assert resp.status_code == 400