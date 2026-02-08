"""Database configuration and session management for Neon PostgreSQL."""

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create engine with NullPool for Neon serverless compatibility
# NullPool disables client-side connection pooling (Neon handles pooling server-side)
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=False,
)


def get_session():
    """Yield a database session for dependency injection.

    Creates a new session for each request and ensures proper cleanup.
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create all database tables defined in SQLModel metadata.

    Should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)
