from fastapi import FastAPI
import uvicorn

from config import settings

app = FastAPI(
    title="GeoTime Central",
    description="Documentation for services provided by GeoTime Central",
    version=settings.VERSION,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
