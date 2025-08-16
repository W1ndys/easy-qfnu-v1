"""
用户相关数据模型
定义用户认证和授权相关的Pydantic模型
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""

    student_id: str
    openid: Optional[str] = None
    contribution_preference: bool = False


class UserCreate(BaseModel):
    """用户创建模型"""

    student_id: str
    openid: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模型"""

    student_id: str
    password: str


class User(UserBase):
    """完整用户模型"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT令牌模型"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模型"""

    student_id: Optional[str] = None
    user_id: Optional[int] = None
