from pydantic import BaseModel


class CameraSchema(BaseModel):
    name: str
    rtsp_url: str


class UpdateCameraSchema(BaseModel):
    id: int
    name: str | None = None
    rtsp_url: str | None = None
