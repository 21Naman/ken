from collections.abc import Generator

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
    SQLModel.metadata.create_all(database_engine or engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
