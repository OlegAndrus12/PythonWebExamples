"""Launcher for the statusboard app — the protection proxy is wired inside
`app.py` itself (see its bottom section), not here.

Needs Flask + requests, which live in `04_uv`'s venv, not here:

    cd module01/04_uv
    uv run python ../08_patterns/proxy/run.py
"""

from __future__ import annotations

from app import app

if __name__ == "__main__":
    print("Statusboard behind an IP-blocking proxy.")
    print("The wiring lives at the bottom of app.py — see README.md for curl commands.\n")
    app.run(debug=True, port=5001)
