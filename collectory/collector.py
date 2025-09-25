""" Curation CLI entrypoint

Interactive terminal app for managing collections with customizable
categories. Provides CRUD operations, filtering/search, summaries of date/category
distributions, and periodically autosaves with timestamped rotating backups.

Responsibilities
---------------
    - Parse CLI args (REPL-only at the moment).
    - Load the selected collection from the disk.
    - Start/own the background autosave loop.
    - Run the interactive REPL that calls into domain operations.
    - Persist data with atomic writes + rotating backups.

Relationships
-------------
Depends on:
    - collectory.analysis: pure domain helpers (mutations, filters, and aggregation).
    - collectory.config: file locations, autosave interval, and backup policy.
    
Used by:
    - End userss directly via 'python -m ...' or the 'curation' entrypoint.
    
Persistence Boundry
--------------------
    - All disk I/O (load/save/backup rotation) happens here.
    - Writes use 'atomic_write()' with a module-wide '_save_lock' to seralize and writes
    across threads and avoids partial/corrupt files.
    
Threading Model
----------------
    - One background daemon thread ('autosave_loop') that periodically calls 'save_items'. It cooperates
    via '_save_lock' and can be stopped with '__stop_event_'.
    - The REPL runs on the main thread and all mutations to 'items' are done here.
    
CLI surface
------------
    - REPL menu (1-9). No subcommands yet.
    
Usage
-----
    $ curation
"""

import argparse
import errno
import json
import os
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style
from tabulate import tabulate
from typing import Optional, Tuple, List, Dict, Any

# Domain logic and analysis helpers (pure operations, no I/O)
from collectory.analysis import ( 
    increment_quantity, 
    create_new_item, 
    remove_item, 
    filter_by_category, 
    search_by_keyword,
    get_category_distribution,
    get_time_distribution
)
from collectory import config

# Initialize terminal color handling only once
init(autoreset=True)

# Single lock for full program serialized writing to disk
_save_lock = threading.Lock()

# stop autosave loop cleanly on exit with one last atomic save
_stop_event = threading.Event()

# Timestamp format
TIME_FMT = "%Y-%m-%d %H:%M:%S"

def main():
    """ Top level CLI: parses args, loads data, starts autosave, runs REPL loop
    Flow:
        1) Parse CLI args (placeholder for future subcommands).
        2) Prompt for a collection name and load items from disk.
        3) Start a daemon autosave thread (interval from config).
        4) Enter REPL (menu-driven), muatating in-memory 'items'.
        5) On exit or interrupt, perform a final save.
        
        
    Side Effects:
        - Read/write files under 'config.DATA_DIR'.
        - Spawns a deamon thread for autosave.
    """
    parser = argparse.ArgumentParser(
        prog="curation",
        description="Curation: a CLI colleciton tracker with analytics."
    )
    parser.parse_args() # NOTE: currently no subcommands; REPL only
    
    running = True

    # --- Startup: choose collection & load items ----------------------
    file_name = prompt_nonempty("Enter name to load: ")
    path = config.collection_path(file_name)
    items = load_items(path)
    
    # --- Autosave: background thread ----------------------------------
    # Periodically writes the current items list to disk + backup. Uses
    # Now uses a cooperative stop event so shutdown is deterministic
    t = threading.Thread(
        target=autosave_loop,
        args=(file_name, items),
        daemon=True
    )
    t.start()
    
    try:
        # --- Main REPL loop --------------------------------------------
        while running:
            display_menu()
            choice = prompt_nonempty("Select an option (1-9): ")
            if choice == "1":
                # Add item: either increments existing exact "name+category" match or creates new a one
                name = prompt_nonempty("Enter new item name: ")
                category = prompt_nonempty("Enter item category: ")
                quantity = prompt_positive_int("Quantity to add: ")
            
                matches = [e for e in items 
                       if e["name"].lower() == name.lower() 
                       and e["category"].lower() == category.lower()
                        ]
                if matches:
                    entry = matches[0]
                    increment_quantity(entry, quantity)
                    print_success(f"{quantity} added to '{name}'. New total: {entry['quantity']}")
                else:
                    create_new_item(name, items, category, quantity)
                    print_success(f"Created new item '{name}' x {quantity}.")
                    
            elif choice == "2":
                # Remove an item (by name) with a quantity 
                target = prompt_nonempty( "Enter name of item to remove: ")
                quantity = prompt_positive_int("Quantity to remove: ")
                success = remove_item(items, quantity, target)
                confirm_action(
                    success,
                    success_message = f"Removed {quantity} x {target}",
                    error_message = f"Couldn't remove {target}"
                )
                
            elif choice == "3":
                # Edit category for an item found by name
                target  = prompt_nonempty("Enter name of item to re-categorize: ")
                success = edit_category(items, target)
                confirm_action(
                    success,
                    success_message = f"{target}'s category changed successfully.",
                    error_message = f"{target}'s category wasn't changed."
                    )
                
            elif choice == "4":
                # Display table of all items in terminal
                show_table(items)
                
            elif choice == "5":
                # Save collection and rotate backups
                success = save_items(file_name, items)
                confirm_action(
                    success, 
                    success_message = f"Collection saved to {file_name} and backed up successfully.",
                    error_message = f"Save failed."
                )
                
            elif choice == "6":
                # Summarizes category and time distribution
                show_summary(items)
                
            elif choice == "7":
                # Filter by category and display subset
                category = prompt_nonempty("Enter category to filter: ").strip()
                results = filter_by_category(items, category)
                if results:
                    show_table(results)
                else:
                    print_error(f"No items found in '{category}'.")
                    
            elif choice == "8":
                # Keyword search 
                keyword = prompt_nonempty("Enter search keyword: ")
                results = search_by_keyword(items, keyword)
                if results:
                    if isinstance(results, list) and results and isinstance(results[0], dict):
                        show_table(results)
                    else:
                        print(results)
                else: 
                    print_error("Keyword not in collection.")
                
            elif choice == "9":
                running = False
                
            else:
                print_error("Please choose input from menu above (1-9)")
                
    except (KeyboardInterrupt, EOFError):
        # Graceful interruption that will proceed to final save in finally
        print(f"\n{Fore.CYAN}Interrupted, saving and exiting...")
        
    finally:
        # --- Graceful shutdown -----------------------------------------------
        # 1) Signal autosave loop to stop, 2) wait briefly for thread exit,
        # 3) perform one last atomic save.
        request_shutdown()
        # Wait up to a tick for the autosave loop to observe the event
        # (daemon=True means the process would exit anyway but keep it tidy)
        t.join(timeout=config.AUTOSAVE_INTERVAL + 0.1)
        
        print(Fore.CYAN + "Saving before exit...")
        ok = save_items(file_name, items)
        confirm_action(ok,
                       success_message = "Final save succeeded.",
                        error_message = "Final save FAILED")
        print("Have a great day!")
    
    
