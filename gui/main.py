from __future__ import annotations

""" 
Curation GUI bootstrap and Qt plugin path setup.

Responsibilites
---------------
    - Configure Qt plugin search paths at runtime so PySide6 can locate platform
    plugins (e.g. 'platforms/libqcocoa', 'platforms/qwindows', 'platforms/libqxcb').
    - Create and run the QApplication, show the MainWindow, and exit with the app code.
    
Threading/UI
    - All GUI work occurs on the Qt GUI thread. This module should be imported and 
    executed from the main process only.
"""

import os
import sys
import PySide6
from PySide6.QtCore import QCoreApplication

# --- Qt plugin path configuration -------------------------------------------------------
# Compute PySide6's plugin directories, then set enviroment, variables so that Qt can discover
# platform plugins reliably.
pyside_dir = os.path.dirname(PySide6.__file__)
plugin_dir = os.path.join(pyside_dir, "Qt", "plugins")
platforms_dir = os.path.join(plugin_dir, "platforms")

# Set defaults only if not already provided by the enviroment/packager.
os.environ.setdefault("QT_PLUGIN_PATH", plugin_dir)
os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", platforms_dir)

# Also update Qt's internal library search paths at runtime
QCoreApplication.setLibraryPaths([plugin_dir])

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Create the QApplication, show the main window, and run the event loop."""
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()