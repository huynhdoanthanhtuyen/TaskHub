import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.projects import (
    router as project_router,
)
from app.api.v1.endpoints.projects import (
    workspace_projects_router,
)
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.workspaces import router as workspace_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    RelatedResourceNotFoundError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TaskHub API is starting ...")
    yield
    logger.info("TaskHub API is shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=exc.headers,
    )


@app.exception_handler(RelatedResourceNotFoundError)
async def related_resource_not_found_handler(
    request: Request,
    exc: RelatedResourceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.get("/")
async def root():
    return {"message": "Welcome to TaskHub API"}


app.include_router(
    tasks_router,
    prefix="/api/v1/tasks",
    tags=["Tasks"],
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(workspace_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

app.include_router(
    workspace_projects_router,
    prefix="/api/v1",
)

app.include_router(
    project_router,
    prefix="/api/v1",
)
