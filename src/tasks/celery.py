from celery import Celery
from src.config import settings

app = Celery("geotime", backend=settings.CELERY_BACKEND, broker=settings.CELERY_BROKER)
app.conf.update(enable_utc=True, timezone=settings.DEFAULT_TIMEZONE)
