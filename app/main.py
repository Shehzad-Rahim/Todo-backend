"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["*"],  # ✅ allowed because credentials are OFF
    allow_credentials=False,  # 🚨 MUST be False
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register API routers
# Tasks API - user identity comes from JWT token, not URL
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
