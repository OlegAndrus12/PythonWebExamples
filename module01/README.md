# Module 01 — Python Development

Self-contained folders, one per lecture subtopic, in agenda order. Each folder has its own
`README.md`, its own dependencies, and its own run instructions. **Always `cd` into a folder first** —
nothing here is run from the repo root.

| # | Topic | Folder | Project / domain | What you run |
| --- | --- | --- | --- | --- |
| 2 | pip | [`02_pipenv/`](02_pipenv/) | `statusboard` — uptime board for public sites | a Flask status page over Cloudflare/AWS/Instagram, installed with `pip install -r requirements.txt` |
| 3 | Poetry | [`03_poetry/`](03_poetry/) | `statusboard` again | the identical app, now with `pyproject.toml` + `poetry.lock` and dependency groups |
| 4 | uv | [`04_uv/`](04_uv/) | `statusboard` again | the identical app and the identical `pyproject.toml`, with `uv.lock` — and a resolver 28× faster |
| 5 | Other tooling | [`05_other_tools/`](05_other_tools/) | pyenv, pipx | readme only — Python versions and global CLI tools |
| 6 | Code formatting | [`06_formatting/`](06_formatting/) | `log-triage` — nginx access-log analyser | run ruff/black/isort over a deliberately messy parser |
| 7 | Typing | [`07_typing/`](07_typing/) | `billing-client` — subscription API client | `mypy --strict`, and 8 bugs it catches that tests do not |
| 8 | Design patterns | [`08_patterns/`](08_patterns/) | six patterns, six domains | stdlib-only scripts, no install needed |
| 9 | SOLID | [`09_solid/`](09_solid/) | five separate domains | before/after pairs, proven by a pytest suite |
| — | Tooling benchmark | [`07_compare/`](07_compare/) | measures folders 2–4 | `bench.py` — 3 tools × 3 operations × 2 dependency sets, rendered to a chart page. Not a lecture subtopic; the numbers folders 3 and 4 quote come from here |

Folders 2–4 each also ship a **deliberately unsatisfiable dependency set** in a file of its own, so
you can watch the same conflict handled by all three tools — `requirements-conflict.txt`,
`conflict/pyproject.toml`, `conflict/pyproject.toml`. Each folder's README has a
"Конфлікт залежностей" section with the command and the real output. None of them touch that folder's
working manifest or lock file.

## Ground rules for everything in this module

- **Every file runs.** A "before" example demonstrates its failure by catching and printing it, not by
  dumping a traceback. The two files that crash on purpose say so in their docstring. The genuine
  exceptions are `bandit_demo/insecure.py` in folders 2–4 and `mypy_demo/broken.py` in `03_poetry`:
  they exist to be *scanned*, never executed, and their docstrings say so.
- **No toy examples.** Every domain is something a working developer actually builds. No shapes, no
  animals, no `foo`/`bar`.
- **Offline by default.** Seeded randomness, in-memory SQLite, local stub servers. The exceptions —
  folders 2–4 (HTTP probes against public sites, plus Cloudflare's status API) and `09_solid`'s FX
  report — are noted in their READMEs. The *test suites* never touch the network.
- **English in the code**, including comments and docstrings. The READMEs of folders 2–5 are in
  Ukrainian — they double as lecture notes.

## Prerequisites

```bash
uv python install 3.13     # or: pyenv install 3.13
uv tool install poetry
```

`02_pipenv` needs nothing but the standard library's `venv` module — that is the point of it.
`03_poetry` needs Poetry, `04_uv` needs uv, and neither needs the other. `05_other_tools` is a
reference sheet and needs nothing at all.

Folders 2–4 each carry the same dev tooling — `pytest`, `ruff`, `bandit`, `pre-commit` — installed
the way that folder's manager does it: `requirements-dev.txt`, a Poetry group, and a PEP 735
`[dependency-groups]` respectively. `03_poetry` additionally carries `mypy` and `types-requests`,
since a type checker is the clearest example of a dependency group that must never reach production;
the typing *concepts* are folder 7's job.

## Reading order

Folders 2–4 are one lesson told three times: the **same application**, byte-for-byte identical, with
only the dependency manager changing. Do them in order — each is defined by what the previous one
could not do.

Folder 5 is a reference sheet with no code. Folders 6–7 are independent of each other. Folders 8–9 are
independent of everything else, so if you are short on time, start there — they are the ones the rest
of the course leans on hardest.

> The folder is still called `02_pipenv` although it teaches plain `pip`. Renaming it to `02_pip` is a
> single `git mv`; nothing but this table points at the path.

## Where each topic pays off later

| Introduced here | Used again in |
| --- | --- |
| `pyproject.toml` and PEP 621 | `07_typing`, `pydantic_ex/`, every project from module04 on |
| Lock files and hash pinning | every deployed project in the course |
| Jinja2 templates and `url_for` | `todos/`, `module03/flask-node/` |
| `pytest` fixtures and `monkeypatch` | `09_solid`, `zoo_api/` |
| `Protocol` and dependency inversion | `09_solid` (D), `zoo_api/src/services/` |
| `TypedDict` and the runtime-validation gap | `pydantic_ex/` |
| `contextvars` | `module04/async_ex/` |
| Structured logging | `zoo_api/` |
| Middleware chain | `module04/`, `zoo_api/main.py` |

## Note on the older material

`patterns/` and `solid/` are the previous version of subtopics 8 and 9, kept for reference. The numbered
folders supersede them.
