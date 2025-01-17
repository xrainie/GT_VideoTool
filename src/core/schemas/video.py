from pydantic import BaseModel


class CameraDataSchema(BaseModel):
    url: str
    name: str
    object: str
    contractor: str
