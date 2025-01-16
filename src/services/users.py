# from sqlalchemy.orm import Session

# from datetime import datetime, timedelta
# from fastapi import Depends
# from passlib.context import CryptContext
# from fastapi.exceptions import HTTPException
# from fastapi.security import OAuth2PasswordBearer
# import bcrypt
# from jose import jwt, JWTError
# from sqlalchemy.orm import Session

# from src.db import db_helper
# from src.models.users import User
# from src.core.schemas.users import CreateUserSchema


# class UserService:
#     def __init__(self, db: Session) -> None:
#         self.db = db

#     def get_user_by_username(self, username: str) -> User:
#         return self.db.query(User).filter(User.username == username).first()

#     def get_users(self) -> list[User]:
#         return self.db.query(User).all()

#     def create_user(self, schema: CreateUserSchema) -> User:
#         hashed_password = get_password_hash(schema.password).encode("utf-8")
#         user = User(
#             username=schema.username,
#             hashed_password=hashed_password,
#             is_superuser=schema.is_superuser,
#         )
#         self.db.add(user)
#         self.db.commit()
#         self.db.refresh(user)
#         return user

#     def delete_user(self, user_id: int) -> None:
#         user = self.db.query(User).get(user_id)
#         self.db.delete(user)
#         self.db.commit()

#     def change_user_password(
#         self, user_id: int, new_password: str, old_password: str
#     ) -> None:
#         user = self.db.query(User).get(user_id)
#         if not verify_password(old_password, user.hashed_password):
#             raise HTTPException(status_code=400, detail="Invalid password")
#         user.hashed_password = get_password_hash(new_password)
#         self.db.commit()
#         self.db.refresh(user)


# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# # Hashing password
# def get_password_hash(password):
#     return pwd_context.hash(password)


# # Verifying password
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# # Создание токена
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (
#         expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def get_current_user(
#     token: str = Depends(oauth2_scheme), db: Session = Depends(db_helper.get_db)
# ):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user = UserService(db=db).get_user_by_username(username)
#         if user is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# # Middleware для проверки администратора
# def superuser_required(user: User = Depends(get_current_user)):
#     if not user.is_superuser:
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return user

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
