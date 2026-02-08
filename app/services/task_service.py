"""Task service for business logic operations."""

import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models.task import Task


class TaskService:
    """Service class for task CRUD operations.

    All operations are scoped to a specific user to enforce isolation.
    """

    def __init__(self, session: Session, user_id: str):
        """Initialize the service with a database session and user ID.

        Args:
            session: SQLModel database session
            user_id: Authenticated user's ID (from JWT sub claim)
        """
        self.session = session
        self.user_id = user_id

    def list_tasks(self) -> list[Task]:
        """Get all tasks belonging to the authenticated user.

        Returns:
            List of Task objects owned by the user
        """
        statement = select(Task).where(Task.user_id == self.user_id)
        return list(self.session.exec(statement).all())

    def get_task(self, task_id: uuid.UUID) -> Task | None:
        """Get a specific task by ID if it belongs to the user.

        Args:
            task_id: UUID of the task to retrieve

        Returns:
            Task object if found and owned by user, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == self.user_id
        )
        return self.session.exec(statement).first()

    def create_task(self, title: str) -> Task:
        """Create a new task for the authenticated user.

        Args:
            title: Task description (1-255 characters)

        Returns:
            Newly created Task object
        """
        task = Task(
            user_id=self.user_id,
            title=title,
            is_completed=False,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update_task(self, task_id: uuid.UUID, title: str) -> Task | None:
        """Update a task's title if it belongs to the user.

        Args:
            task_id: UUID of the task to update
            title: New task title

        Returns:
            Updated Task object if found and owned, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.title = title
        task.updated_at = datetime.utcnow()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: uuid.UUID) -> bool:
        """Delete a task if it belongs to the user.

        Args:
            task_id: UUID of the task to delete

        Returns:
            True if deleted, False if not found or not owned
        """
        task = self.get_task(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def toggle_complete(self, task_id: uuid.UUID) -> Task | None:
        """Toggle the completion status of a task.

        Args:
            task_id: UUID of the task to toggle

        Returns:
            Updated Task object if found and owned, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
