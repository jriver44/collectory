# Curation

Curation is an inventory/collection management application with both a **command-line API** and a **desktop GUI**.
It allows you to create, organize, import/export, and search collections of items.

The project is modular:
- **`collecotry/`** -> Core business logic, analysis, and configuration.
- **'api/'** -> REST API services for managing items programmatically.
- **'gui/'** -> PySide6-based graphical interface (optional, see [GUI README](gui/README_GUI.md)).

---

## Features

- Persistent JSON-based collections with autosave and backups.
- API endpoints for CRUD operations.
- Filtering and search utilities.
- Optional GUI for interactive management.
- CSV import/export for interoperability.

---

## Installation

Clone the repo and install dependencies:

```bash
git clone git@github.com:jriver44/collecttory.git
cd collectory
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Collectory Modules

1. collectory/config.py
    - Defines the storage directory (~/.collectory) and ensures it exists/writable.
    - Constants for autosave, backup suffixes, and maximum backups.
    - Function collection_path(name) to resolve paths for collection files.

2. collectory/collector.py
    - Core functions for creating and updating colleciton items.
    - Manages unique IDs, timestamps, and insertion into the collection list.
    - Supports integration with GUI and API layers

3. collectory/analysis.py
    - Provides **search** and **filtering** functions:
        1. filter_by_category(items, category)
        2. search_by_keyword(items, query)
    - Use by GUI filters and API queries.

## API Services

1. api/services.py
    - Provides wrapper functions for interacting with items.
    - Connects frontend and storage logic.

2. api/rest.py and api/server.py
    - Flast/FastAPI-based server exposing REST endpoints.
    - Supports GET (list items), POST (create), PUT (update), and DELETE.

## GUI Overview

The GUI is built with **PySide6** and provides:
    - Toolbar with file operations, filters, and search.
    - Table view for browsing items.
    - Add/Edit dialogs for item management

-> -> -> **See GUI README.md for details**

## Running the API

Start the REST server (from repo root):
    ```bash
    python -m api.server
    ```

## Running the GUI