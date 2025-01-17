import json
import logging
import asyncpg

from typing import Optional, Any, Dict, List

logger = logging.getLogger()


def to_url(camera):
    match camera['camera_type']:
        case "COMMON":
            url = f"rtsp://{camera['link']}:554/user={camera['login']}&password={camera['password']}&channel={camera['channel']}&stream=0.sdp?"
        case "DAHUA":
            url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/cam/realmonitor?channel=1&subtype={camera['channel'] if camera['channel'] == 0 else 1}"
        case "HIKVISION":
            if camera['channel']:
                url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/Streaming/Channels/{camera['channel']}"
            else:
                url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/Streaming/Channels/101"
        case "HIKVISIONDS":
            url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/ISAPI/Streaming/Channels/{camera['channel'] if camera['channel'] else 101}"
        case "HIKVISIONCH1":
            url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/h264/ch1/main/av_stream"
        case "TRASSIR":
            url = f"rtsp://{camera['link']}/{camera['login']}/"
        case "VEI":
            if camera['channel'] == 5:
                url = f"rtsp://{camera['link']}:554/{camera['login']}{camera['password']}/"
            else:
                url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/video_1+audio_1.ini"
        case _:
            url = f"rtsp://{camera['login']}:{camera['password']}@{camera['link']}:554/stream={camera['channel']}"

    return url

def convert_cameras_list(cameras):
    result = {}

    # for c in cameras:
    #     result[c['id']] = { "camera_type": c['camera_type'], "url": to_url(c) }

    for c in cameras:
        result[c['id']] = { "camera_type": c["name"], "url": c['rtsp_url'] }

    return result


class DBI:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn: Optional[asyncpg.Connection] = None 
        self.stm_cameras_list: Optional[asyncpg.PreparedStatement] = None

    async def connect(self):
        if self.conn is not None:
            await self.done()

        result = True

        # try:
        #     self.conn = await asyncpg.connect(self.dsn)
        #     self.stm_cameras_list = await self.conn.prepare("SELECT c.* FROM cameras c ORDER BY id")
        #     result = True
        # except Exception as e:
        #     logger.error(f"Can't establish connection to the database {self.dsn}, reason {e}")
        #     self.conn = None
        #     self.stm_cameras_list = None
        #     pass

        return result

    async def get_camera_urls(self):
        result = {}

        try:
            with open("cameras.json", "r") as f:
                data = json.load(f)
                for k, v in data.items():
                    result[k] = {"camera_type": v["name"], "url": v["rtsp_url"]}
        except Exception as e:
            logger.error(f"Can't get camera's list, reason {e}")
            self.stm_cameras_list = None

        return result

    async def done(self):
        if self.conn is not None:
            await self.conn.close()

        self.conn = None
        self.stm_cameras_list = None
