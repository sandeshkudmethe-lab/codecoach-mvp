"""
SQLAlchemy engine/session setup. SQLite for the MVP (zero external
infra), but swapping DATABASE_URL to Postgres later needs no code
changes elsewhere since everything goes through get_db().
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..core.config import settings

# check_same_thread=False is only needed for SQLite (it's single-threaded
# by default); harmless to gate it behind a URL check for future Postgres use.
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
