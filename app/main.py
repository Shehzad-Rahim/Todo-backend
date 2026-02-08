# """FastAPI application entry point."""

# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi import Request
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.v1 import tasks
# from app.core.database import create_db_and_tables


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan handler for startup/shutdown events."""
#     # Startup: Create database tables
#     create_db_and_tables()
#     yield
#     # Shutdown: Nothing to clean up


# app = FastAPI(
#     title="Todo API",
#     description="Fullstack Todo Application API with JWT authentication",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# @app.middleware("http")
# async def allow_options_without_auth(request: Request, call_next):
#     if request.method == "OPTIONS":
#         return await call_next(request)
#     return await call_next(request)

# # CORS configuration for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://todo-hive-pearl.vercel.app", "http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/api/v1/tasks")
# async def get_tasks():
#     return {"tasks": []}

# # Register API routers
# # Tasks API - user identity comes from JWT token, not URL
# app.include_router(tasks.router, prefix="/api/v1")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint."""
#     return {"status": "healthy"}


"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import tasks
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Nothing to clean up


app = FastAPI(
    title="Todo API",
    description="Fullstack Todo Application API with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todo-hive-pearl.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods including OPTIONS
    allow_headers=["*"],  # allow all headers including Authorization
)

# Handle preflight OPTIONS requests globally (optional but recommended)
@app.options("/{full_path:path}")
async def preflight_handler():
    return JSONResponse(status_code=204, content={})

# Example GET route (optional, you can remove if tasks.router handles it)
@app.get("/api/v1/tasks")
async def get_tasks():
    return {"tasks": []}

# Register API routers
app.include_router(tasks.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
