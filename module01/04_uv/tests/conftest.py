"""Shared fixtures.

No test opens a socket or touches the real services.json: the watch list is
redirected to a temporary file, and the probing is replaced with a fixed row.
"""

import pytest

import app as app_module
import services

# One healthy row, in exactly the shape checks.check() returns.
FAKE_RESULTS = [
    {
        "name": "Example",
        "url": "https://example.com",
        "status": 200,
        "latency_ms": 12,
        "error": None,
        "ok": True,
    }
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A Flask test client with one service on the board and no network.

    Patch app.check_all, not checks.check_all: app.py imports the function
    with `from checks import check_all`, so its own namespace holds a separate
    reference that patching the source module would not reach.
    """
    monkeypatch.setattr(services, "SERVICES_FILE", tmp_path / "services.json")
    services.save({"Example": "https://example.com"})
    monkeypatch.setattr(app_module, "check_all", lambda *args, **kwargs: FAKE_RESULTS)

    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()
