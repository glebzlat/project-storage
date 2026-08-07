from fastapi import FastAPI

from .api.v1.router import router
from project_storage.api.v1.users import router as users_router
from .core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    root_path=settings.API_PATH,
)
app.include_router(router)
app.include_router(users_router, prefix="/users")
