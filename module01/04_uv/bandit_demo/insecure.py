"""A deliberately insecure file, written to be scanned — never to be run.

Every function below trips at least one bandit rule. Nothing here is imported
by the application, and the folder is listed in the bandit config's
`exclude_dirs`, so a normal project scan stays clean. Point bandit at this file
explicitly to see the report:

    bandit -r bandit_demo/

The shell commands are harmless on purpose (`echo`, `ls`). Bandit flags the
*pattern*, not the payload, so there is no reason for a teaching file to carry
a destructive one. The credentials are obvious fakes.

DO NOT copy any of this into real code. That is the entire point of the file.
"""

import ftplib
import hashlib
import os
import pickle
import random
import shelve
import ssl
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from urllib.request import urlopen

import requests
import yaml
from jinja2 import Environment

# ── B105 / B106 / B107: hardcoded credentials ──────────────────────────
API_TOKEN = "sk_live_totally_fake_do_not_use"  # B105
DB_PASSWORD = "hunter2"  # B105


def connect(user, password="hunter2"):  # B107 default arg
    return f"{user}:{password}"


def login():
    return connect("admin", password="hunter2")  # B106 funcarg


# ── B108: hardcoded /tmp path ──────────────────────────────────────────
def write_report(data):
    """Predictable path in a world-writable directory — a symlink attack."""
    with open("/tmp/report.txt", "w") as handle:  # B108
        handle.write(data)


def write_report_safely(data):
    """The fix: let the OS pick an unpredictable name."""
    with tempfile.NamedTemporaryFile("w", delete=False) as handle:
        handle.write(data)
        return handle.name


# ── B102 / B307: executing strings ─────────────────────────────────────
def run_expression(source):
    exec(source)  # B102
    return eval(source)  # B307


# ── B602 / B605 / B607: shell injection ────────────────────────────────
def list_dir(path):
    subprocess.call(f"ls {path}", shell=True)  # B602 (High)
    os.system(f"echo {path}")  # B605
    subprocess.Popen(["ls", path])  # B607 partial path


def list_dir_safely(path):
    """The fix: an argument list, no shell, absolute binary."""
    subprocess.run(["/bin/ls", path], check=False, shell=False)


# ── B303 / B324: weak hashing ──────────────────────────────────────────
def fingerprint(value):
    return hashlib.md5(value.encode()).hexdigest()  # B324


def fingerprint_safely(value):
    return hashlib.sha256(value.encode()).hexdigest()


# ── B311: predictable randomness ───────────────────────────────────────
def make_reset_token():
    """random is seeded predictably — never use it for anything secret."""
    return "".join(random.choice("0123456789abcdef") for _ in range(32))  # B311


def make_reset_token_safely():
    import secrets

    return secrets.token_hex(16)


# ── B501 / B113: careless HTTP ─────────────────────────────────────────
def fetch_ignoring_tls(url):
    return requests.get(url, verify=False, timeout=5)  # B501 (High)


def fetch_without_timeout(url):
    """No timeout: this call can hang forever and take the app with it."""
    return requests.get(url)  # B113


# ── B310: unvalidated URL scheme ───────────────────────────────────────
def read_url(url):
    """`file://` and `ftp://` are accepted too — that is the problem."""
    return urlopen(url).read()  # B310


# ── B323: TLS verification disabled globally ───────────────────────────
def unverified_context():
    return ssl._create_unverified_context()  # B323


# ── B301 / B403: unpickling untrusted data ─────────────────────────────
def load_session(blob):
    """Unpickling attacker-controlled bytes is arbitrary code execution."""
    return pickle.loads(blob)  # B301


def open_shelf(path):
    return shelve.open(path)  # B301 family


# ── B506: yaml.load without a safe loader ──────────────────────────────
def load_config(text):
    return yaml.load(text)  # B506


def load_config_safely(text):
    return yaml.safe_load(text)


# ── B314 / B405: XML parsing ───────────────────────────────────────────
def parse_xml(text):
    """Vulnerable to billion-laughs and external-entity attacks."""
    return ET.fromstring(text)  # B314


# ── B321 / B402: cleartext protocols ───────────────────────────────────
def download(host):
    session = ftplib.FTP(host)  # B321
    session.login("anonymous", "anonymous@example.com")
    return session


# ── B608: SQL built by string formatting ───────────────────────────────
def find_user(cursor, name):
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)  # B608
    return cursor.fetchone()


def find_user_safely(cursor, name):
    """The fix: parameters, so the driver escapes them."""
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cursor.fetchone()


# ── B701: Jinja2 without autoescaping ──────────────────────────────────
def render(template, **context):
    """autoescape=False turns every rendered value into an XSS vector."""
    env = Environment(autoescape=False)  # B701
    return env.from_string(template).render(**context)


# ── B110 / B112: swallowed exceptions ──────────────────────────────────
def ignore_everything(paths):
    """Note the exception types: bandit only complains about the broad ones.

    `except OSError: pass` is not flagged — catching a specific error you know
    how to ignore is legitimate. `except Exception: pass` hides bugs you have
    never even seen, which is why B110 exists.
    """
    for path in paths:
        try:
            os.remove(path)
        except Exception:  # noqa: BLE001
            pass  # B110

    for path in paths:
        try:
            os.stat(path)
        except Exception:  # noqa: BLE001
            continue  # B112


# ── B201: Flask debug mode in production ───────────────────────────────
def serve():
    """The Werkzeug debugger exposes an interactive console to the internet."""
    from flask import Flask

    app = Flask(__name__)
    app.run(debug=True)  # B201 (High)
