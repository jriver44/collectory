# Changelog

All notable changes to this project are documented in this file.  
See [Keep a Changelog](https://keepachangelog.com/) for guidelines.

### Added
- Prepare for v1.0.0 release: setup packaging, docs, CI, help flag.

## [1.0.0] – 2025-07-03

### Added
- Packaged as `curation` on PyPI.  
- `--help` flag (via Click).  
- Man page draft.  
- GitHub Actions for tests, lint, and build.

## [0.3.3] – 2025-06-25 :contentReference[oaicite:2]{index=2}

### Added
- Analytics helpers (`get_category_distribution`, `get_time_distribution`).  
- ANSI color integration for headers, prompts, success (green) & error (red) messages.  
- Centralized `confirm_action()` for boolean feedback.

### Fixed
- Edge-case handling for invalid inputs & menu choices.

## [0.3.2] – 2025-06-24 :contentReference[oaicite:3]{index=3}

### Added
- Table-mode CLI view using `tabulate` with `tablefmt="grid"`.

### Improved
- Unified listing function `show_table()`.

## [0.2.0] – 2025-06-21 

### Added
- JSON load/save with human-readable formatting.  
- Manual backups prior to save.  
- Timestamp on item creation.  
- `remove_item` and `edit_category` commands.

### Fixed
- Corrupt JSON recovery & fallback to empty collection.  
- File-not-found errors.

## [0.1.0] – 2025-06-20 :contentReference[oaicite:5]{index=5}

### Added
- Basic in-memory CLI: add, list, quit.  
- Plain-dictionary item storage.
