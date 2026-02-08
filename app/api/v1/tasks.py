"""Task management REST API endpoints.

All routes derive user identity from the JWT token, NOT from URL parameters.
This ensures proper authorization - the user cannot access other users' tasks
by manipulating URL parameters.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.auth.dependencies import CurrentUserId
from app.core.database import get_session
from app.services.task_service import TaskService


# Request/Response models

class TaskCreate(BaseModel):
    """Request model for creating a task."""

    title: str = Field(min_length=1, max_length=255, description="Task description")


class TaskUpdate(BaseModel):
    """Request model for updating a task (partial update)."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated task description"
    )


# Router - NO user_id in path, user comes from token
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get("")
def list_tasks(
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """List all tasks for the authenticated user.

    User ID is extracted from the JWT token, not from URL.
    Returns a list of all tasks owned by the user.
    """
    service = TaskService(session, current_user)
    tasks = service.list_tasks()
    return {"tasks": tasks}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """Create a new task for the authenticated user.

    The task is automatically associated with the authenticated user's ID
    from the JWT token.
    """
    service = TaskService(session, current_user)
    task = service.create_task(task_data.title)
    return task


@router.get("/{task_id}")
def get_task(
    task_id: uuid.UUID,
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """Get a specific task by ID.

    Returns 404 if the task doesn't exist or doesn't belong to the user.
    """
    service = TaskService(session, current_user)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}")
def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """Update a task's title.

    Supports partial updates - only provided fields are updated.
    Returns 404 if the task doesn't exist or doesn't belong to the user.
    """
    if task_data.title is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    service = TaskService(session, current_user)
    task = service.update_task(task_id, task_data.title)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """Delete a task.

    Permanently removes the task from the database.
    Returns 404 if the task doesn't exist or doesn't belong to the user.
    """
    service = TaskService(session, current_user)
    if not service.delete_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch("/{task_id}/complete")
def toggle_complete(
    task_id: uuid.UUID,
    current_user: CurrentUserId,
    session: Session = Depends(get_session),
):
    """Toggle the completion status of a task.

    If the task is incomplete, it becomes complete.
    If the task is complete, it becomes incomplete.
    Returns 404 if the task doesn't exist or doesn't belong to the user.
    """
    service = TaskService(session, current_user)
    task = service.toggle_complete(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
