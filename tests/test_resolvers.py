import pytest
from unittest.mock import patch

from api.server import (
    resolve_get_item,
    resolve_search_items,
    resolve_filter_items,
    resolve_category_distribution,
    resolve_time_distribution,
)

SAMPLE_ITEM = {
    "id": 1,
    "name": "A",
    "category": "X",
    "quantity": 2,
    "time": "2025-01-01 00:00:00",
}

SAMPLE_LIST = [SAMPLE_ITEM]

@patch("api.server.get_item_by_id", return_value=SAMPLE_ITEM)
def test_get_item_type_coercion(mock_get):
    assert resolve_get_item(None, None, id="1")["name"] == "A"
    assert resolve_get_item(None, None, id=1)["name"] == "A"
    
@patch("api.server.search_items", return_value=SAMPLE_LIST)
def test_search_items(mock_search):
    assert resolve_search_items(None, None, keyword="anything") == SAMPLE_LIST
    
@patch("api.server.filter_items", return_value=SAMPLE_LIST)
def test_filter_items(mock_filter):
    assert resolve_filter_items(None, None, category="anything") == SAMPLE_LIST
    
@patch("api.services.category_distribution", return_value=[{"category": "X", "count": 2}])
def test_category_distribution(mock_cat):
    assert resolve_category_distribution(None, None) == [{"category": "X", "count": 2}]
    
@patch("api.services.time_distribution", return_value=[{"period": "2025-01", "count": 2}])
def test_time_distribution(mock_time):
    assert resolve_time_distribution(None, None) == [{"period": "2025-01", "count": 2}]