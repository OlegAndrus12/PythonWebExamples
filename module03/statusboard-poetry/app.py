"""
Flask entry point.

    flask --app app run --debug
"""

import requests
from flask import Flask, redirect, render_template, request, url_for

import incidents
import services
from checks import check_all

app = Flask(__name__)


@app.get("/")
def board():
    return render_template("index.html", results=check_all(services.load()), active="board")


@app.get("/incidents")
def incidents_page():
    """Cloudflare's recent incidents, from its public status API."""
    try:
        found = incidents.fetch()
    except requests.RequestException:
        message = "Could not reach the Cloudflare status API."
        return render_template(
            "incidents.html", incidents=[], error=message, active="incidents"
        ), 502

    return render_template("incidents.html", incidents=found, error=None, active="incidents")


@app.post("/services")
def add_service():
    """Handle the add form, then redirect.

    Answering a POST with a redirect instead of HTML is the Post/Redirect/Get
    pattern. Without it, the browser's address bar still points at a POST, so
    a reload — or the 30-second meta refresh on the board — re-submits the
    form and adds the service again.
    """
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()

    if name and url and name not in services.load():
        services.add(name, url)

    return redirect(url_for("board"))


@app.post("/services/delete")
def delete_service():
    services.remove(request.form.get("name", ""))
    return redirect(url_for("board"))
