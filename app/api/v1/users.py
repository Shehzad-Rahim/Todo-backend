"""Protected user routes with authentication and authorization."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user_id, VerifiedUserId

# Router with authentication required for all routes
router = APIRouter(
    prefix="/users/{user_id}",
    tags=["users"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("/tasks")
async def list_user_tasks(verified_user: VerifiedUserId):
    """List all tasks for the authenticated user.

    Requires:
    - Valid JWT token
    - user_id in path must match JWT sub claim

    Returns 403 if user_id doesn't match authenticated user.
    """
    return {
        "user_id": verified_user,
        "tasks": [],  # Task CRUD will be implemented in separate spec
    }


@router.post("/tasks")
async def create_user_task(verified_user: VerifiedUserId, task: dict):
    """Create a new task for the authenticated user.

    Requires:
    - Valid JWT token
    - user_id in path must match JWT sub claim
    """
    return {
        "user_id": verified_user,
        "task": task,
        "message": "Task creation placeholder - will be implemented in task CRUD spec",
    }
