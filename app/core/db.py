from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    pool_pre_ping=True,
    echo=settings.db_echo,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def commit_or_rollback(session: Session) -> None:
    """Commit ; en cas d'erreur la session est remise dans un état propre avant de propager."""
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
