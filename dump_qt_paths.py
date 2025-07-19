import os, sys
from PySide6 import __file__ as pyside_file
from PySide6.QtCore import QCoreApplication

print("PySide6 module path: ", pyside_file)
print("QT_PLUGIN_PATH: ", os.environ.get("QT_PLUGIN_PATH"))
print("QT_QPA_PLATFORM_PLUGIN_PATH: ", os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"))
print()

app = QCoreApplication(sys.argv)
print("QCoreApplication.libraryPaths():")
for p in QCoreApplication.libraryPaths():
    print(" ->", p)