def atomic_write(fname: Path, data: Any) -> None:
    """Atomically write JSON to 'fname' using a temp file + replace.
    
    Atomic write protocol (POSIX-friendly):
        1) Create a temp file in the same directory as 'fname' (ensures
        'os.replace' is atomic on the same filesystem).
        2) Dump JSON to the temp file and 'flush' + os.fsync' the descriptor.
        3) 'os.replace(tmp,fname)' to swap in the new file automatically.
        
    Concurrency
        - Protected by a module-wide '_save_lock' to avoid overlapping writes
    Args:
        fname (Path): Target JSON file path
        data (Any): JSON-serializable content. 
    """
    fname.parent.mkdir(parents=True, exist_ok=True)
    
    # Create temp in the same directory to ensure atomic rename/replace
    tmp_path: Path | None = None
    
    with _save_lock:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(fname.parent),
                prefix=fname.name + ".",
                suffix=".tmp",
                delete=False,
            ) as tmp:
                # Write JSON with UTF-8 and pretty indent while keeping unicode characters
                json.dump(data, tmp, indent=2, ensure_ascii=False)
                # Make sure data is flushed to disk before replacing
                tmp.flush()
                os.fsync(tmp.fileno())
                tmp_path = Path(tmp.name)
            
            # Atomic swap: on success, either old or new exists, and no partial file
            os.replace(str(tmp_path), str(fname))
        
        except PermissionError:
            print_error("Permission denied: cannot write data file.")
            # Best-effort cleanup of temp
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise
        
        except OSError as e:
            if e.errno == errno.ENOSPC:
                print_error("No space left on device: save failed")
            else:
                print_error(f"Filesystem error during save: {e}")
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise
    
    
def autosave_loop(file_name: str, items: list) -> None:
    """Background loop that periodically saves the in-memory items.
    
    Respects:
        - feature flag 'config.AUTOSAVE_ENABLED'
        - sleeps for 'config.AUTOSAVE_INTERVAL' seconds.
        
    Threading: 
        - Runs forever as a daemon thread (no stop event).
        - SYnchronizes with manual saves via '_save_lock'.
        
    Args:
        file_name: Logical collection name (used to derive file paths).
        items: The in-memory list of item dicts to persist.
    """
    while not _stop_event.wait(config.AUTOSAVE_INTERVAL):
        if config.AUTOSAVE_ENABLED:
            save_items(file_name, items)
            
def request_shutdown():
    _stop_event.set()
            
