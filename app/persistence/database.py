from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str):
        if url.startswith("sqlite:///"):
            database_path = url.replace("sqlite:///", "", 1)

            Path(database_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self.engine = create_engine(
            url,
            future=True,
        )

        self.Session = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)
