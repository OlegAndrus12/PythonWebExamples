"""
Flask entry point.

    flask --app app run --debug
"""

import logging
from pathlib import Path

import requests
from colorama import Back, Fore, Style, init
from flask import Flask, redirect, render_template, request, url_for

import incidents
import services
from checks import check_all

# --- logging ----------------------------------------------------------------
#
# Configuring logging is an entry-point job, done once, here. Modules that only
# *emit* records ask for `logging.getLogger(__name__)` and stop there — where
# the output goes is a decision for whoever runs the program, and a library
# that adds its own handlers takes that decision away from them.

# Wraps stderr: translates the color codes on old Windows consoles, and drops
# them when the output is redirected to a file or a pipe. Has to run before
# StreamHandler() below, which captures sys.stderr as it is built.
init()

LOG_FILE = Path(__file__).parent / "app.log"

FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
# The console format leaves the padding out — see ColorFormatter.format below.
CONSOLE_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Style.BRIGHT + Fore.WHITE + Back.RED,
}


class ColorFormatter(logging.Formatter):
    """Console formatter: the level name gets a color, everything else is the same."""

    def format(self, record):
        print(record.__dict__)
        color = LEVEL_COLORS.get(record.levelno, "")
        # Format a copy. Both handlers are handed the same record object, so
        # coloring it in place would put escape codes into app.log as well.

        colored = logging.makeLogRecord(record.__dict__)
        # Pad here, not in the format string: "%(levelname)-8s" would count the
        # escape bytes as characters and the column would come out ragged.
        colored.levelname = f"{color}{record.levelname:<8}{Style.RESET_ALL}"
        return super().format(colored)


# delay=True: the file is opened on the first record actually written, so
# importing this module — as the tests do — leaves no app.log behind.
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", delay=True)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(FILE_FORMAT))

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter(CONSOLE_FORMAT))

# The root logger, not app.logger. Werkzeug's request lines and anything a
# library logs propagate up to root, so configuring it once puts every line in
# the same format. Root sits at DEBUG so records reach both handlers; the file
# handler then filters itself down to INFO.
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

log = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/")
def board():
    results = check_all(services.load())
    down = [result["name"] for result in results if not result["ok"]]

    # The arguments stay separate instead of being f-string'd in: logging only
    # builds the final message if a handler is going to take it, so a DEBUG
    # line in a service running at INFO costs nothing.
    if down:
        log.warning("%d of %d services down: %s", len(down), len(results), ", ".join(down))
    else:
        log.info("all %d services healthy", len(results))

    return render_template("index.html", results=results, active="board")


@app.get("/incidents")
def incidents_page():
    """Cloudflare's recent incidents, from its public status API."""
    try:
        found = incidents.fetch()
    except requests.RequestException:
        # log.exception() is log.error() plus the traceback of the exception
        # being handled. The visitor gets one sentence; the log keeps the
        # stack, which is the half you need to find out why it broke.
        log.exception("Cloudflare status API unreachable")
        message = "Could not reach the Cloudflare status API."
        return render_template(
            "incidents.html", incidents=[], error=message, active="incidents"
        ), 502

    log.info("fetched %d Cloudflare incidents", len(found))
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
        log.info("added service %s -> %s", name, url)
    else:
        # A form that silently does nothing is the kind of bug that gets
        # reported as "the button is broken". The log says which rule rejected it.
        log.warning("rejected add: name=%r url=%r", name, url)

    return redirect(url_for("board"))


@app.post("/services/delete")
def delete_service():
    name = request.form.get("name", "")
    services.remove(name)
    log.info("removed service %r", name)

    return redirect(url_for("board"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
