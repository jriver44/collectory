from __future__ import annotations

"""
Curation GUI main window (PySide6).

Responsibilities
----------------
    - Present a table view of items (ID/Name/Category/Quantity/Timestamp).
    - Provide toolbar actions: Open/Save JSON, Import/Export CSV, Add Item, Refresh (API).
    - Surface lightweight filtering (category dropdown + keyword search).
    - Orchestrate in-memory '_items' and keep the table model in sync.
    
Relationships
-------------
Depends on:
    - 'api.services' (optional online source via 'get_all_items()').
    - 'gui.add_item_dialog.AddItemDialog' (modal item creation).
    - Domain helper 'collectory.collector.create_new_item (pure create).
    
Persistence boundry
-------------------
    - JSON Open/Save and CSV Import/Export occur here via standard dialogs.
    - API reads via 'services.get_all_items()' (if available).
    - no background threads, all operations run on the GUI thread.
    
Thread/UI
    - All slots and UI updates must run on the Qt GUI thread.
    - Long-running I/O is synchronous here (OK for small collections, consider moving
    to a worker with signals/slots if needed).
    
Data model expectation
----------------------
Each item is a dict with keys:
    id: String (UUID or similar)
    name: String
    category: String
    quantity: int
    time: String ("%Y-%m-%d %H:%M:%S")
"""

import sys
import api.services as services
import csv
from PySide6.QtCore import Slot
API_BASE = "http://localhost:5000"

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QTableView, 
    QStatusBar, QVBoxLayout, QWidget, QDialog, QMenu,
    QMessageBox, QFileDialog, QLineEdit, QComboBox
)

from gui.add_item_dialog import AddItemDialog

from datetime import datetime
from collectory.collector import create_new_item # domain creation helper

import json
from pathlib import Path

