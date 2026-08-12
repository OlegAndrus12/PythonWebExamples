"""Налаштування застосунку — сінглтон без патерна Singleton.

Тіло модуля виконується один раз на процес. Тому будь-який об'єкт, створений
на рівні модуля, вже є сінглтоном — жодного `__new__`, метакласів чи блокувань.

Читати `.env` на кожен виклик було б повільно й непередбачувано (значення
могло б змінитися посеред запиту), тому `get_settings()` кешується.
`@lru_cache` дає те саме, що й класичний сінглтон, плюс `cache_clear()` —
шов, через який тест підміняє конфігурацію.

Run: python3 main.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import dotenv_values

# ---------------------------------------------------------------------------
# Значення
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Settings:
    """Звичайний клас — жодного `__new__`, жодного метакласу.

    Клас нічого не знає про те, що він сінглтон, і не заважає створити другий
    екземпляр. За "рівно один" відповідає модуль, а не клас, — і саме тому цей
    код тестується, а `__new__`-версія ні.

    `slots=True` не має стосунку до сінглтона: він просто не дає створити
    атрибут з друкарською помилкою (`settings.debgu = True` впаде).

    `frozen=True` — те, чого `slots` не дає: спроба присвоїти вже оголошене
    поле (`settings.debug = True`) кидає `FrozenInstanceError`. Глобальний
    об'єкт, який ніхто не може мутувати, — це рівно та проблема класичного
    Singleton, яку тут закрито в один рядок.
    """

    database_url: str
    secret_key: str
    debug: bool = False
    allowed_hosts: tuple[str, ...] = field(default_factory=lambda: ("localhost",))

    def __repr__(self) -> str:
        return (
            f"Settings(database_url={self.database_url!r}, "
            f"secret_key='***', debug={self.debug}, "
            f"allowed_hosts={self.allowed_hosts!r})"
        )

    @classmethod
    def from_env(cls) -> Settings:
        """Зібрати налаштування з `.env`."""
        env = dotenv_values(".env")

        debug = env.get("DEBUG", "false").lower() in {"1", "true", "yes"}
        secret_key = env.get("SECRET_KEY", "")

        if not debug and not secret_key:
            raise RuntimeError("SECRET_KEY is required when DEBUG is off")

        return cls(
            database_url=env.get("DATABASE_URL", "postgresql://localhost/app"),
            secret_key=secret_key or "dev-only-insecure-key",
            debug=debug,
            allowed_hosts=tuple(
                host.strip()
                for host in env.get("ALLOWED_HOSTS", "localhost").split(",")
                if host.strip()
            ),
        )


# ---------------------------------------------------------------------------
# Доступ
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Один екземпляр на процес.

    Створюється не під час імпорту, а при першому виклику — тому імпорт модуля
    не падає через відсутній `.env`, і тест може підготувати конфігурацію
    перед тим, як вона знадобиться.
    """
    return Settings.from_env()
