from fastapi import FastAPI
import uvicorn

from src.config import settings
from src.api.router.users import router as users_router

app = FastAPI(
    title="GeoTime Central",
    description="Documentation for services provided by GeoTime Central",
    version=settings.VERSION,
)

app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
