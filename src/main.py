from fastapi import FastAPI

from src.config import settings
from src.api.router.users import router as users_router
from src.api.router.video import router as video_router
from src.api.router.cameras import router as camera_router

app = FastAPI(
    title="GeoTime Local",
    description="Documentation for services provided by GeoTime Local",
    version=settings.VERSION,
)

app.include_router(users_router)
app.include_router(video_router)
app.include_router(camera_router)
