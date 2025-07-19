import os, sys,PySide6
from PySide6.QtCore import QCoreApplication
_VENV_PLUGINS = os.path.join(os.path.dirname(PySide6.__file__),
                             "Qt", "plugins")
paths = [os.getenv("QT_PLUGIN_PATH"),
         
         _VENV_PLUGINS]
QCoreApplication.setLibraryPaths([p for p in paths if p])

import api.services as services
import csv
from PySide6.QtCore import Slot
API_BASE = "http://localhost:5000"

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QTableView, 
    QStatusBar, QVBoxLayout, QWidget, QDialog, QMenu,
    QMessageBox, QFileDialog
)

from gui.add_item_dialog import AddItemDialog

from datetime import datetime
from collectory.collector import create_new_item

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Curation")
        self.resize(800, 600)
        
        self._items: list[dict] = []
        
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        file_menu = QMenu("File", self)
        file_menu.addAction("Export to CSV", self.on_export)
        file_menu.addAction("Import from CSV", self.on_import)
        toolbar.addAction(file_menu.menuAction())
        
        add_act = QAction("Add Item", self)
        add_act.setStatusTip("Create a new item")
        add_act.triggered.connect(self.on_add_item)
        toolbar.addAction(add_act)
        
        refresh_act = QAction("Refresh", self)
        refresh_act.setStatusTip("Reload items from API")
        refresh_act.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_act)
        self.refresh_button = toolbar.widgetForAction(refresh_act)
        
        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ["ID", "Name", "Category", "Quantity", "Timestamp"]
        )
        
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")
        
    def on_file(self):
        self.statusBar().showMessage("File... clicked")
        
    def on_add_item(self):
        dlg = AddItemDialog(self)
        if dlg.exec() == QDialog.Accepted:
            items_list = self._items
            data = dlg.data()
            create_new_item(
                name=data["name"],
                items=items_list,
                category=data["category"],
                quantity=data["quantity"],
            )
            self._items = items_list
            self._populate_table(self._items)
            self.statusBar().showMessage(f"Added: {data['name']}")
        
    @Slot()
    def on_refresh(self):
        self.statusBar().showMessage("Refreshing...")
        self.setEnabled(False)
        
        try:
            items = services.get_all_items()
            self._items = items
            self._populate_table(items)
            self.statusBar().showMessage(f"Loaded {len(items)} items")
        except Exception as e:
            self.statusBar().showMessage(f"Refresh failed: {e}")
        finally:
            self.setEnabled(True)
            
    def _populate_table(self, items: list[dict]):
        self.model.removeRows(0, self.model.rowCount())
        for row_index, item in enumerate(items):
            values = [
                str(item["id"]),
                    item["name"],
                    item["category"],
                    str(item["quantity"]),
                    item["time"],
            ]
            for column_index, text in enumerate(values):
                cell = QStandardItem(text)
                self.model.setItem(row_index, column_index, cell)
                
    def on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Items from CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                imported_count = 0
                
                for row in reader:
                    create_new_item(
                        name=row.get("Name", "").strip(),
                        items=self._items,
                        category=row.get("Category", "").strip(),
                        quantity=int(row.get("Quantity", 0)),
                    )
                    imported_count += 1
                    
                self._populate_table(self._items)
                self.statusBar().showMessage(f"Imported {imported_count} items from {path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Could not read CSV:\n{e}")
            self.statusBar().showMessage("Import failed")
    
    def on_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Items to CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        
        try:
            items = self._items if self._items else services.get_all_items()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Category", "Quantity", "Timestamp"])
                for item in items:
                    writer.writerow([
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("category", ""),
                        item.get("quantity", ""),
                        item.get("time", ""),
                    ])   
            self.statusBar().showMessage(f"Exported {len(items)} items to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not write CSV:\n{e}")
            self.statusBar().showMessage("Export failed")
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())