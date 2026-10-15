#!/usr/bin/env python3
"""Preview or restore VS Code UI visibility. Close all VS Code windows before apply."""
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path


def restore(database, desired, apply=False):
    if set(desired) != {"workbench.statusbar.hidden", "menu.hiddenCommands"}:
        raise ValueError("UI state must contain exactly the two managed keys")
    hidden = desired["workbench.statusbar.hidden"]
    menus = desired["menu.hiddenCommands"]
    if not isinstance(hidden, list) or not all(isinstance(v, str) for v in hidden):
        raise ValueError("Hidden status entries must be a list of strings")
    if not isinstance(menus, dict) or not all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(i, str) for i in v)
        for k, v in menus.items()
    ):
        raise ValueError("Hidden commands must map menu names to lists of strings")
    mode = "rw" if apply else "ro"
    with sqlite3.connect(database.resolve().as_uri() + "?mode=" + mode, uri=True) as connection:
        changes = {}
        for key, value in desired.items():
            row = connection.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
            if row is None or json.loads(row[0]) != value:
                changes[key] = value
        if changes and apply:
            backup = database.with_name(database.name + ".ui-backup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
            with sqlite3.connect(backup) as destination:
                connection.backup(destination)
            print(f"Backup: {backup}")
            with connection:
                for key, value in changes.items():
                    connection.execute("INSERT OR REPLACE INTO ItemTable (key,value) VALUES (?,?)", (key, json.dumps(value)))
            for key, value in changes.items():
                row = connection.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
                if json.loads(row[0]) != value:
                    raise RuntimeError(f"Verification failed: {key}")
        return list(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path.home() / ".config/Code/User/globalStorage/state.vscdb")
    parser.add_argument("--apply", action="store_true", help="Write changes; close all VS Code windows first")
    args = parser.parse_args()
    desired = json.loads(Path(__file__).with_name("ui-state.json").read_text())
    changes = restore(args.database, desired, args.apply)
    print(("Applied: " if args.apply else "Would change: ") + (", ".join(changes) or "none"))


if __name__ == "__main__":
    main()
