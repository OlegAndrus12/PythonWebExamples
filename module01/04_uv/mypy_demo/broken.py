# mypy: disallow-untyped-defs, disallow-any-generics, warn-return-any
# mypy: warn-unreachable, strict-equality
"""A deliberately mistyped file, written to be checked — never to be run.

Every block below trips at least one mypy error code. Nothing here is imported
by the application, and the folder is listed in the mypy config's `exclude`,
so a normal `poetry run mypy` stays clean. Point mypy at this file explicitly
to see the report:

    mypy mypy_demo/broken.py

The two `# mypy:` lines at the top are an inline configuration comment. They
switch on the stricter checks for this file only, so the demo does not depend
on how strict the project settings happen to be.

Note what is *not* here: a single syntax error, and not one thing Python
itself would reject at import time. Every line below is valid Python that the
interpreter will happily start executing. That is the whole argument for a
type checker — these are the bugs that survive `python -c "import broken"`.

The last section is the opposite lesson: code mypy accepts and that still
crashes. A clean run is not a proof of correctness.
"""

from __future__ import annotations

import json
import subprocess  # noqa: F401  (only here for the shadowing demo below)
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, Literal, TypedDict, TypeVar, cast, overload

import requests
import statusboard_internals  # [import-not-found] — no such module anywhere
import yaml  # [import-untyped] — PyYAML ships no type information

# ── [arg-type] / [return-value]: the two you meet first ────────────────


def greet(name: str) -> str:
    return f"Hello, {name}"


greet(42)  # [arg-type] — int where str was promised


def latency_label(ms: int) -> str:
    return ms  # [return-value] — declared str, returns int


# ── [assignment]: the wrong thing put in the right box ─────────────────

port: int = "8080"  # [assignment]
timeout: float = 5.0
timeout = None  # [assignment] — float is not Optional unless you say so


# ── [union-attr]: the most valuable check mypy does ────────────────────
#
# This is the class of bug that annotations pay for. The function is honest
# about returning None, and every caller that forgets is now an error.


def find_service(name: str, table: dict[str, str]) -> str | None:
    return table.get(name)


def show(name: str, table: dict[str, str]) -> str:
    url = find_service(name, table)
    return url.upper()  # [union-attr] — url may be None


def show_safely(name: str, table: dict[str, str]) -> str:
    """The fix: narrow before use. mypy follows the `if` and stops complaining."""
    url = find_service(name, table)
    if url is None:
        return "unknown"
    return url.upper()


# ── [attr-defined]: typos and API drift ────────────────────────────────


def status_of(response: requests.Response) -> int:
    return response.status  # [attr-defined] — the attribute is status_code


# ── [call-arg]: wrong number of arguments ──────────────────────────────


def probe(name: str, url: str, timeout: float = 5.0) -> bool:
    return bool(name and url and timeout)


probe("cloudflare")  # [call-arg] — url is required
probe("cloudflare", "https://cloudflare.com", 5.0, True)  # [call-arg] — one too many
probe(name="cloudflare", host="https://x.com")  # [call-arg] — no such keyword


# ── [index] / [operator]: containers and arithmetic ────────────────────


def first_word(text: str) -> str:
    return text["0"]  # [index] — str indices must be int


def total_latency(rows: list[dict[str, int]]) -> int:
    return sum(row["latency_ms"] for row in rows) + "ms"  # [operator]


# ── [var-annotated]: mypy cannot infer from nothing ────────────────────

seen = []  # [var-annotated] — an empty list of what?
seen_ok: list[str] = []  # the fix


# ── [list-item] / [dict-item]: one bad element ─────────────────────────

ports: list[int] = [80, 443, "8080"]  # [list-item]
labels: dict[str, str] = {"http": "80", "https": 443}  # [dict-item]


# ── [return]: a branch that falls off the end ──────────────────────────


def impact_rank(impact: str) -> int:
    """Returns None on any other input — silently, at runtime."""
    if impact == "critical":
        return 3
    if impact == "major":
        return 2  # [return] — no return on the remaining path


# ── [no-untyped-def]: the annotation that is missing ───────────────────


def check_all(services):  # [no-untyped-def] — needs disallow-untyped-defs
    return [probe(name, url) for name, url in services.items()]


# ── [type-arg]: a generic left bare ────────────────────────────────────


def summarise(rows: list) -> dict:  # [type-arg] x2 — list of what? dict of what?
    return {"count": len(rows)}


# ── [no-any-return]: Any leaking out through a typed signature ─────────


def load_services(path: str) -> dict[str, str]:
    """`json.loads` returns Any, so nothing here is actually checked.

    This is the real limitation of a type checker: the errors come from the
    edges of the program, where data arrives untyped. Anything downstream of
    an Any is invisible to mypy.
    """
    with open(path) as handle:
        return json.loads(handle.read())  # [no-any-return]


def load_services_safely(path: str) -> dict[str, str]:
    """The fix: assert the shape at the boundary, once, where it enters."""
    with open(path) as handle:
        data = json.loads(handle.read())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected an object")
    return {str(key): str(value) for key, value in data.items()}


