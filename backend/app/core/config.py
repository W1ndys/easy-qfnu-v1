"""
配置文件
管理应用程序的所有配置项
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用程序配置"""

    # 应用基础配置
    PROJECT_NAME: str = "Easy-QFNUJW"
    VERSION: str = "0.0.1"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app/data/easyqfnujw.db"

    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "https://servicewechat.com",  # 微信小程序域名
        "http://localhost",
        "http://127.0.0.1",
    ]

    # 学校教务系统配置
    QFNU_LOGIN_URL: str = "http://jwgl.qfnu.edu.cn/jsxsd/xk/LoginToXk"
    QFNU_GRADE_URL: str = "http://jwgl.qfnu.edu.cn/jsxsd/kscj/cjcx_list"
    QFNU_SCHEDULE_URL: str = "http://jwgl.qfnu.edu.cn/jsxsd/xskb/xskb_list.do"

    # 会话配置
    SESSION_TIMEOUT: int = 30 * 60  # 30分钟

    # 数据统计配置
    MIN_DATA_FOR_RANKING: int = 10  # 班内排名最小数据量要求

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
