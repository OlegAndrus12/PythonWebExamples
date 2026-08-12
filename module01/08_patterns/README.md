# 08 — Design patterns

Six patterns. **Standard library only** — no `pyproject.toml`, no install, nothing to break mid-lecture.

```bash
cd module01/08_patterns
python3 01_singleton.py
python3 02_template_method.py
python3 03_proxy_middleware.py
python3 05_strategy.py
python3 06_observer.py

cd adapter && python3 before.py && python3 after.py
```

Python 3.12 or newer (the files use PEP 695 `type` aliases and `class C[T]` generics).

## What a pattern is

A recurring shape in code, given a name so you can point at it in a code review. That is the whole
definition. Patterns are not libraries, they are not rules, and they are not a checklist to work through.
Most of them describe something you would arrive at anyway after being burned once.

The value is almost entirely in the vocabulary. "Make the payment providers a Strategy" is four words
that replace two minutes of explanation, and everyone in the room ends up with the same picture.

## How to read a file in this folder

Every file opens with the same docstring block:

| Section | What it tells you |
| --- | --- |
| **Problem** | The concrete situation, in one sentence. |
| **Before** | The naive code, sketched in four to six lines. This is the version you will actually meet. |
| **After** | What the pattern replaces it with. |
| **Already seen it in** | Where the pattern already lives in Django, FastAPI, SQLAlchemy, requests or the stdlib. This is the part that makes it click. |
| **Cost** | What the pattern charges you, and when to skip it. No file here only sells its pattern. |
| **Run** | The command. |

Singleton, Adapter and Strategy run their "before" version as code instead of only sketching it — the
singleton because its failures (leaking across tests, losing a race) have to be seen to be believed,
adapter because the carrier branching needs room to hurt, and the strategy because a duplicated
`if/elif` chain does too. `adapter/` splits this into `before.py` and `after.py`; everywhere else the
"before" is the sketch in the docstring and the file itself is the "after".

## The files

| # | Pattern | Domain | What you see happen |
| --- | --- | --- | --- |
| 01 | Singleton | application settings | the `__new__` trick leaks `debug=True` into the next test, refuses to be copied, and eight threads build eight "singletons" |
| 02 | Template Method | export jobs | one bug fix in `run()` applies to all three exports |
| 03 | Proxy → middleware | HTTP pipeline | 401 short-circuits before the app runs, a cache layer answers the third request, and the app itself runs twice for four requests |
| [`adapter/`](adapter/) | Adapter | three carrier APIs | strings, floats and kopiykas sorted into one price list |
| 05 | Strategy | payment providers | the naive version refunds a crypto order **0.00** because the second `if/elif` chain has no branch for it |
| 06 | Observer | order events | one handler raises and the others still run |

`03` covers Proxy and Chain of Responsibility together on purpose: a middleware layer *is* a proxy — an
object with the same interface as the thing it wraps, deciding whether and how to call through. Stack
several and you have Django's `MIDDLEWARE`.

## Patterns are not free

Several classic patterns exist to route around limitations that C++ and Java have and Python does not:
no first-class functions, no keyword arguments, no default parameters, no dynamic dispatch on argument
type. Written in Python, those patterns are ceremony — `01_singleton.py` is the clearest case, where the
pattern is strictly worse than the module system it reimplements.

The test before reaching for any pattern is always the same: **name the change it makes cheap.** If you
cannot, you are adding indirection and getting nothing.

## See also

- [`singleton/`](singleton/) — Singleton в деталях, українською: чому `__new__` — не той інструмент,
  і як виглядає модуль налаштувань, який робить ту саму роботу (`python3 main.py`).
- [`proxy/`](proxy/) — Proxy в деталях, українською: справжній WSGI кеш-проксі перед `/incidents`
  навколо копії застосунку statusboard з [`../04_uv/`](../04_uv/); жоден маршрут не змінено, підключення
  — один рядок унизу `app.py` (`uv run python ../08_patterns/proxy/run.py`, запускати з `04_uv/`).
- [`adapter/`](adapter/) — `before.py` branches on carrier and unpacks each payload inline; `after.py` is
  the same three carriers behind one `RateAdapter` (an ABC, not a `Protocol`).
- [`patterns_map.md`](patterns_map.md) — every pattern, where you have met it, and what Python already
  does for you. Also covers the ones deliberately absent from this folder.
- [`../09_solid/`](../09_solid/) — the principles these patterns serve. Patterns are the mechanism;
  SOLID is the motivation.
