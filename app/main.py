from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import tasks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todo-hive-pearl.vercel.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}
