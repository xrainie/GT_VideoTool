from sqlalchemy.orm import Session
from src.core.schemas.cameras import UpdateCameraSchema


class CameraService:
    def __init__(self, db: Session):
        self.db = db

    def update_camera(self, id: int, name: str, rtsp_url: str) -> Camera:
        camera = self.db.query(Camera).filter(Camera.id == id).first()
        camera.name = name
        camera.rtps_url = rtsp_url
        self.db.commit()
        return camera
