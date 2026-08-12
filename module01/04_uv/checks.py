"""Probe a URL, report what happened.

Nothing in this file imports Flask. Health checking is not a web concern — it
is a thing the web layer happens to call — and keeping the two apart is what
lets you reuse this module from a cron job, a test, or a Slack bot later.

Each probe is a plain dict with a fixed set of keys:

    name        the label shown on the board
    url         what was requested
    status      HTTP status code, or None if the request never completed
    latency_ms  round trip in whole milliseconds, or None on failure
    error       exception class name, or None on success
    ok          True when a response came back under 400

Every key is present in every result, including the failure case. A dict whose
shape depends on which branch built it is the thing that turns into a KeyError
three files away.
"""

from __future__ import annotations

import time

import requests


def check(name: str, url: str, timeout: float = 5.0) -> dict:
    """Make one request and time it.

    Every network error is caught and turned into a row. A status page that
    raises when a monitored site is down goes down with the thing it monitors,
    which is the one moment it needed to stay up.

    `requests.get` follows redirects by default. That is why Instagram, which
    bounces anonymous visitors to a login page, still reports 200.
    """
    started = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as err:
        return {
            "name": name,
            "url": url,
            "status": None,
            "latency_ms": None,
            "error": type(err).__name__,
            "ok": False,
        }

    return {
        "name": name,
        "url": url,
        "status": response.status_code,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "error": None,
        "ok": response.status_code < 400,
    }


def check_all(services: dict[str, str], timeout: float = 5.0) -> list[dict]:
    """Probe every service, one after another.

    The page therefore takes as long as all the probes added together. With six
    services that is under a second, and the simplicity is worth more than the
    time saved. It stops being worth it somewhere around twenty.
    """
    return [check(name, url, timeout) for name, url in services.items()]
