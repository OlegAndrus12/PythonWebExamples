#!/usr/bin/env python3
"""Benchmark pip, Poetry and uv on the same two dependency sets.

Standard library only — the point of this folder is that you can run it with the
`python3` you already have, without installing anything first.

    python3 bench.py --quick      # the small set only (~1 min)
    python3 bench.py              # the full matrix, writes results.json

One run per cell: the numbers here are one measurement, not a statistic. The
spread between runs is small for `lock` and `install-warm`, and large for
`install-cold`, where the network dominates — run it again if a cold number looks
surprising.

What is measured, for every tool:

    lock           resolve the declared ranges into a lock file
    install-cold   create a venv and materialise the lock file, empty cache
    install-warm   the same, with the package cache already populated

Rules the runner enforces so the numbers mean something:

* Package caches are *redirected*, never cleared. Every subprocess gets
  PIP_CACHE_DIR / POETRY_CACHE_DIR / UV_CACHE_DIR pointing inside a temporary
  directory, so a "cold cache" run is a fresh empty temp cache and your real
  ~/.cache/uv and ~/Library/Caches/pypoetry are never touched.
* All three tools build their environment with the *same* interpreter, found
  once via `uv python find`, and none of them is allowed to download a Python.
* Every timed command, its exit code and its raw duration end up in results.json.
  Nothing is rounded away or hidden.
* Only the command under test is timed. Generating the lock file that the
  install scenarios consume and warming a cache are preparation steps, run
  outside the timer.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The interpreter every measured environment is built with. 3.12 is what
# 02_pipenv / 03_poetry / 04_uv all declare.
PYTHON_VERSION = "3.12"
REQUIRES_PYTHON = ">=3.12,<3.13"

# Per-command ceiling. A cold install downloads every wheel in the set; anything
# past this is a hang, not a slow network.
TIMEOUT = 1800

TOOLS = ("pip", "poetry", "uv")

SCENARIOS = ("lock", "install-cold", "install-warm")


# --------------------------------------------------------------------------- #
# Dependency sets
# --------------------------------------------------------------------------- #
# Direct dependencies only, as ranges — exactly how you would write them by
# hand. The resolver's job is to turn these into the full closure, and how long
# that takes is most of what this benchmark shows.

DEPSETS = {
    "statusboard": {
        "label": "statusboard",
        "note": "the app from 02_pipenv / 03_poetry / 04_uv",
        # Copied from 04_uv/pyproject.toml.
        "runtime": [
            "flask>=3.1.0,<4.0.0",
            "requests>=2.32.3,<3.0.0",
        ],
        "dev": [
            "bandit>=1.9.4",
            "pre-commit>=4.6.1",
            "pytest>=9.1.1",
            "ruff>=0.14.0",
        ],
    },
    "zoo_api": {
        "label": "zoo_api-sized",
        "note": "the runtime dependencies of zoo_api plus a normal dev toolchain",
        # zoo_api/pyproject.toml, trimmed to keep the run quick: no pandas and no
        # psycopg2 — the first is a large download and the second wants a C
        # compiler, and neither tells you anything about a resolver.
        "runtime": [
            "fastapi[standard]>=0.116.1,<0.117.0",
            "sqlalchemy>=2.0.43,<3.0.0",
            "pydantic-settings>=2.10.1,<3.0.0",
            "alembic>=1.16.5,<2.0.0",
            "passlib>=1.7.4,<2.0.0",
            "bcrypt>=4.3.0,<5.0.0",
            "python-jose>=3.5.0,<4.0.0",
            "redis>=6.4.0,<7.0.0",
            "celery>=5.4.0,<6.0.0",
        ],
        "dev": [
            "pytest>=8.3.0",
            "pytest-asyncio>=0.24.0",
            "ruff>=0.14.0",
            "mypy>=1.11.0",
        ],
    },
}


# --------------------------------------------------------------------------- #
# Process plumbing
# --------------------------------------------------------------------------- #


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def which_or_die(name: str) -> str:
    found = shutil.which(name)
    if not found:
        die(f"{name} is not on PATH — this benchmark needs pip, poetry and uv all present")
    return found


def find_python() -> str:
    """The interpreter every measured venv is built from."""
    proc = subprocess.run(
        ["uv", "python", "find", PYTHON_VERSION],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        die(
            f"no Python {PYTHON_VERSION} available.\n"
            f"       install one with: uv python install {PYTHON_VERSION}"
        )
    return proc.stdout.strip()


def tool_env(cache_root: Path, python: str, tmp_root: Path) -> dict[str, str]:
    """Environment for every measured subprocess.

    The three cache variables are the safety mechanism: they must resolve inside
    the run's temporary directory, so that no run can read or evict anything
    from the caches the user actually depends on.
    """
    env = os.environ.copy()

    # An activated venv in the parent shell would leak into pip and poetry.
    for leaky in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "CONDA_PREFIX"):
        env.pop(leaky, None)

    # Poetry picks the active interpreter off PATH (virtualenvs.use-poetry-python
    # is false by default), so this is how all three tools end up agreeing.
    env["PATH"] = f"{Path(python).parent}{os.pathsep}{env['PATH']}"

    caches = {
        "PIP_CACHE_DIR": cache_root / "pip",
        "POETRY_CACHE_DIR": cache_root / "poetry",
        "UV_CACHE_DIR": cache_root / "uv",
    }
    for var, path in caches.items():
        resolved = path.resolve()
        if tmp_root.resolve() not in resolved.parents and resolved != tmp_root.resolve():
            die(f"refusing to run: {var} would point outside the temp dir ({resolved})")
        path.mkdir(parents=True, exist_ok=True)
        env[var] = str(path)

    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env["POETRY_NO_INTERACTION"] = "1"
    env["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"
    env["POETRY_VIRTUALENVS_CREATE"] = "true"
    env["POETRY_VIRTUALENVS_USE_POETRY_PYTHON"] = "false"
    env["UV_NO_PROGRESS"] = "1"
    env["UV_PYTHON_DOWNLOADS"] = "never"
    return env


def run(cmd: list[str], cwd: Path, env: dict[str, str], *, check: bool = True) -> dict:
    """Run one command, return its wall-clock duration and outcome."""
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )
    seconds = time.perf_counter() - start
    step = {
        "cmd": [Path(cmd[0]).name, *cmd[1:]],
        "seconds": round(seconds, 4),
        "returncode": proc.returncode,
    }
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-12:]
        step["output_tail"] = tail
        if check:
            print("\n".join(f"    | {line}" for line in tail), file=sys.stderr)
            die(f"{' '.join(step['cmd'])} exited {proc.returncode} in {cwd}")
    return step


# --------------------------------------------------------------------------- #
# Manifests
# --------------------------------------------------------------------------- #


def write_manifest(project: Path, tool: str, depset: dict) -> None:
    """Write one dependency set in the manifest format the tool expects.

    Same packages, same ranges, three syntaxes — which is the other half of what
    these folders teach.
    """
    project.mkdir(parents=True, exist_ok=True)
    runtime, dev = depset["runtime"], depset["dev"]

    if tool == "pip":
        # requirements.in holds the *ranges*; pip-compile turns it into a pinned
        # requirements.txt. pip itself has neither file format nor a lock step —
        # that is the whole point of the pip row below.
        lines = ["# direct dependencies, unpinned — the input to pip-compile", *runtime, "", *dev]
        (project / "requirements.in").write_text("\n".join(lines) + "\n")
        return

    if tool == "poetry":
        deps = "\n".join(f'    "{spec}",' for spec in runtime)
        dev_deps = "\n".join(f'{name_of(spec)} = "{caret_of(spec)}"' for spec in dev)
        (project / "pyproject.toml").write_text(
            "[project]\n"
            'name = "bench"\n'
            'version = "0.1.0"\n'
            f'requires-python = "{REQUIRES_PYTHON}"\n'
            f"dependencies = [\n{deps}\n]\n"
            "\n"
            "[tool.poetry]\n"
            "package-mode = false\n"
            "\n"
            "[tool.poetry.group.dev.dependencies]\n"
            f"{dev_deps}\n"
        )
        return

    if tool == "uv":
        deps = "\n".join(f'    "{spec}",' for spec in runtime)
        dev_deps = "\n".join(f'    "{spec}",' for spec in dev)
        (project / "pyproject.toml").write_text(
            "[project]\n"
            'name = "bench"\n'
            'version = "0.1.0"\n'
            f'requires-python = "{REQUIRES_PYTHON}"\n'
            f"dependencies = [\n{deps}\n]\n"
            "\n"
            "[dependency-groups]\n"
            f"dev = [\n{dev_deps}\n]\n"
        )
        return

    raise AssertionError(tool)


def name_of(spec: str) -> str:
    """`pytest>=9.1.1` -> `pytest`."""
    for sep in (">=", "<=", "==", "~=", ">", "<", "["):
        spec = spec.split(sep)[0]
    return spec.strip()


def caret_of(spec: str) -> str:
    """`pytest>=9.1.1` -> `^9.1.1`, Poetry's equivalent of the same range."""
    _, _, rest = spec.partition(">=")
    return f"^{rest.split(',')[0].strip()}" if rest else "*"


