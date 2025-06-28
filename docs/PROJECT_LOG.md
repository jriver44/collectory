Project Log 2025-06-20 (Phase 1 CLI & Basic Item Management)
    Tasks completed:
        1. Created project folder and ran git init.
        2. Added initial README.md with small goal statement.
        3. Implemented a CLI in collectory.py
            * Menu has options such as add item, list items, quit.
            * add_item() prompts for name and category, stores each item as a dictionary in the items list.
            * list_items() loops through items and prints numbered entries
    Key decisions:
        * Chose plain dictionaries over a dataclass for now to keep data handling simple.
        * Two miniman attributes per item: name and category
        * Kept in-memory storage only for now and will implement save files/loading files in future phase.
    
    Edge-case tests:
        Scenarios & Results:
            1. Listing before any items exists prints nothing.
            2. Invalid menu choice (e.g. "5") will prompt a fresh print of the menu.
            3. Adding two items then listing shows both items displayed correctly in order added.
    
    Commit History:
        1. Initial commit: README and empty collector.py
        2. Add CLI loop with menu skeleton
        3. Implemented add_item and list_items with dictionary storage

    Reflection/Future notes:
        * Input flow feels clear and numbering the list output helps readability
        * Might rename exit flag to running
        * Want a way to remove an item and save data to file so that the collection isn't lost upon exit.  -> Phase 2 target.
        * No blockers since a plain dictionary keeps learning curve lower.

ProjectLog 2025-06-21 (Phase 2 - Persistence and Item Management)
    Tasks completed:
        1. Added JSON file loading on startup (load_items).
        2. Added manual save to JSON with human-readable formatting (save_items).
        3. Implemented backup creation before every save (shutil.copyfile).
        4. Added timestamp field (datatime.now()) when an item is created.
        5. Added remove_item function.
        6. Added edit_category function.
        7. Improved list display (1-based numbering nad timestamp)
        8. Improved error handling: missing gile and JSON-decode failures fall back to empty lists.
    Key decisions:
        * Kept plain dictionaries with dataclass being postponed until refactor later. Keeping it simple for now.
        * JSON chosen for persistence over CSV or SQLite to stay human-readable.
        * Manual save (menu option) preferred to autosave for now. Old style, will need updating.
        * Added optional backup strategy to prevent data loss. 
        * Menu expanded to six options for added features.
    Edge-case tests:
        Scenario/Results:
            1. Start with no file -> program reports "No file found" and opens with an empty collection.
            2. Corrupted JSON -> program catches 'JSONDecodeError', starts fresh file, prints warning.
            3. Attempt to remove a non-existing item -> prints "not found" message, list unchanged.
            4. Attempt to save with empty collection -> prints "Nothing to save," file unchanged.
            5. Add three items, quit, relaunch -> all three items load and list correctly.
            6. Edit category -> new category persists after save and reload. 

    Commit history:
        1. Load/save scaffolding with try/except ('v0.2-alpha').
        2. Add timestamp on add_item.
        3. Add remove_item and edit_category commands.
        4. Implemented backup before saving and indented JSON with 2 ('v0.2.0')
        5. Error-handling polish and 1-based list numbering fixed ('v0.2.1').
    
    Reflection/Future notes:
        * Core CRUD and persistence feels stable, backup gives peace of mind. 
        * Next up is a small refactor that will move menu text to a constant, and split the helpers into seperate modules
        * Phase 3 target: summary stats (total count, per-category count, newest/oldest).
        * Stretch Phase 3+: search/filter command and basic table display.
        * Longer term: GUI or web front-end and AI data-enrichment module.

Project Log 2025-06-22 (Phase 3 Act 1 - Summary & Search/Filter)
    Tasks completed:
        1. Implemented 'show_summary()' in 'collector.py'
            * Total items count
            * Per-category totals via 'get_category_distribution()'
            * Oldest vs. newest timestamp via 'get_time_stamp_distribution()'
        2. Added 'filter_by_category()' and wired menu option "Filter"
        3. Added 'search_by_keyword()' and wired menu option "Search"
    Key Decisions:
        * Summary and search/filter live in the CLI core, not GUI
        * Pure-logic helpers in 'analysis.py' return dicts or lists for easy testing.
    Edge-case tests:
        1. Empty collection -> summary prints zero/none, filter/search return empty without crash.
        2. Case insensitive matching for both filter and search. 
    Commit history:
        * feat: added summary stats & filter/search commands (v0.3.0)
        * test: unit tests for distribution and keyword search.
    Reflection/Futrue Notes:
        * Next: offload backups to background (autosave thread + rotation)

Project Log 2025-06-23 (Phase 2 - Persistence & Backups)
    Tasks completed:
        1. Added daemon 'autosave_loop()' thread (configurable interval)
        2. Enhanced 'save_items()' to write timestamped backups ('_YYYYMMDDTHHMMSS_backup.json')
        3. Built 'rotate_backups()' to prune old backups down to 'MAX_BACKUPS'
    Key decisions:
        * Autosave runs in a daemon so it never blocks CLI input.
        * ISO-style timestamps for lexicographic sort.
        * Single pass prune logic in 'rotate_backups()
    Edge-case tests:
        1. Simulated 5 backups, 'keep=3' prunes exactly the 2 oldest.
        2. No errors when backups < 'keep'.
    Commit history:
        * feat: autosave thread & rotating backups (v0.3.1)
        * test: backup-rotation unit tests
    Reflection/Future notes:
        * Need atomic file writes or locks to avoid race conditions with threads

Project Log 025-06-24 (Phase 3 Act 3 - Table-Mode CLI)
    Tasks completed:
        1. Installed an imported 'tabulate'
        2. Replaced 'list_items()' with 'show_table()' rendering bordered ASCII grid.
        3. Updated menu to call 'show_table()' for "View items"
    Key decisions:
        * Use 'tablefmt="grid"' for clear visual separation.
        * Keep a single listing function for maintainability.
    Edge-case tests/manually verified:
        1. Empty collection -> "No items to display"
        2. Long names wrap/truncate cleanly.
    Commit history:
        * feat: add table-mode CLI view (v0.3.2)
    Reflection/Future notes:
        * Could allow user to switch formats (plain, GitHub) via config

Project Log 2025-06-25 (Phase 3 Act 4 & 5 - Analytics Helpers & CLI Polish)
    Tasks completed:
        1. Added 'get_time_distribution()' for time bucketed quantities
        2. Wrote & passed unit tests for both category and time distributions.
        3. Integrated 'colorama' for colored headers, prompts, success (green) & error (red) messages
        4. Consolidated all boolean feedback through 'confirm_action(ok, success, error)'
        5. Centralized menu rendering in 'display_menu()' with consistent styling.
    Key decisions:
        * Use 'autoreset=True' to avoid style bleed over.
        * Yellow prompts and cyan headers guide the user's eye.
    Edge-case tests/manually verified>
        1. Invalid inputs (non-numeric quantities, bad menu choices) show red errors, no crash.
        2. Success/failure branches all display correct color feedback.
    Commit history:
        * feat: add analytics helpers & CLI colorization (v0.3.3)
    Reflection/Future notes:
        * Next up: packaging ('setup.py'/'pyproject.toml'), CLI entry point, and full README (Act 6)