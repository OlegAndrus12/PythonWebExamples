"""Singleton — exactly one instance of something, for the whole process.

Problem: settings, a connection pool and a logger must be created once and
         shared. Creating a second one costs money or corrupts state.

Before:  a `__new__` trick that returns the same object forever. It works, and
         then it leaks between tests, resists copying, and races under threads.

After:   in Python the module system already is a singleton — a module body runs
         once per process. A module-level object, or a cached factory function,
         is all you need.

Already seen it in: `from django.conf import settings`, logging.getLogger(name),
         and in this repo zoo_api/src/services/auth.py — `auth_service =
         AuthService()` at module level.

Cost:    a singleton is global mutable state. Order of initialisation becomes
         load-bearing, tests bleed into each other, and nothing can be swapped
         out. `@lru_cache` at least gives you `cache_clear()` as a test seam.

Run:     python3 01_singleton.py
"""

from __future__ import annotations

import copy
import functools
import threading
from dataclasses import dataclass
from typing import Self

# --------------------------------------------------------------------------
# The pattern, written the way the GoF book describes it
# --------------------------------------------------------------------------


class SettingsSingleton:
    _instance: SettingsSingleton | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.debug = False  # type: ignore[attr-defined]
        return cls._instance


# --------------------------------------------------------------------------
# The same guarantee, in Python
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str = "postgresql://localhost/app"
    debug: bool = False


@functools.lru_cache()
def get_settings() -> Settings:
    """One instance per process — and cache_clear() resets it for a test."""
    return Settings()


def main() -> None:
    print("The __new__ trick\n")
    a, b = SettingsSingleton(), SettingsSingleton()
    print(f"  same object: {a is b}")

    a.debug = True  # type: ignore[attr-defined]
    print(f"  test A set debug=True -> test B reads debug="
          f"{SettingsSingleton().debug}")  # type: ignore[attr-defined]
    print(f"  copy.deepcopy(a) is a: {copy.deepcopy(a) is a}  <-- no clean copy")
    print("  __new__ intercepts construction, so nothing can escape it.")

    print("\n  ...and the check is not atomic:")
    seen: set[int] = set()
    barrier = threading.Barrier(8)

    class Racy:
        _instance: Racy | None = None

        def __new__(cls) -> Self:
            if cls._instance is None:
                barrier.wait()          # make the interleaving visible
                cls._instance = super().__new__(cls)
            return cls._instance

    threads = [threading.Thread(target=lambda: seen.add(id(Racy())))
               for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print(f"  8 threads produced {len(seen)} distinct 'singletons'")

    print("\nThe Python version\n")
    print(f"  same object: {get_settings() is get_settings()}")
    get_settings.cache_clear()
    print(f"  after cache_clear(), fresh instance debug={get_settings().debug}")
    print("  A module body runs once. That is the whole mechanism.")


if __name__ == "__main__":
    main()