# --------------------------------------------------------------------------- #
# Commands under test
# --------------------------------------------------------------------------- #


def venv_python(project: Path) -> Path:
    return project / ".venv" / "bin" / "python"


def commands(tool: str, project: Path, python: str, pip_compile: Path) -> dict[str, list[list[str]]]:
    """The timed command(s) per scenario, for one tool."""
    if tool == "pip":
        return {
            # pip cannot lock. pip-compile is pip-tools, a separate project, and
            # the closest thing the pip world has to `poetry lock`.
            "lock": [[str(pip_compile), "requirements.in", "-o", "requirements.txt", "--quiet"]],
            # poetry install and uv sync both create the environment, so pip's
            # venv creation is timed alongside its install.
            "install": [
                [python, "-m", "venv", ".venv"],
                [str(venv_python(project)), "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            ],
        }
    if tool == "poetry":
        poetry = which_or_die("poetry")
        return {
            "lock": [[poetry, "lock", "--regenerate", "--no-ansi"]],
            "install": [[poetry, "install", "--no-ansi"]],
        }
    if tool == "uv":
        uv = which_or_die("uv")
        return {
            "lock": [[uv, "lock"]],
            "install": [[uv, "sync", "-p", python]],
        }
    raise AssertionError(tool)


def lock_files(tool: str) -> tuple[str, ...]:
    return {
        "pip": ("requirements.txt",),
        "poetry": ("poetry.lock",),
        "uv": ("uv.lock",),
    }[tool]


def installed_count(project: Path) -> int:
    """How many distributions the install actually put in the venv."""
    site = project / ".venv" / "lib" / f"python{PYTHON_VERSION}" / "site-packages"
    return len(list(site.glob("*.dist-info"))) if site.is_dir() else 0


# --------------------------------------------------------------------------- #
# The measurement loop
# --------------------------------------------------------------------------- #


class Bench:
    def __init__(self, tmp_root: Path, python: str) -> None:
        self.tmp = tmp_root
        self.python = python
        self.counter = 0
        self.pip_compile = self._install_pip_tools()

    def _install_pip_tools(self) -> Path:
        """pip-compile lives in its own throwaway venv, never in the user's tools."""
        venv = self.tmp / "pip-tools"
        env = tool_env(self.tmp / "cache-prep", self.python, self.tmp)
        print("preparing pip-tools (for pip's lock row)")
        run([self.python, "-m", "venv", str(venv)], cwd=self.tmp, env=env)
        run(
            [str(venv / "bin" / "python"), "-m", "pip", "install", "-q", "pip-tools"],
            cwd=self.tmp,
            env=env,
        )
        return venv / "bin" / "pip-compile"

    def fresh_project(self, tag: str) -> Path:
        self.counter += 1
        project = self.tmp / "work" / f"{self.counter:03d}-{tag}"
        project.mkdir(parents=True)
        return project

    def cache(self, tag: str) -> Path:
        return self.tmp / "cache" / tag

    # -- preparation -------------------------------------------------------- #

    def prepare(self, tool: str, set_name: str, depset: dict) -> Path:
        """Build the template every measurement for this cell is copied from.

        The template holds the manifest *and* a lock file generated with a warm
        cache, so the install scenarios start from the same place for all three
        tools. None of this is timed.
        """
        template = self.tmp / "templates" / f"{set_name}-{tool}"
        if template.exists():
            return template

        warm = self.cache(f"{set_name}-warm")
        env = tool_env(warm, self.python, self.tmp)

        scratch = self.fresh_project(f"prep-{set_name}-{tool}")
        write_manifest(scratch, tool, depset)
        cmds = commands(tool, scratch, self.python, self.pip_compile)

        print(f"preparing {set_name}/{tool}: lock + cache warm-up")
        for cmd in cmds["lock"]:
            run(cmd, cwd=scratch, env=env)
        # Warming the cache means actually downloading everything once.
        for cmd in cmds["install"]:
            run(cmd, cwd=scratch, env=env)

        template.mkdir(parents=True)
        write_manifest(template, tool, depset)
        for name in lock_files(tool):
            shutil.copy2(scratch / name, template / name)
        shutil.rmtree(scratch, ignore_errors=True)
        return template

    def project_from(self, template: Path, tag: str) -> Path:
        project = self.fresh_project(tag)
        shutil.rmtree(project)
        shutil.copytree(template, project)
        return project

    # -- one measurement ---------------------------------------------------- #

    def measure(self, tool: str, set_name: str, scenario: str, template: Path) -> dict:
        cold = scenario == "install-cold"
        cache = self.cache(f"{set_name}-cold-{tool}") if cold else self.cache(f"{set_name}-warm")
        env = tool_env(cache, self.python, self.tmp)

        project = self.project_from(template, f"{set_name}-{tool}-{scenario}")
        # commands() bakes in absolute .venv paths, so it is built per copy.
        cmds = commands(tool, project, self.python, self.pip_compile)

        if scenario == "lock":
            for name in lock_files(tool):
                (project / name).unlink(missing_ok=True)
            timed = cmds["lock"]
        else:
            timed = cmds["install"]

        steps = [run(cmd, cwd=project, env=env) for cmd in timed]
        result = {
            "seconds": round(sum(step["seconds"] for step in steps), 4),
            "steps": steps,
        }
        if scenario != "lock":
            result["installed"] = installed_count(project)
        else:
            result["lock_bytes"] = sum(
                (project / name).stat().st_size for name in lock_files(tool)
            )
        shutil.rmtree(project, ignore_errors=True)
        if cold:
            shutil.rmtree(cache, ignore_errors=True)
        return result


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def tool_versions() -> dict[str, str]:
    def first_line(cmd: list[str]) -> str:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return (proc.stdout or proc.stderr).strip().splitlines()[0] if proc.returncode == 0 else "?"

    return {
        "poetry": first_line(["poetry", "--version"]),
        "uv": first_line(["uv", "--version"]),
    }


def machine_block(python: str) -> dict:
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "python": python,
        "python_version": subprocess.run(
            [python, "-V"], capture_output=True, text=True
        ).stdout.strip(),
        "tools": tool_versions(),
        # No wall-clock timestamp is invented here; the file records what ran,
        # and `git log` records when.
    }


def print_table(results: dict, sets: list[str], scenarios: list[str]) -> None:
    for set_name in sets:
        print(f"\n{set_name}")
        print(f"  {'':10}" + "".join(f"{s:>16}" for s in scenarios))
        for tool in TOOLS:
            row = f"  {tool:10}"
            for scenario in scenarios:
                cell = results.get(set_name, {}).get(scenario, {}).get(tool)
                row += f"{'—':>16}" if cell is None else f"{cell['seconds']:>13.2f} s"
            print(row)


# --------------------------------------------------------------------------- #


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="statusboard set only")
    parser.add_argument("--set", action="append", choices=list(DEPSETS), dest="sets")
    parser.add_argument("--scenario", action="append", choices=list(SCENARIOS), dest="scenarios")
    parser.add_argument("--tool", action="append", choices=list(TOOLS), dest="tools")
    parser.add_argument("--out", type=Path, default=HERE / "results.json")
    parser.add_argument("--keep-tmp", action="store_true", help="do not delete the work directory")
    args = parser.parse_args()

    sets = args.sets or list(DEPSETS)
    scenarios = args.scenarios or list(SCENARIOS)
    tools = args.tools or list(TOOLS)
    if args.quick:
        sets = ["statusboard"]

    which_or_die("poetry")
    which_or_die("uv")
    python = find_python()

    tmp_root = Path(tempfile.mkdtemp(prefix="pkgbench-"))
    print(f"python      {python}")
    print(f"work dir    {tmp_root}")
    print(f"matrix      {len(tools)} tools x {len(scenarios)} scenarios x {len(sets)} sets, one run each")
    print("caches are redirected into the work dir; your real caches are untouched\n")

    results: dict[str, dict[str, dict[str, dict]]] = {}
    try:
        bench = Bench(tmp_root, python)
        for set_name in sets:
            depset = DEPSETS[set_name]
            results[set_name] = {}
            templates = {tool: bench.prepare(tool, set_name, depset) for tool in tools}
            for scenario in scenarios:
                results[set_name][scenario] = {}
                for tool in tools:
                    print(f"{set_name:12} {scenario:13} {tool:7} ", end="", flush=True)
                    cell = bench.measure(tool, set_name, scenario, templates[tool])
                    results[set_name][scenario][tool] = cell
                    print(f"{cell['seconds']:.2f}s")
    finally:
        if args.keep_tmp:
            print(f"\nwork dir kept at {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)

    payload = {
        "machine": machine_block(python),
        "config": {
            "python_version": PYTHON_VERSION,
            "requires_python": REQUIRES_PYTHON,
            "sets": {
                name: {
                    "label": DEPSETS[name]["label"],
                    "note": DEPSETS[name]["note"],
                    "direct": len(DEPSETS[name]["runtime"]) + len(DEPSETS[name]["dev"]),
                    "runtime": DEPSETS[name]["runtime"],
                    "dev": DEPSETS[name]["dev"],
                }
                for name in sets
            },
            "scenarios": scenarios,
            "tools": tools,
        },
        "results": results,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print_table(results, sets, scenarios)
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
