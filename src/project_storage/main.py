from fastapi import FastAPI, status

from project_storage.api.v1.router import router
from project_storage.api.v1.users import router as users_router
from project_storage.api.v1.projects import router as projects_router
from project_storage.core.config import settings
from project_storage.core.logging import setup_logging


setup_logging()


app = FastAPI(
    title=settings.APP_NAME,
    root_path=settings.API_PATH,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": 'Unauthorized'}
    }
)

app.include_router(router)
app.include_router(users_router, prefix="/users")
app.include_router(projects_router, prefix="/projects")
