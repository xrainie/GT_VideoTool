from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from celery import chain

from src.core.schemas.video import CameraDataSchema
from src.tasks.tasks import (
    create_script,
    start_saving,
    stop_saving_all,
    stop_saving_single,
)


router = APIRouter(tags=["Video"])


@router.post("/save_video")
def save_video(data: CameraDataSchema):
    static_dir = (
        Path.cwd().parents[3]
        / "data"
        / "video_sync_daemon"
        / "contractors_video_storage"
        / data.contractor
        / data.object
    )

    # TODO Сделать преобразование rtsp ссылки в ссылку, ретранслируемую mediamtx
    # camera_url = data.url ...

    if not static_dir.exists():
        try:
            static_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Не удалось создать директорию: {str(e)}"
            )

    task_chain = chain(
        create_script.s(
            str(data.url), str(static_dir), str(data.object), str(data.name)
        ),
        start_saving.s(data.object, data.name),
    )
    task_chain.delay()

    return JSONResponse(
        content={"message": "Script created successfully and start saving"}
    )


@router.get("/stop_saving")
def stop_save_all():
    stop_saving_all.delay()
    return JSONResponse(content={"message": "Script stopped successfully"})


@router.get("/stop_saving/{object}/{camera}")
def single_stop_save(object: str, camera: str):
    stop_saving_single.delay(object, camera)
    return JSONResponse(
        content={"message": f"Script load_{object}_{camera} stopped successfully"}
    )
