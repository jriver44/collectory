import pytest
from datetime import datetime
import api.services as services

def test_get_item_by_id_found(monkeypatch):
    sample = [{"id": 1, "name": "Alpha"}]
    monkeypatch.setattr(services, "load_items", lambda path: sample)
    result = services.get_item_by_id(1)
    assert result is sample[0]
    
def test_get_item_by_id_not_found(monkeypatch):
    sample = [{"id": 2, "name": "Beta"}]
    monkeypatch.setattr(services, "load_items", lambda path: sample)
    result = services.get_item_by_id(1)
    assert result is None
    
def test_create_item_invokes_create_new_item(monkeypatch):
    items = []
    monkeypatch.setattr(services, "load_items", lambda path: items)
    captured = {}
    def fake_create(name, lst, category, qty, ts):
        captured.update({
            "name": name,
            "lst": lst,
            "category": category,
            "qty": qty,
            "ts": ts
        })
        return {"id": 99}
    monkeypatch.setattr(services, "create_new_item", fake_create)
    out = services.create_item("ItemX", "CatY", 7)
    
    assert out == {"id": 99}
    
    assert captured["name"] == "ItemX"
    assert captured["lst"] is items
    assert captured["category"] == "CatY"
    assert captured["qty"] == 7
    assert isinstance(captured["ts"], str)
    datetime.strptime(captured["ts"], "%Y-%m-%d %H:%M:%S")
    
def test_search_items_forwards_to_analysis(monkeypatch):
    sample_items = [{"id": 1}, {"id":2}]
    monkeypatch.setattr(services, "load_items", lambda path: sample_items)
    monkeypatch.setattr(services, "search_by_keyword", lambda items, kw: ["RESULT", items, kw])
    out = services.search_items("foo")
    assert out == ["RESULT", sample_items, "foo"]
    
def test_filter_items_forwards_to_analysis(monkeypatch):
    sample_items = [{"id":3}]
    monkeypatch.setattr(services, "load_items", lambda path: sample_items)
    monkeypatch.setattr(services, "filter_by_category", lambda items, cat: ["F", items, cat])
    out = services.filter_items("bar")
    assert out == ["F", sample_items, "bar"]
    
def test_category_distribution_transforms_counts(monkeypatch):
    raw = {"A": 5, "B": 2}
    monkeypatch.setattr(services, "load_items", lambda path: None)
    monkeypatch.setattr(services, "get_category_distribution", lambda items: raw)
    out = services.category_distribution()
    
    assert isinstance(out, list)
    assert {"category": "A", "count": 5} in out
    assert {"category": "B", "count": 2} in out
    
def test_time_distribution_transforms_counts(monkeypatch):
    raw = {"2025-07": 10}
    monkeypatch.setattr(services, "load_items", lambda path: None)
    monkeypatch.setattr(services, "get_time_distribution", lambda items: raw)
    out = services.time_distribution()
    assert out == [{"period": "2025-07", "count": 10}]