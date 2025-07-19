import csv, io, pytest
from PySide6.QtWidgets import QFileDialog
from gui.main_window import MainWindow

def test_import_csv(tmp_path, qtbot, monkeypatch):
    csv_content = io.StringIO()
    writer = csv.writer(csv_content)
    
    writer.writerow(["ID", "Name", "Category", "Quantity", "Timestamp"])
    writer.writerow(["", "TestItem", "TestCat", "7", ""])
    
    path = tmp_path /  "in.csv"
    path.write_text(csv_content.getvalue(), encoding="utf-8")
    
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwsargs: (str(path), "CSV Files (*.csv)")

    )
    
    calls = []
    import gui.main_window as mw
    def fake_create_new_item(**data):
        calls.append({
            "name": data["name"],
            "category": data["category"],
            "quantity": data["quantity"],
        })
    monkeypatch.setattr(mw, "create_new_item", fake_create_new_item)
    
    import api.services as services
    monkeypatch.setattr(services, "get_all_items", lambda: [])
    
    win = MainWindow()
    qtbot.addWidget(win)
    win.on_import()
    
    assert len(calls) == 1
    assert calls[0] == {
        "name": "TestItem",
        "category": "TestCat",
        "quantity": 7,
    }