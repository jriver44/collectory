from gui.main_window import MainWindow
import api.services as services

def test_on_refresh_success(monkeypatch):
    SAMPLE = [{"id": 1, "name": "Y", "category": "X", "quantity": 5, "time": "T"}]
    monkeypatch.setattr(services, "get_all_items", lambda: SAMPLE)
    
    win = MainWindow()
    win.on_refresh()
    
    assert win.model.rowCount() == 1
    assert "Loaded 1 items" in win.statusBar().currentMessage()
    
def test_on_refresh_failure(monkeypatch):
    monkeypatch.setattr(services, "get_all_items", lambda: (_ for _ in ()).throw(Exception("network error")))
    
    win =  MainWindow()
    win.on_refresh()
    
    assert win.model.rowCount() == 0
    msg = win.statusBar().currentMessage()
    assert msg.startswith("Refresh failed:")
    assert "network error" in msg