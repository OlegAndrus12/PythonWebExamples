from __future__ import annotations

from typing import Self

from dotenv import dotenv_values


class Settings:
    _instance: Settings | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        env = dotenv_values(".env")
        self.database_url = env["DATABASE_URL"]
        self.secret_key = env["SECRET_KEY"]
        self.debug = env.get("DEBUG", "false").lower() in {"1", "true", "yes"}


if __name__ == "__main__":
    a = Settings()
    b = Settings()
    print(a is b, a.database_url, a.debug)
