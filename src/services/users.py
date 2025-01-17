from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.exceptions import HTTPException
from fastapi import Depends, status
from dotenv import load_dotenv
import os

from src.config import settings


load_dotenv()

auth_state = {"is_admin": False}
security = HTTPBasic()


def password_required(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Basic"},
        )
