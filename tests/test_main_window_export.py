import csv
from pathlib import Path
import pytest
from PySide6.QtWidgets import QFileDialog
from gui.main_window import MainWindow

def test_export_csv(tmp_path, qtbot, monkeypatch):
    sample = [
        {"id":"1", "name":"Foo", "category":"Bar", "quantity":5, "time":"2025-07-18 12:00:00"}
    ]
    import api.services as services
    monkeypatch.setattr(services, "get_all_items", lambda: sample)
    
    out_file = tmp_path / "export.csv"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(out_file), "CSV Files (*.csv)")
    )
    
    window = MainWindow()
    qtbot.addWidget(window)
    window.on_export()
    
    assert out_file.exists()
    with open(out_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    assert rows[0] == ["ID", "Name", "Category", "Quantity", "Timestamp"]
    assert rows[1] == ["1", "Foo", "Bar", "5", "2025-07-18 12:00:00"]