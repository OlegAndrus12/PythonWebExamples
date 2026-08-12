"""Report whether the current environment is actually consistent.

`pip install` installs one requirement at a time and does not re-check the
packages already present, so it can leave a venv whose contents contradict each
other. The damage is quiet: the import works, a plain route still answers 200,
and the failure only appears on the code path that needs the API the downgraded
package no longer has.

This file makes that visible. Run it with the interpreter of the venv you want
to inspect — see the README section "Конфлікт залежностей" for the venv that is
deliberately broken:

    python conflict_demo.py

Exit code 0 means the environment is consistent, 1 means it is not.
"""

from __future__ import annotations

import os
import sys
import traceback
from importlib.metadata import version


def build_app():
    """A Flask app whose only route touches the session — i.e. a signed cookie.

    Flask 3.1 sets that cookie through a Werkzeug 3.1 API. On an older Werkzeug
    the call fails, which is why this route is the one that breaks while a
    plain "return 'hello'" route keeps working.
    """
    from flask import Flask, session

    app = Flask(__name__)
    # A throwaway key generated per run: signing has to work for the session to
    # be written at all, and a literal here would be a bandit B105 finding in a
    # folder whose README promises a clean scan.
    app.secret_key = os.urandom(16)
    app.testing = True  # let the real exception through instead of a bare 500

    @app.get("/login")
    def login() -> str:
        session["user"] = "anna"
        return "signed in"

    return app


def main() -> int:
    print(f"flask     {version('flask')}")
    print(f"werkzeug  {version('werkzeug')}")
    print()

    client = build_app().test_client()
    try:
        response = client.get("/login")
    except Exception:  # noqa: BLE001 - the point is to show whatever comes out
        print("The session route raised:\n")
        # stdout, so the traceback stays in order with everything else printed
        traceback.print_exc(file=sys.stdout)
        print(
            "\nThe environment is inconsistent: Flask and Werkzeug versions that"
            "\nwere never meant to run together. `pip check` reports the same"
            "\nthing without executing any code."
        )
        return 1

    print(f"GET /login -> {response.status_code}")
    print("The environment is consistent: Flask and Werkzeug agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
