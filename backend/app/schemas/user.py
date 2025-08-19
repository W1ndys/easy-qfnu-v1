# app/schemas/user.py
from pydantic import BaseModel


class UserLogin(BaseModel):
    student_id: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
