from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from src.core.schemas.cameras import UpdateCameraSchema
from src.utils import read_json, write_json


router = APIRouter()


@router.post("/update_camera/{camera_id}")
def update_camera(camera_id: str, camera_data: UpdateCameraSchema):
    data = read_json()
    data[camera_id] = camera_data.model_dump()
    write_json(data)
    return {"message": f"Camera {camera_id} updated successfully", "data": data}


# Получить данные по одной камере
@router.get("/cameras/{camera_id}")
async def get_camera(camera_id: str):
    data = read_json()
    if camera_id not in data:
        raise HTTPException(status_code=404, detail="Camera not found")
    return data[camera_id]
