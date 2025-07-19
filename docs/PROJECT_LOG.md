# Project Log

## 2025-06-20 – Phase 1: Basic CLI
- Initialized repository & README.
- Built `collector.py` CLI with in-memory add/list/quit.
- Chose plain Python dicts for item storage.

## 2025-06-21 – Phase 2: Persistence & Item Management
- Added JSON load/save (`load_items`/`save_items`).
- Manual backups via `shutil.copyfile`.
- Implemented `remove_item`, `edit_category`, timestamp on add.
- Error handling for missing/corrupt JSON.

## 2025-06-22 – Phase 3 Act 1: Summary & Search
- `show_summary`, `search_by_keyword`, category filters.
- Wrote unit tests for summary and search.

## 2025-06-23 – Phase 3 Act 2: Autosave & Backups
- Autosave thread with rotating timestamped backups.
- Unit tests for autosave functionality.

## 2025-06-24 – Phase 3 Act 3: Table View
- Integrated `tabulate` for table-mode display.
- Added unit tests for table-mode.

## 2025-06-24 – Phase 3 Act 4: Analytics Helpers
- Wrote `get_category_distribution`, `get_time_distribution`.
- Unit tests for analytics functions.

## 2025-06-25 – Phase 3 Act 5: ANSI Colors & Hardeners
- Added `colorama` for ANSI styling.
- Unified `confirm_action()`, polished prompts.
- Began edge-case hardening.

## 2025-06-26 – Phase 3 Hardeners: Directory & Locking
- Ensured `~/.collectory/` exists & is writable.
- Implemented atomic JSON writes + thread-safe lock.

## 2025-06-27 – Phase 3 Hardeners: Quit & Recovery
- Final flush on Quit via `try/finally` and SIGINT handler.
- Corrupt-JSON quarantine and recovery.

## 2025-06-28 – Phase 3 Hardeners: I/O-Failure Tests
- Added tests for permission errors, disk-full, backup-prune failures.

## 2025-07-01 – Phase 3 Step 6: Packaging & CLI Entry
- Wrote `setup.py`/`pyproject.toml`, defined `console_scripts`.
- Verified wheel & sdist builds.

## 2025-07-02 – Phase 3 Step 7: README & CHANGELOG
- Finalized `README.md` (install, usage screenshots).
- Created `CHANGELOG.md`.
- Tagged v1.0.0 in Git.

## 2025-07-03 – Phase 3 Step 8 & 9: Help Flag & CI
- Implemented `--help` via `argparse`.
- Added GitHub Actions CI for tests, lint, build.

## 2025-07-04 – Phase 4 Act 0: GUI Environment Setup
- Created `.venv`, installed `PySide6` for desktop GUI.
- Explored event loops, layouts, widget hierarchy, signals.

## 2025-07-04 – Quest 4: Dual-API Harmony
- Scaffolded GraphQL with Ariadne; wrote `Query` & `Mutation`.
- Built REST endpoints in `api/rest.py`.
- Extracted shared logic into `api/services.py`.

## 2025-07-05 – Quest 4: Testing & Documentation
- Wrote integration tests for GraphQL (`tests/test_api.py`) and REST (`tests/test_rest.py`).
- Unit-tested resolvers (`tests/test_resolvers.py`) and services (`tests/test_services.py`).
- Achieved 100% green in `pytest -q` across CLI, REST, GraphQL, services.
- Added full Markdown docs under `markdown/`; zipped as `docs.zip`.
- Bumped version to **1.0.1** on `develop` branch.

> **Next:** switch to **develop** branch, begin **Phase 5 Act 1 (Reflection)** under version 1.0.1.