class MainWindow(QMainWindow):
    """Primary application window hosting the item table and toolbar.
    
    UI Composition
    ---------------
        - QToolBar with File menu, Add Item, search box, category combo, Refresh action.
        - QTableView backed by QStandardItemModel (5 columns).
        - QStatusBar for ephemeral feedback.
        
    State
    ------
        - '_items': list[dict] representing the current in-memory collection.
        The table is (re)populated from this source.
        
    Invariants
    ----------
        - Table headers are fixed: ["ID", "Name", "Category", "Quantity", "Timestamp"].
        - '_populate_table' replaces all rows to reflect '_items' or a filtered view. 
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Curation")
        self.resize(800, 600)
        
        # Backing store for the current sessions data
        self._items: list[dict] = []
        
        # -- Toolbar and File menu -------------------------------------------------------
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        file_menu = QMenu("File", self)
        
        file_menu.addSeparator()
        file_menu.addAction("Open", self.on_open)
        file_menu.addAction("Save", self.on_save)
        
        file_menu.addAction("Export to CSV", self.on_export)
        file_menu.addAction("Import from CSV", self.on_import)
        toolbar.addAction(file_menu.menuAction())
        
        # Add item action (opens menu dialog)
        add_act = QAction("Add Item", self)
        add_act.setStatusTip("Create a new item")
        add_act.triggered.connect(self.on_add_item)
        toolbar.addAction(add_act)
        
        # Inline keyword search (case-insensitive substring on name)
        self.search_edit = QLineEdit(self)
        self.search_edit.setPlaceholderText("Search...")
        toolbar.addWidget(self.search_edit)
        
        # Category filter (populated on refresh/open/import)
        self.category_combo = QComboBox(self)
        self.category_combo.addItem("All")
        toolbar.addWidget(self.category_combo)
        
        # Filter triggers: any change re-applies filters against '_items'
        self.search_edit.textChanged.connect(self.apply_filters)
        self.category_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Refresh from API (optional online path)
        refresh_act = QAction("Refresh", self)
        refresh_act.setStatusTip("Reload items from API")
        refresh_act.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_act)
        self.refresh_button = toolbar.widgetForAction(refresh_act)
        
        # -- Table model/view ---------------------------------------------------------------
        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ["ID", "Name", "Category", "Quantity", "Timestamp"]
        )
        
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setEditTriggers(QTableView.NoEditTriggers)
        
        # Central widget and layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Status bar for feedback
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")
        
    def on_file(self):
        """Placeholder for future File menu handling (unused)"""
        self.statusBar().showMessage("File... clicked")
        
    def on_add_item(self):
        """Open the AddItemDialog and append the result to the table.
        
        Behavior:
            - If the dialog is accepted, create a new item via the domain helper.
            - '_items' remains the canonical store, and the table will repopulate.
            
        Side Effects:
            - Shows a model dialog.
            - Updates '_items' and the model on success.
        """
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
            
            # Ensure view reflects the updated in-memory list.
            self._items = items_list
            self._populate_table(self._items)
            self.statusBar().showMessage(f"Added: {data['name']}")
        
    @Slot()
    def on_refresh(self):
        """Fetch items from the API and refresh the view.
        
        Behavior:
            - Disables the window while fetching (simple reentrancy guard)
            - Rebuilds the category combo from the refreshed items.
            
        Failure:
            - On exception, shows a status message and re-enables the window.
        """
        self.statusBar().showMessage("Refreshing...")
        self.setEnabled(False)
        
        try:
            items = services.get_all_items()
            self._items = items
            self._populate_table(items)
            
            # Rebuild category options based on current items
            categories = sorted({item["category"] for item in self._items})
            self.category_combo.clear()
            self.category_combo.addItem("All")
            self.category_combo.addItems(categories)
            
            self.statusBar().showMessage(f"Loaded {len(items)} items")
        except Exception as e:
            self.statusBar().showMessage(f"Refresh failed: {e}")
        finally:
            self.setEnabled(True)
            
    def _populate_table(self, items: list[dict]):
        """Replace the table contents with 'items'.
        
        Args:
            items: The list of item dicts to render (often filterd).
        """
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
                
    def on_open(self):
        """Open a JSON file and load items into the table.
        
        Behavior:
            - If user cancels, returns quietly.
            - On success, '_items' becomes the loaded list and categories are not auto-rebuilt here,
            user can refresh categories by hitting Refresh or re-open/import again (to keep behavior minimal).
            
        Failure:
            - Shows a critical message box and updates the status bar.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Collection",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._items = json.load(f)
            self._populate_table(self._items)
            self.statusBar().showMessage(f"Opened {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Open Failed", f"Could not load JSON:\n{e}")
            self.statusBar().showMessage("Open failed")
            
    def on_save(self):
        """Save current items to a JSON file chosen by the user.
        
        Failure:
            - Shows a critical message box and sets a status message.
            """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Collection",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._items, f, indent=2)
            self.statusBar().showMessage(f"Saved to {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not write JSON:\n{e}")
            self.statusBar().showMessage("Save Failed")
                
    def on_import(self):
        """Import items from a CSV file and append to the current collection.
        
        CSV schema (expected headers):
            - Name, Category, Quantity
        
        Behavior:
            - Calls the domain 'create_new_item' for each row.
            - Rebuilds the table when done, categories are not auto-rebuilt here.
            
        Failure:
            - Shows a critical message box and updates the status bar.
        """
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
        """Export itmems to a CSV chosen by the user.
        
        Behavior:
            - Uses in-memory '_items' if available, else fetches from the API.
            
        Failure:
            - Shows a critical message box and updates the status bar.
        """
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
            
    def apply_filters(self):
        """Apply category + keyword filters to '_items' and refresh the table.
        
        Filtering:
            - Category: exact, case-insensitive match unless "All" is selected. 
            - Keyword: case-insensitive substring match on 'name'.
        
        Side Effects:
            - Updates the status bar with 'showing/total' counts.    
        """
        text = self.search_edit.text().strip()
        cat = self.category_combo.currentText()
        
        results = list(self._items)
        
        if cat != "All":
            from collectory.analysis import filter_by_category
            results = filter_by_category(results, cat)
            
        if text:
            from collectory.analysis import search_by_keyword
            results = search_by_keyword(results, text)
            
        self._populate_table(results)
        
        self.statusBar().showMessage(
            f"Showing {len(results)} of {len(self._items)} items"
        )
        
        
if __name__ == "__main__":
    # Standard Qt application bootstrap
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())