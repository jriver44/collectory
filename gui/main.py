import os
import sys
import PySide6
from PySide6.QtCore import QCoreApplication

pyside_dir = os.path.dirname(PySide6.__file__)
plugin_dir = os.path.join(pyside_dir, "Qt", "plugins")
platforms_dir = os.path.join(plugin_dir, "platforms")

os.environ.setdefault("QT_PLUGIN_PATH", plugin_dir)
os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", platforms_dir)
QCoreApplication.setLibraryPaths([plugin_dir])

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()