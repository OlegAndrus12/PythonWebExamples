from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None
    )
    db_user: str
    db_password: str
    db_name: str
    db_domain: str
    db_port: int
    secret_key: str

    @computed_field
    @property
    def DB_URL(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_domain}:{self.db_port}/{self.db_name}"

settings = Settings()
