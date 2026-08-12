"""Демонстрація: модуль налаштувань як сінглтон.

Run: python3 main.py
"""

from __future__ import annotations

import dataclasses
import sys

import settings as settings_module
from settings import Settings, get_settings


def main() -> None:
    first = get_settings()
    second = get_settings()
    assert first is second

    assert "settings" in sys.modules
    assert sys.modules["settings"] is settings_module
    assert Settings.from_env() is not get_settings()

    try:
        get_settings().debug = True
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("expected FrozenInstanceError")

    get_settings.cache_clear()
    assert get_settings() is not first


if __name__ == "__main__":
    main()
