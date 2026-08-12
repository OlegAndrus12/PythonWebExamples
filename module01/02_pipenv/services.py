"""The watch list, stored as JSON on disk.

Reading and writing a JSON file is the smallest possible thing that survives a
restart. It is not a database, and the limits show up quickly:

  * Two requests writing at the same moment both read, both modify, and the
    second one to finish wins — the first edit is silently lost. Flask's
    development server is threaded, so this is a real race here, not a
    theoretical one.
  * The whole file is rewritten on every change.
  * There is no schema, so nothing stops a hand-edit from putting a number
    where a URL should be.

All three are fine at six services and unacceptable at six thousand, which is
the argument for SQLite and SQLAlchemy in module05.
"""

from __future__ import annotations

import json
from pathlib import Path

# Relative to this file, not to the working directory. `flask run` can be
# invoked from anywhere, and a relative "services.json" would resolve against
# wherever the shell happens to be.
SERVICES_FILE = Path(__file__).parent / "services.json"


def load() -> dict[str, str]:
    """Read the watch list. A missing file means an empty board, not a crash."""
    if not SERVICES_FILE.exists():
        return {}
    return json.loads(SERVICES_FILE.read_text(encoding="utf-8"))


def save(services: dict[str, str]) -> None:
    SERVICES_FILE.write_text(
        json.dumps(services, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def add(name: str, url: str) -> None:
    """Add one service. `url` may omit the scheme; https is assumed."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    services = load()
    services[name] = url
    save(services)


def remove(name: str) -> None:
    services = load()
    services.pop(name, None)
    save(services)
