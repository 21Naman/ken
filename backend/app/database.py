from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.settings import Settings, get_settings


def create_database_engine(settings: Settings | None = None):
    settings = settings or get_settings()
    database_path = settings.database_path
    if database_path:
        database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    )


engine = create_database_engine()


def initialize_database(database_engine=None) -> None:
    active_engine = database_engine or engine
    SQLModel.metadata.create_all(active_engine)
    # SQLModel creates new tables but does not evolve existing local SQLite files.
    # Keep this one additive migration here so existing household memory gains the
    # field without requiring users to delete data/household.db.
    if active_engine.dialect.name == "sqlite":
        columns = {column["name"] for column in inspect(active_engine).get_columns("inventory_lots")}
        if "freshness" not in columns:
            with active_engine.begin() as connection:
                connection.execute(text("ALTER TABLE inventory_lots ADD COLUMN freshness VARCHAR(32) NOT NULL DEFAULT 'fresh'"))


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
