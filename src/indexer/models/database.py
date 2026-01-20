from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import StaticPool
from indexer.config import settings

# Create engine
# Note: StaticPool is used here to support SQLite in-memory testing correctly.
# In a production Postgres setup, SQLAlchemy will use its default QueuePool.
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool if settings.database_url.startswith("sqlite") else None,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)