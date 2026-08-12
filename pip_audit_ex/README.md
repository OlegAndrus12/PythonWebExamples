# pip-audit example

A deliberately vulnerable environment for demonstrating `pip-audit` — a tool that
checks your **installed dependencies** against databases of known vulnerabilities
(the [PyPI Advisory Database](https://github.com/pypa/advisory-database) and
[OSV](https://osv.dev)).

This is the counterpart to `bandit`: bandit statically analyzes *your own code*
for insecure patterns, while `pip-audit` checks whether *third-party packages*
you depend on have published CVEs.

## What's inside

A [uv](https://docs.astral.sh/uv/) project whose `pyproject.toml` pins old
package versions with known vulnerabilities:

| Package  | Pinned version | Example vulnerability                                      |
| -------- | -------------- | ---------------------------------------------------------- |
| requests | 2.28.0         | PYSEC-2023-74 — `Proxy-Authorization` header leak (CVE-2023-32681) |
| urllib3  | 1.26.5         | PYSEC-2023-192 — request body not stripped on 303 redirect |
| jinja2   | 3.1.2          | PYSEC-2026-1473 — HTML attribute injection via `xmlattr`   |
| certifi  | 2022.12.7      | PYSEC-2023-135 — removal of compromised e-Tugra root cert  |
| idna     | 3.4            | PYSEC-2024-60 — quadratic-complexity DoS in `idna.encode`  |

**Do not copy these pins into a real project.**

## Setup

```bash
cd pip_audit_ex
uv sync          # creates .venv and installs the pinned (vulnerable) versions
```

## Option A: audit the environment

`pip-audit` is included as a dev dependency, so it runs inside the project venv
and inspects every installed package:

```bash
uv run pip-audit
```

Expected output (abridged — ~20 findings across all 5 packages):

```
Found 21 known vulnerabilities in 5 packages
Name     Version   ID              Fix Versions
-------- --------- --------------- -------------
certifi  2022.12.7 PYSEC-2023-135  2023.7.22
idna     3.4       PYSEC-2024-60   3.7
jinja2   3.1.2     PYSEC-2026-1473 3.1.3
requests 2.28.0    PYSEC-2023-74   2.31.0
urllib3  1.26.5    PYSEC-2023-192  1.26.17,2.0.6
...
```

The exit code is non-zero when vulnerabilities are found, which is what makes
this usable as a CI gate.

## Option B: audit the lockfile (no install needed)

Export the uv lockfile to `requirements.txt` format and audit it directly.
`--no-deps` trusts the fully-pinned export instead of re-resolving, and
`--disable-pip` skips building a temporary virtualenv:

```bash
uv export --format requirements-txt --no-emit-project > requirements.txt
uvx pip-audit -r requirements.txt --no-deps --disable-pip
```

This is the better fit for CI: it audits exactly what the lockfile says without
installing anything, and `uvx` fetches `pip-audit` on the fly.

## Useful flags

```bash
uv run pip-audit --desc on       # include vulnerability descriptions
uv run pip-audit -f json         # machine-readable output
uv run pip-audit --fix           # upgrade vulnerable packages to fixed versions
                                 # (updates the venv only — pyproject.toml pins stay,
                                 #  so `uv sync` reverts it; fix real projects by
                                 #  bumping the constraint, e.g. `uv add "requests>=2.32.4"`)
```

## Fixing for real

Bump the constraints and re-lock:

```bash
uv add "requests>=2.32.4" "urllib3>=2.7.0" "jinja2>=3.1.6" "certifi>=2024.7.4" "idna>=3.15"
uv run pip-audit             # now reports: No known vulnerabilities found
```
