# app/schemas/user.py
from pydantic import BaseModel


class UserLogin(BaseModel):
    student_id: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # 过期时间（秒）


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
