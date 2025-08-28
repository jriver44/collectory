# conftest.py
import os, importlib.util, pytest

# 1) Headless platform for tests (do this before importing PySide6)
os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

# 2) Locate PySide6's plugin directories without importing it yet
spec = importlib.util.find_spec("PySide6")
if not spec or not spec.submodule_search_locations:
    raise RuntimeError("PySide6 not found in current venv")
pyside_dir = spec.submodule_search_locations[0]
plugin_dir = os.path.join(pyside_dir, "Qt", "plugins")
platforms_dir = os.path.join(plugin_dir, "platforms")

# 3) Provide plugin hints to Qt (env vars are read very early)
os.environ.setdefault("QT_PLUGIN_PATH", plugin_dir)
os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", platforms_dir)

# 4) Now import Qt and non-destructively add library paths
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox
for p in (plugin_dir, platforms_dir):
    if p and p not in QCoreApplication.libraryPaths():
        QCoreApplication.addLibraryPath(p)

# IMPORTANT: don't force-create a QApplication for every test session.
# Let pytest-qt create it only when a test asks for qapp/qtbot.

@pytest.fixture(autouse=True)
def patch_question(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)