# ── [override]: a subclass that breaks its parent's promise ────────────


class Probe:
    def run(self, url: str, timeout: float = 5.0) -> bool:
        return bool(url and timeout)


class LoggingProbe(Probe):
    def run(self, url: int) -> str:  # [override] — narrower args, wrong return
        return str(url)


# ── [misc]: instantiating something abstract ───────────────────────────


class Reporter:
    def __init__(self) -> int:  # [misc] — __init__ must return None
        self.rows: list[str] = []
        return 0


# ── [name-defined] / [no-redef]: names ─────────────────────────────────


def render_board() -> str:
    return render_row(rows)  # [name-defined] x2 — neither exists


def subprocess() -> None:  # [no-redef] — shadows the imported module
    pass


# ── [unreachable]: code that can never run ─────────────────────────────


def describe(count: int) -> str:
    if count < 0:
        raise ValueError("negative")
    return f"{count} services"
    print("never printed")  # [unreachable]


def describe_optional(name: str) -> str:
    if name is None:  # [unreachable] — str is never None
        return "unnamed"
    return name


# ── [comparison-overlap]: a check that is always False ─────────────────


def is_ok(status: int) -> bool:
    return status == "200"  # [comparison-overlap] — int vs str, never equal


# ── [truthy-function]: a forgotten pair of parentheses ─────────────────


def refresh() -> bool:
    return True


def maybe_refresh() -> str:
    if refresh:  # [truthy-function] — the function object, always truthy
        return "refreshed"
    return "skipped"


# ── [typeddict-item] / [literal-required]: structured dicts ────────────


class Incident(TypedDict):
    name: str
    impact: Literal["none", "minor", "major", "critical"]
    resolved: bool


def build_incident() -> Incident:
    return {
        "name": "Elevated errors",
        "impact": "catastrophic",  # [typeddict-item] — not in the Literal
        "resolved": "no",  # [typeddict-item] — str, not bool
        "region": "eu-west",  # [typeddict-unknown-key]
    }


def field_of(incident: Incident, key: str) -> object:
    """A TypedDict is a dict at runtime and a record to mypy — keys are literals."""
    return incident[key]  # [literal-required]


# ── [call-overload]: no matching signature ─────────────────────────────


@overload
def fetch(url: str) -> str: ...
@overload
def fetch(url: str, as_bytes: Literal[True]) -> bytes: ...


def fetch(url: str, as_bytes: bool = False) -> str | bytes:
    body = requests.get(url, timeout=5).content
    return body if as_bytes else body.decode()


fetch(b"https://example.com")  # [call-overload] — bytes matches no overload


# ── [valid-type]: an annotation that is not a type ─────────────────────


def parse(text: str) -> json:  # [valid-type] — a module is not a type
    return yaml.safe_load(text)


# ── [func-returns-value]: using the result of a None function ──────────


def log(message: str) -> None:
    print(message)


greeting: str = log("board refreshed")  # [func-returns-value]


# ── [unused-ignore]: a silencer left behind ────────────────────────────

count: int = len("statusboard")  # type: ignore[assignment]  # [unused-ignore]


# ── [type-var]: a constrained TypeVar given something else ─────────────

Number = TypeVar("Number", int, float)


def double(value: Number) -> Number:
    return value * 2


double("statusboard")  # [type-var] — str is neither int nor float


# ── [abstract]: instantiating an unfinished class ──────────────────────


class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...


Notifier()  # [abstract] — send() has no implementation


# ── [misc]: a generator that yields the wrong thing ────────────────────


def wrong_iterator() -> Iterator[int]:
    yield "1"  # [misc] — yields str from an Iterator[int]


# ══════════════════════════════════════════════════════════════════════
# What mypy does NOT catch
# ══════════════════════════════════════════════════════════════════════
#
# Everything below passes the type check and crashes at runtime. A green
# mypy run means "the annotations are consistent", not "the program works".


def crash_on_empty(rows: list[str]) -> str:
    """IndexError on []. Types say nothing about how many elements there are."""
    return rows[0]


def crash_on_zero(total: int, count: int) -> float:
    """ZeroDivisionError. int is int, whatever its value."""
    return total / count


def lie_with_cast(payload: object) -> str:
    """`cast` asserts a type without checking it — it is a promise, not a test.

    Wrong here, and mypy has no way to know: it was told to trust you.
    """
    return cast(str, payload).upper()


def lie_with_any(config: Any) -> str:
    """Any absorbs everything — the whole chain below is checked against nothing.

    Note that mypy is not silent here by accident: `warn-return-any` catches
    the value on its way *out*. Nothing catches what happened on the way.
    """
    return str(config.services.first().name.whatever())


def missing_at_runtime() -> str:
    """The annotation is right, the code is wrong, and mypy sees only the type."""
    services: dict[str, str] = {}
    return services["cloudflare"]  # KeyError
