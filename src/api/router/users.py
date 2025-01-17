# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from src.services.users import (
#     superuser_required,
#     UserService,
#     create_access_token,
#     verify_password,
# )
# from src.core.schemas.users import CreateUserSchema
# from src.models.users import User
# from src.db import db_helper

# router = APIRouter()


# @router.post("/token/")
# def login_for_access_token(
#     username: str, password: str, db: Session = Depends(db_helper.get_db)
# ):
#     user = UserService(db).get_user_by_username(username)
#     if not user:
#         return {"error": "Invalid credentials"}
#     if not verify_password(password, user.hashed_password):
#         return {"error": "Invalid credentials"}
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": "Bearer: " + access_token}


# @router.post("/users/")
# async def create_user(
#     user_data: CreateUserSchema,
#     # current_user: User = Depends(superuser_required),
#     db: Session = Depends(db_helper.get_db),
# ):
#     user = UserService(db).create_user(user_data)
#     return user


# @router.delete("/users/{user_id}")
# async def delete_user(
#     user_id: int,
#     current_user: User = Depends(superuser_required),
#     db: Session = Depends(db_helper.get_db),
# ):
#     UserService(db).delete_user(user_id)
#     return {"message": "User deleted successfully"}


# @router.get("/users/")
# async def get_users(
#     current_user: User = Depends(superuser_required),
#     db: Session = Depends(db_helper.get_db),
# ):
#     users = UserService(db).get_users()
#     return users


from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBasicCredentials
from fastapi.exceptions import HTTPException

from src.services.users import auth_state
from src.config import settings
from src.core.schemas.users import PasswordUserSchema, ChangePasswordSchema


router = APIRouter(tags=["Users"])


@router.post("/login")
def login(data: PasswordUserSchema):
    if data.password == settings.ADMIN_PASSWORD:
        auth_state["is_admin"] = True
        return {"message": "Authenticated successfully"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
    )


@router.post("/logout")
def logout():
    auth_state["is_admin"] = False
    return {"message": "Logged out successfully"}


@router.post("/change_password")
def change_password(data: ChangePasswordSchema):
    if not auth_state["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You must login first."
        )
    if data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    settings.ADMIN_PASSWORD = data.new_password

    return {"message": "Password changed successfully"}
