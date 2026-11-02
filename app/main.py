from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints.tasks import router as tasks_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
  print("TaskHub API is starting ...")
  yield
  print("TaskHub API is shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

@app.get("/")
async def root():
  return {"message": "Welcome to TaskHub API"}

app.include_router(
    tasks_router,
    prefix="/api/v1/tasks",
    tags=["Tasks"],
)