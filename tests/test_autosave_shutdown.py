import json
import threading
import time

def _wait_until(predicate, timeout=1.5, interval=0.01):
    """Poll until predicate() is True or timeout elapses."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False

def test_autosave_writes_and_stops(monkeypatch, tmp_path):
    """
    Acceptance:
        - autosave writes at least once
        - after request_shutdown(), no further writes occur
    """
    from collectory import collector
    
    # ensure clean loop
    if hasattr(collector, "_stop_event"):
        collector._stop_event.clear()
    
    # Patch config so writes go to a temp dir and tick quickly
    monkeypatch.setattr(collector, "config", type("C", (), {
        "DATA_DIR": tmp_path,
        "AUTOSAVE_ENABLED": True,
        "AUTOSAVE_INTERVAL": 0.05,
        "BACKUP_SUFFIX": "_bak",
        "MAX_BACKUPS": 3,
    }))
    
    file_name = "test_collection"
    base = tmp_path / f"{file_name}.json"
    calls = {"n": 0}
    
    # spy: replace save_items so the test doesn't depend on real rotation logic
    def fake_save(fn, items):
        calls["n"] += 1
        base.parent.mkdir(parents=True, exist_ok=True)
        base.write_text(json.dumps(items), encoding="utf-8")
        return True
    
    monkeypatch.setattr(collector, "save_items", fake_save)
    
    items = [{"id": 1, "name": "A", "category": "X", "quantity": 1, "time": "2024-01-01 00:00:00"}]

    
    # Start autosave loop in a thread (same as the CLI does)
    t = threading.Thread(target=collector.autosave_loop, args=(file_name, items), daemon=True)
    t.start()
    
    # prove it runs at least twice
    assert _wait_until(lambda: calls["n"] >= 2), "autosave did not run twice"
    
    n_before = calls["n"]
    collector.request_shutdown()
    t.join(timeout=1.0)
    assert not t.is_alive(), "autosave thread failed to stop"
    
    # ensure no more calls after shutdown
    time.sleep(0.12)
    assert calls["n"] == n_before, "autosave kept running after shutdown"
    
    # sanity check: file exists and JSON is valid
    assert base.exists()
    data = json.loads(base.read_text("utf-8"))
    assert isinstance(data, list) and data[0]["id"] == 1