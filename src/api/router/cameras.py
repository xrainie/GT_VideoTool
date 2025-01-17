from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.schemas.cameras import UpdateCameraSchema
from src.models.cameras import Camera
from src.services.cameras import CameraService
from src.db import db_helper

router = APIRouter()


@router.post("/update_camera")
def update_camera(data: UpdateCameraSchema, db: Session = Depends(db_helper.get_db)):
    camera_service = CameraService(db=db)
    camera = camera_service.update_camera(data.id, data.name, data.rtsp_url)
    return camera
