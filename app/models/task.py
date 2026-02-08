"""Task model for todo items."""

import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """A todo task belonging to a user.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Owner's user ID (from JWT sub claim), indexed for query performance
        title: Task description (1-255 characters)
        is_completed: Whether the task is done
        created_at: When the task was created
        updated_at: When the task was last modified
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=255)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
