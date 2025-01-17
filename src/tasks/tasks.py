import subprocess
import os
from jinja2 import Template
from pathlib import Path
from time import time
from datetime import datetime, timedelta
from pm2 import PM2
from loguru import logger
from celery.schedules import crontab
from celery import Task

from src.tasks.celery import app as celery_app
from src.utils import update_config, create_new_config
from src.config import settings


class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} succeeded: {retval}")


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/1"), check_video_saving.s())
    sender.add_periodic_task(crontab(minute=5), check_video_for_five_with_delay.s())
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=1, month_of_year="*/3"),
        del_old_videos.s(),
    )


@celery_app.task()
def create_script(url, static_dir, object, camera):
    current_date_moscow = datetime.now().astimezone().strftime("%Y-%m-%d")
    current_hour = datetime.now().astimezone().strftime("%H")
    script_templates = """#!/bin/bash
    while :
    do
        base_filename="$(TZ='Europe/Moscow' date +'%Y-%m-%dT%H-%M-%S')"
        filename="{{ static_dir }}/${base_filename}.flv"

        ffmpeg -i '{{ url }}' \
        -t 300 -c:v copy -c:a copy -b:a 256k -reset_timestamps 1 "$filename"
    done
    """
    template = Template(script_templates).render(url=url, static_dir=static_dir)

    with open(f"load_{object}_{camera}.sh", "w") as f:
        f.write(template)


@celery_app.task()
def start_saving(object, camera):
    pm2 = PM2()
    project_dir = Path(__file__).resolve().parents[2]
    camera_script_path = project_dir / "geotime.config.js"

    script_name = f"load_{object}_{camera}"
    now = datetime.now()
    current_minute = now.minute
    current_second = now.second

    if current_minute != 0 and current_second != 0:
        update_config(camera_script_path, script_name)
        pm2.start(
            path=str(project_dir / f"load_{object}_{camera}.sh"), name=script_name
        )

        time_to_sleep = (60 - current_minute - 1) * 60 + (60 - current_second)
        time.sleep(time_to_sleep)

    update_config(camera_script_path, script_name)

    pm2.start(path=str(project_dir / f"load_{object}_{camera}.sh"), name=script_name)

    logger.info(f"Start saving with app name: {script_name}")


@celery_app.task()
def stop_saving_all() -> None:
    command = "pm2 stop all"
    subprocess.Popen(command, shell=True)
    logger.info("Stop saving")


@celery_app.task()
def stop_saving_single(object, camera) -> None:
    command = f"pm2 stop load_{object}_{camera}"
    subprocess.Popen(command, shell=True)
    logger.info(f"Stop saving {object} {camera}")


@celery_app.task()
def check_video_for_five_with_delay():
    check_video_for_five.apply_async(countdown=settings.CHECK_VIDEO_SAVING)


@celery_app.task()
def check_video_for_five():
    pm2 = PM2()
    processes = pm2.list()
    for process in processes:
        if process["name"].startswith("load_"):
            _, object, camera = process["name"].split("_")
            restart_saving_from_pm2.apply_async(
                (object, camera, process.pid, process.pm_id)
            )
            logger.info(f"Restarting {object} {camera} process successful")


@celery_app.task(base=MyTask, name="Рестарт записи с помощью pm2")
def restart_saving_from_pm2(object: str, camera: str, pid: int, pm_id: int) -> str:
    pm2 = PM2()
    project_dir = Path(__file__).resolve().parents[2]
    camera_script_path = project_dir / "geotime.config.js"
    script_name = f"load_{object}_{camera}"
    new_camera_script_path = project_dir / f"{script_name}.config.js"

    if not new_camera_script_path.exists():
        logger.info("Creating new config")
        create_new_config(camera_script_path, new_camera_script_path, script_name)
    logger.info(f"{pid=}{pm_id=}")
    logger.info(f"{script_name=}")
    pm2.restart(pm_id=pid, pid=pm_id, name=script_name)

    return f"Start saving with app name: {script_name}"


@celery_app.task(name="Проверка состояния записей камер")
def check_video_saving():
    pm2 = PM2()
    processes = pm2.list()

    for process in processes:
        if process.status != "online" and process.name.startswith("load_"):
            _, object, camera = process.name.split("_")
            start_saving_from_pm2(object, camera)


@celery_app.task(base=MyTask, name="Запуск записи с помощью pm2")
def start_saving_from_pm2(object: str, camera: str) -> str:
    pm2 = PM2()
    project_dir = Path(__file__).resolve().parents[2]
    camera_script_path = project_dir / "geotime.config.js"
    script_name = f"load_{object}_{camera}"
    new_camera_script_path = project_dir / f"{script_name}.config.js"

    if not new_camera_script_path.exists():
        logger.info("Create new config file")
        create_new_config(camera_script_path, new_camera_script_path, script_name)
    logger.info(f'{str(project_dir / f"load_{object}_{camera}.sh")=}')
    pm2.start(path=str(project_dir / f"load_{object}_{camera}.sh"), name=script_name)

    return f"Start saving with app name: {script_name}"


@celery_app.task(name="Удаление старых видеозаписей (>45 дней)")
def del_old_videos():
    video_dir = Path.cwd().parents[2] / "mnt" / "acqdata"
    threshold_date = datetime.now() - timedelta(days=45)

    for video_file in video_dir.glob("**/*.mp4"):
        object_dir, camera_dir, file_name = video_file.relative_to(video_dir).parts
        date_str = file_name.split(".")[0]
        formatted_date = datetime.strptime(date_str, "%Y-%m-%dT%H-%M-%S")

        if formatted_date < threshold_date:
            os.remove(video_file)
            logger.info(f"Deleting old video file: {video_file}")
