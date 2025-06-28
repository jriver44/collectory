import unittest
from datetime import datetime
import uuid
from collectory.analysis import get_category_distribution, get_time_distribution

from collectory.analysis import (
    increment_quantity,
    create_new_item,
    remove_item,
    filter_by_category,
    search_by_keyword
)

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.items = []
        self.timestamp = "2025-06-26 10:00:00"
        
    def test_create_new_item(self):
        create_new_item("Padron", self.items, "cigar", 2, self.timestamp)
        self.assertEqual(len(self.items), 1)
        item = self.items[0]
        self.assertEqual(item['name'], 'Padron')
        self.assertEqual(item['category'], 'cigar')
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(item['time'], self.timestamp)
        
        uuid_obj = uuid.UUID(item['id'], version=4)
        self.assertEqual(str(uuid_obj), item['id'])
        
    def test_increment_quantity(self):
        entry = {'id': 'dummy-id', 'name': 'Padron', 'category': 'cigar', 'quantity': 5, 'time': self.timestamp}
        increment_quantity(entry, 3)
        self.assertEqual(entry['quantity'], 8)
        
    def test_remove_item_decrement(self):
        create_new_item("A", self.items, "book", 5, self.timestamp)
        result = remove_item(self.items, 2, "A")
        self.assertTrue(result)
        self.assertEqual(len(self.items), 1)
        self.assertEqual(self.items[0]['quantity'], 3)
        
    def test_remove_item_entire(self):
        create_new_item("B", self.items, "books", 2, self.timestamp)
        result = remove_item(self.items, 2, "B")
        self.assertTrue(result)
        self.assertEqual(self.items, [])
        
    def test_remove_item_not_found(self):
        result = remove_item(self.items, 1, "C")
        self.assertFalse(result)
        
    def test_filter_by_category(self):
        
        create_new_item("A", self.items, "book", 1, self.timestamp)
        create_new_item("B", self.items, "cigar", 1, self.timestamp)
        result = filter_by_category(self.items, "book")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'A')
        all_items = filter_by_category(self.items, "")
        self.assertCountEqual(all_items, self.items)
        
    def test_search_by_keyword(self):
        create_new_item("Alpha", self.items, "misc", 1, self.timestamp)
        create_new_item("Beta", self.items, "misc", 1, self.timestamp)
        create_new_item("alphabet soup", self.items, "food", 1, self.timestamp)
        result = search_by_keyword(self.items, "alph")
        names = [i['name'] for i in result]
        self.assertCountEqual(names, ["Alpha", "alphabet soup"])
        
    def test_get_category_distribution(self):
        items =[
            {"category":"cigar", "quantity":2},
            {"category": "book", "quantity":1},
            {"category":"cigar", "quantity": 3}
            ]
        expected = {"cigar":5, "book":1}
        self.assertEqual(get_category_distribution(items), expected)
    
    def test_get_time_distribution(self):
        items = [
        {"time":"2025-06-01 09:00:00","quantity":2},
        {"time":"2025-06-15 10:00:00","quantity":3},
        {"time":"2025-07-01 11:00:00","quantity":1},
        ]
        expected = {"2025-06":5, "2025-07":1}
        self.assertEqual(get_time_distribution(items), expected)
        
if __name__ == "__main__":
    unittest.main()
