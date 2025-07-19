import os
import sys
import PySide6
import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QMessageBox

os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

if sys.platform == "darwin":
    pyside_dir = os.path.dirname(PySide6.__file__)
    qt_lib_dir = os.path.join(pyside_dir, "Qt", "lib")
    os.environ.setdefault("DYLD_FRAMEWORK_PATH", qt_lib_dir)
    os.environ.setdefault("DYLD_LIBRARY_PATH", qt_lib_dir)
    
pyside_dir = os.path.dirname(PySide6.__file__)
plugin_dir = os.path.join(pyside_dir, "Qt", "plugins")
os.environ.setdefault("QT_PLUGIN_PATH", plugin_dir)
os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", os.path.join(plugin_dir, "platforms"))
QCoreApplication.setLibraryPaths([plugin_dir])

@pytest.fixture(scope="session", autouse=True)
def qapp_session():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

@pytest.fixture(autouse=True)
def patch_question(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)