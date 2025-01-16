from pydantic import BaseModel


class PasswordUserSchema(BaseModel):
    password: str


class ChangePasswordSchema(BaseModel):
    password: str
    new_password: str
