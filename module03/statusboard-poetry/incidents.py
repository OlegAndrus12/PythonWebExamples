"""Cloudflare's recent incidents, read from its public status API.

Cloudflare's status page runs on Atlassian Statuspage, which exposes a public
JSON API with no key and no authentication:

    https://www.cloudflarestatus.com/api/v2/incidents.json

Each incident is a plain dict:

    name        what Cloudflare called it
    impact      none | minor | major | critical
    started     timezone-aware datetime
    url         the stspg.io shortlink
    components  tuple of affected component names, possibly empty
"""

from __future__ import annotations

from datetime import datetime

import requests

INCIDENTS_URL = "https://www.cloudflarestatus.com/api/v2/incidents.json"


def _parse(raw: dict) -> dict:
    started = datetime.fromisoformat(raw.get("started_at") or raw["created_at"])

    return {
        "name": raw["name"],
        "impact": raw.get("impact", "none"),
        "started": started,
        "url": raw.get("shortlink", ""),
        "components": tuple(c["name"] for c in raw.get("components", [])),
    }


def fetch(timeout: float = 10.0) -> list[dict]:
    response = requests.get(INCIDENTS_URL, timeout=timeout)
    response.raise_for_status()

    incidents = []
    for raw in response.json()["incidents"]:
        incidents.append(_parse(raw))

    incidents.sort(key=lambda incident: incident["started"], reverse=True)

    return incidents
