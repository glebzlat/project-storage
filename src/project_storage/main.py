from fastapi import FastAPI

from .api.v1.router import router
from .core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    root_path=settings.API_PATH,
)
app.include_router(router)
