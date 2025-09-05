# Curation GUI

The GUI for Curation is implemented with **PySide6** and provides an interactive way to manage collections.

---

## Features

- **Toolbar** with:
    - File operations (Open, Save, Import, Export).
    - Add Item dialog.
    - Category filter and search field.
    - Refresh button for reloading items from the API.
- **Table View**:
    - Displays items with columns: ID, Name, Category, Quantity, Timestamp.
    - Read-only rows, selectable by entire row.
- **Dialogs**:
    - `AddItemDialog`: add new items via form.
- **Import/Export**:
    - CSV import/export with schema: `ID, Name, Category, Quantity, Timestamp.

---

## Files

1. **`gui/main.py`**
    - Entrypoint for the GUI.
    - Configures Qt plugin paths for compatibility with PyInstaller.
    - Starts `QApplication` and shows the `MainWindow`.

2. **`gui/main_window.py`**
    - Defines `MainWindow` (the main application window).
    - Handles toolbar actions, search/filter logic, and file operations.
    - Integrates with `collectory` for creating items and `api/services` for refresh.

3. **`gui/add_item_dialog.py`**
    - Provides `AddItemDialog`, a model dialog for adding items.
    - Includes from fields for name, category, and quantity.

---

## Usage

Run the GUI:

```bash
python -m gui.main
```

## Example workflow:

1. Launch app.
2. Click **Add Item** to create a new entry.
3. Use **Search** and **Category Filter** To narrow results once enough items are in database to test.
4. Save JSON or export CSV.

## Future Improvements

- Edit and delete functionally for items.
- Batch import with validation.
- Enhanced UI/UX styling with Qt Designer.
- Dark mode toggle.
- Drag-and-drop CSV loading
- Settings panels

## Screenshots