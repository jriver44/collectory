import pytest
from api.server import app

@pytest.fixture
def client():
    return app.test_client()

def test_get_item_not_found(client, monkeypatch):
    monkeypatch.setattr("api.services.get_item_by_id", lambda id: None)
    res = client.get("/items/1")
    assert res.status_code == 404
    assert res.get_json() == {"error": "Not found"}
    
def test_get_item_success(client, monkeypatch):
    SAMPLE = [{"id": 1, "name": "X", "category": "C", "quantity": 2, "time": "2025-01-01 00:00:00"}]
    monkeypatch.setattr("api.services.get_item_by_id", lambda id: SAMPLE if id == 1 else None)
    res = client.get("/items/1")
    assert res.status_code == 200
    assert res.get_json() == SAMPLE
    
def test_create_item_rest(client, monkeypatch):
    SAMPLE = {"id": 1, "name": "Y", "category": "D", "quantity": 4, "time": "TS"}
    monkeypatch.setattr("api.services.create_item", lambda n, c, q: SAMPLE)
    payload = {"name": "Y", "category": "D", "quantity": 4}
    res = client.post("/items", json=payload)
    assert res.status_code == 201
    assert res.get_json() == SAMPLE
    
@pytest.mark.parametrize("keyword,expected_ids", [
    ("Alpha", [1]),
    ("alpha", [1]),
    ("NoneMatch", []),
])

def test_search_items_rest(client, monkeypatch, keyword, expected_ids):
    SAMPLE = [
        {"id": 1, "name": "Alpha", "category": "A", "quantity": 1, "time": "2025-01-01 00:00:00"},
        {"id": 2, "name": "Beta", "category": "B", "quantity": 2, "time": "2025-01-02 00:00:00"},
    ]
    monkeypatch.setattr("api.services.search_items", lambda kw: [SAMPLE[0]] if kw.lower() == "alpha" else [])
    res = client.get(f"/items/search?keyword={keyword}")
    assert res.status_code == 200
    assert [item["id"] for item in res.get_json()] ==  expected_ids
    
def test_filter_items_rest(client, monkeypatch):
    SAMPLE = [{"id": 1, "name": "A", "category": "X", "quantity": 2, "time": "2025-01-01 00:00:00"}]
    monkeypatch.setattr("api.services.filter_items", lambda cat: SAMPLE if cat == "X" else [])
    res = client.get("/items/filter?category=X")
    assert res.status_code == 200
    assert res.get_json() == SAMPLE
    
def test_category_distribution_rest(client, monkeypatch):
    dist = [{"category": "X", "count": 7}, {"category": "Y", "count": 3}]
    monkeypatch.setattr("api.services.category_distribution", lambda: dist)
    res = client.get("/analytics/category")
    assert res.status_code == 200
    mapping = {d["category"]: d["count"] for d in res.get_json()}
    assert mapping == {"X": 7, "Y": 3}
    
def test_time_distribution_rest(client, monkeypatch):
    td = [{"period": "2025-01", "count": 5}]
    monkeypatch.setattr("api.services.time_distribution", lambda: td)
    res = client.get("/analytics/time")
    assert res.status_code == 200
    mapping = {d["period"]: d["count"] for d in res.get_json()}
    assert mapping == {"2025-01": 5}
    
def test_list_items_rest(client, monkeypatch):
    SAMPLE = [{"id":1, "name":"A", "category": "X", "quantity": 2, "time": "2025-01-01 00:00:00"},
              {"id": 2, "name": "B", "category": "Y", "quantity": 1, "time": "2025-02-01 01:00:00"}
              ]
    monkeypatch.setattr("api.services.get_all_items", lambda: SAMPLE)
    res = client.get("/items")
    assert res.status_code == 200
    assert res.get_json() == SAMPLE