def show_table(items: list) -> None:
    """Print items as a grid table, otherwise notify collection is empty.
    
    Columns: ID, Name, Category, Quantity, Time
    
    Args:
        items: The current collection (list of dicts with the core fields).
        
    Side Effects:
        Prints to stdout.
    """
    if not items:
        print_error("No items in collection.")
        return
    
    rows = [
        [item.get("id", ""), item["name"], item["category"], item["quantity"], item["time"]]
        for item in items
    ]
    headers = ["ID", "Name", "Category", "Quantity", "Time"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
        
def load_items(path: Path) -> list:
    """Load items from JSON file.

    Behavior:
        - If the file doesn't exist: return [] and warn.
        - If JSON is corrupt: move the bad file aside with a timestamp and return [].
        - If JSON is valid but not a list: warn and return [].
        
    Args:
        path: Fully resolved path to the JSON collection.
        
    Returns:
        A list of item dicts (possibly empty).
        
    Side Effects:
        May rename a corrupt JSON file to '*_corrupt_<timestamp>.json'.
        
    Notes:
        Function is intentionally forgiving to keep the CLI usable even if
        the file is missing or damaged.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data: Any = json.load(f)
        if not isinstance(data, list):
            print_error(f"Data at {path} is not a JSON list. Starting with an empty collection.")
            return []
        return data
    
    except FileNotFoundError:
        print_error(f"No file found at {path!s}. Starting with an empty collection.")
        return []

    except json.JSONDecodeError:
        # Quarantine corrupt file so a fresh one can be created
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        corrupt = path.with_name(f"{path.stem}_corrupt_{ts}{path.suffix}")
        try:
            path.replace(corrupt)
            print_error(f"Corrupt data detected. Moved bad file to {corrupt.name}.")
        except Exception as e:
            # If we can't move it, at least report the issue
            print_error(f"Corrupt data detected at {path}, but could not move file: {e}")
        return []

    except PermissionError:
        print_error(f"Permission denied reading {path}.")
        return []
        
def save_items(file_name: str, items: list) -> bool:
    """Persist current items and write a timestamped backup. Rotates old backups afterwards.

    Protocol (under '_save_lock'):
        1) Write the main file '<file_name>.json' automatically.
        2) Write a timestamped backup '<file_name>_<YYYYmmddTHHMMSS><suffix>.json'.
        3) Prune old backups keeping the newest 'config.MAX_BACKUPS'.
        
    Args:
        file_name: Logical collection name (determines filenames).
        items: in-memory list of item dicts.
        
    Returns:
        True on success (main save + backup + rotation), False otherwise. 
        
    Side Effects:
        Writes/renames/deletes files in 'config.DATA_DIR'
    """
    with _save_lock:
        data_dir = config.DATA_DIR
        base = data_dir / f"{file_name}.json"
    
        try:
            atomic_write(base, items)
            ts = datetime.now().strftime("%Y%m%dT%H%M%S")
            backup = data_dir / f"{file_name}_{ts}{config.BACKUP_SUFFIX}.json"
            atomic_write(backup, items)
        
            return rotate_backups(data_dir, file_name, keep=config.MAX_BACKUPS)
        except Exception as e:
            print_error(f"Save failed: {e}")
            return False
        
def edit_category(items: list, target: str) -> bool:
    """Update the 'category' field of the first item whose name matches 'target'.
    
    Args:
        items: the collection (mutated in place).
        target: name to match (case-insensitive).
        
    Returns:
        True if the item was found and updated, False otherwise
        
    Side Effects:
        Prompts the user for the new category if a match is found.
    
    """
    for item in items:
        if item['name'].lower() == target.lower():
            new_category = prompt_nonempty(f"Enter new category for {target}: ")
            item['category'] = new_category
            return True
    return False

def items_per_category(items):
    """Print a count of *items* per category (not quantities of items themselves).
    
    Args:
        items: current colleciton.
        
    Returns:
        True if any categories were found (and printed), False if empty.
        
    Notes:
        This function counts entries per category (one per item row), not the sum of 'wuantity'. 
        Use 'get_category_distribution' for quantity totals.
    
    """
    categories_count = {}
    for item in items:
        category = item['category']
        if category not in categories_count:
            categories_count[category] = 1
        else:
            categories_count[category] += 1
    if not categories_count:
        print_error("Items per category: none")
        return False
    else: 
        print_success("Items per category: ")
        sorted_categories = sorted(categories_count.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            print(f"    {category}: {count}")
        return True
            
def show_summary(items):
    """Print a high-level summary: total items, by category, by time bucket.
    
    Prints:
        - Total number of *rows* (len(itmes)).
        - Category distribution (by *quantity*).
        - Time distribution (by *quantity*, default monthly buckets).
    
    """
    print(f"Total items: {len(items)}")
    for category, quantity in get_category_distribution(items).items():
        print(f"    {category}: {quantity}")
    for period, quantity in get_time_distribution(items).items():
        print(f"    {period}: {quantity}")
        
def _parse_time_or_none(s: str) -> Optional[datetime]:
    """Parese 's' using TIME_FMT, returning None on failure (non-throwing).

    Args:
        s: a timestamp string in the expected TIME_FMT.

    Returns:
        A datetime if parsing succeeds, otherwise None.
    """
    try:
        return datetime.strptime(s, TIME_FMT)
    except Exception:
        return None
    
def oldest_newest(items: list) -> None:
    """Print oldest and newest item by 'time' field (YYYY-mm-dd HH:MM:SS).
    
    Behavior:
        - Silently skips items with missing or invalid 'time'.
        - If none are valid, prints a friendly error.
        
    Args:
        items: current collection
    
    """
    if not items:
        print_error("No items in system to display.")
        return
    
    # Precompute (parsed_dt, item) pairs, skipping any with bad/missing time.
    parsed: List[Tuple[datetime, Dict[str, Any]]] = []
    for item in items:
        time = item.get("time")
        if isinstance(time, str):
            datetime = _parse_time_or_none(time)
            if datetime is not None:
                parsed.append((datetime, item))
                
    if not parsed:
        print_error("No valid timestamps found on items.")
        return
    
    # NOTE: update for consistency
    oldest_datetime, oldest_item = min(parsed, key=lambda p: p[0]) # NOTE: Consider formatting date output later 
    newest_datetime, newest_item = max(parsed, key=lambda p: p[0])
    
    print(f"Oldest item: {oldest_item.get('name', '(unknown)')}\nDate/Time: {oldest_item.get('time', '')}\n")
    print(f"Newest item: {newest_item.get('name', '(unknown)')}\nDate/Time: {newest_item.get('time', '')}\n")
        
def rotate_backups(data_dir: Path, prefix: str, keep: int) -> bool:
    """Keep only the newest 'keep' backups for the given collection prefix.
    
    Args:
        data_dir: Directory containing the backups.
        prefix: Collection base name used to backup filenames.
        keep: Number of most-recent backups to retain.
        
    Returns:
        True if all deletions succeeded, False otherwise.
        
    File Pattern:
        '{prefix}_*{config.BACKUP_SUFFIX}.json'
        
    Notes:
        - Files are sorted by modification time (newest first).
        - Failures to delete are reported but not raised.
    """
    pattern = f"{prefix}_*{config.BACKUP_SUFFIX}.json"
    backups = sorted(
        data_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    success = True
    for old in backups[keep:]:
        try:
            old.unlink()
            print_success(f"Pruned old backup : {old}")
        except Exception as e:
            print_error(f"Could not delete {old}: {e}")
            success = False
    return success

def prompt_positive_int(prompt: str) -> int:
    """Prompt until a positive integer is entered.
    
    Args:
        prompt: String to display to the user.
        
    Returns:
        A strictly positive integer (> 0).
        
    User Experience:
        - On invalid input, prints an error and re-prompts for positive number.
    """
    while True:
        resp = input(Fore.YELLOW + prompt).strip()
        try:
            val = int(resp)
            if val > 0:
                return val
            else:
                print_error("Please enter a positive integer.")
        except ValueError:
            print_error("Not a number - try again")
            
def prompt_nonempty(prompt: str) -> str:
    """Prompt until a non-empty string is entered.
    
    Args:
        prompt: String to display to the user.
        
    Returns:
        The user's response (stripped), guaranteed non-empty.
    """
    while True:
        resp = input(Fore.YELLOW + prompt).strip()
        if resp:
            return resp
        print_error("Input cannot be blank.")

def print_header(text: str) -> None:
    """Print a cyan bright header"""
    print(Fore.CYAN + Style.BRIGHT + text)
    
def print_success(text: str) -> None:
    """Print a green success message."""
    print(Fore.GREEN + text)
    
def print_error(text: str) -> None:
    """Print a red error message."""
    print(Fore.RED + text)
    
def display_menu() -> None:
    """Render the interactive menu."""
    menu = (
      Fore.CYAN + Style.BRIGHT +
      "\n=== Curation ===\n" + 
      Fore.YELLOW +
      "1) Add Item\n"
      "2) Remove Item\n"
      "3) Edit Category\n"
      "4) View Items\n"
      "5) Save Collection\n"
      "6) Summary\n"
      "7) Filter by Category\n"
      "8) Search by Keyword\n"
      "9) Quit\n" +
      Style.RESET_ALL
    )
    print(menu)
    
def confirm_action(ok: bool, success_message: str, error_message: str | None = None) -> None:
    """Print success/error based on a boolean outcome.
    
    Args:
        ok: Result flag.
        success_message: Message to print when 'ok' is True.
        error_message: Message to print when 'ok' is False (falls back to
        'success_message' if None).
    """
    if ok:
        print_success(success_message)
    else:
        print_error(error_message or success_message)

if __name__ == "__main__":
    main()