from pathlib import Path

import yaml
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    url: str


class ZalktisConfig(BaseModel):
    output_directory: Path


class AccountingConfig(BaseModel):
    provider: str
    zalktis: ZalktisConfig


class ApplicationConfig(BaseModel):
    environment: str
    timezone: str


class Settings(BaseModel):
    application: ApplicationConfig
    database: DatabaseConfig
    accounting: AccountingConfig


def load_config(
    path: str | Path,
) -> Settings:

    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(file)

    return Settings.model_validate(data)
