from fastapi import FastAPI
import uvicorn
from loguru import logger

from src.models.cameras import Camera
from src.config import settings
from src.db import db_helper
from src.api.router.users import router as users_router
from src.api.router.video import router as video_router
from src.api.router.cameras import router as camera_router


def lifespan(app: FastAPI):
    db_gen = db_helper.get_db()
    db = next(db_gen)
    cameras = db.query(Camera).all()
    logger.info(str(len(cameras)) + " cameras in DB")
    if not cameras:
        initial_cameras = [Camera() for i in range(7)]
        db.add_all(initial_cameras)
        db.commit()
        logger.info("Данные проинициализированы.")

    yield


app = FastAPI(
    title="GeoTime Local",
    description="Documentation for services provided by GeoTime Local",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.include_router(users_router)
app.include_router(video_router)
app.include_router(camera_router)
