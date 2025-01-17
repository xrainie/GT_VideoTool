import asyncio
import logging

from asyncio import Task
from typing import Optional, Any, Dict, List
from subprocess import Popen

from .db import DBI
from .ffmpeg import make_restream_cmd


AWAIT_INTERVAL_PROC = 5
AWAIT_INTERVAL_NEW_URL = 10
AWAIT_INTERVAL_CHECK = 30

logger = logging.getLogger()

class State:
    def __init__(self, loop: asyncio.AbstractEventLoop, db: DBI):
        self.db = db
        self.streams: Dict[int, str] = {}
        self.camera_types: Dict[int, str] = {}
        self.to_close: List[int] = []

        self.loop = loop
        self.check_task: Optional[Task[Any]] = None
        self.restream_tasks: Dict[int, Task[Any]] = {}

        self.start_check_task()


    def start_check_task(self):
        logger.debug(f"Start checking task")
        self.check_task = self.loop.create_task(self.check_task_loop())

    def add_restream_task(self, camera_id):
        logger.info(f"[{camera_id}] Start restream task")
        after_done = lambda Task: self.restream_done(camera_id)

        self.restream_tasks[camera_id] = self.loop.create_task(self.restream_loop(camera_id))
        self.restream_tasks[camera_id].add_done_callback(after_done)

    async def check_task_loop(self):
        while True:
            to_close = list(self.streams.keys())
            cameras = await self.db.get_camera_urls()
                
            new_streams = {}
            new_camera_types = {}

            for camera_id, camera_info in cameras.items():
                new_streams[camera_id] = camera_info['url']
                new_camera_types[camera_id] = camera_info['camera_type']

            self.streams = new_streams
            self.camera_types = new_camera_types

            # logger.debug(f"Streams and types {self.streams} {self.camera_types}")

            for camera_id in new_streams.keys():
                if camera_id in to_close:
                    to_close.remove(camera_id)
                else:
                    self.add_restream_task(camera_id)
            self.to_close = to_close

            await asyncio.sleep(AWAIT_INTERVAL_CHECK)


    async def restream_loop(self, camera_id):
        proc = None    

        url = self.streams[camera_id]
        camera_type = self.camera_types[camera_id]    
        logger.debug(f"[{camera_id}] Check for ({camera_type}) {url}")

        cmd = await self.get_cmd(camera_id, camera_type, url)
        logger.debug(f"[{camera_id}] Restream command is {cmd}")

        while True:
            if proc is None:
                logger.debug(f"[{camera_id}] Exec {cmd}")
                proc = Popen(cmd, shell=True)                
            else:
                return_code = proc.poll()
                if return_code is not None:
                    logger.warning(f"[{camera_id}] Process is closed with return {return_code}")
                    proc = None
                
                if camera_id in self.to_close:
                    # if we need to stop restreaming
                    logger.info(f"[{camera_id}] Camera in close list, exit")

                    if return_code is None:
                        proc.terminate() 

                    break
                elif self.streams[camera_id] != url:
                    # if url was changed                        
                    logger.info(f"[{camera_id}] Camera URL was changeg from {url} to {self.streams[camera_id]}")

                    if return_code is None:
                        proc.terminate() 
                        proc = None

                    url = self.streams[camera_id]
                    camera_type = self.camera_types[camera_id]
                    cmd = await self.get_cmd(camera_id, camera_type, url)                            
                    logger.debug(f"[{camera_id}] New restream command is {cmd}")

            await asyncio.sleep(AWAIT_INTERVAL_PROC)


    async def get_cmd(self, camera_id, camera_type, url):
        cmd = None

        while cmd is None:
            cmd = make_restream_cmd(camera_id, camera_type, url)

            if cmd is None:
                if self.streams[camera_id] == url:
                    logger.warning(f"[{camera_id}] Can't create restream command for ({camera_type}) {url}, is camera online?")
                    await asyncio.sleep(AWAIT_INTERVAL_NEW_URL)
                else:
                    url = self.streams[camera_id]
            
        return cmd


    def restream_done(self, camera_id):
        logger.debug(f"[{camera_id}] Task for camera is stopped, cleanup")
        if camera_id in self.restream_tasks:
            del self.restream_tasks[camera_id]  
        if camera_id in self.to_close:
            self.to_close.remove(camera_id)  
