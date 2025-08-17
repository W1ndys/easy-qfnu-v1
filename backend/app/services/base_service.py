"""
基础服务类
提供所有服务类的公共功能
"""

import logging
from typing import Optional
from app.core.security import SessionExpiredError
from app.core.database import DatabaseManager
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class BaseService:
    """基础服务类，提供公共功能"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.auth_service = AuthService(db)

    def is_session_expired(self, response_text: str, response_url: str) -> bool:
        """
        判断session是否过期

        Args:
            response_text: 响应内容
            response_url: 响应URL

        Returns:
            True表示session已过期，False表示session有效
        """
        # 检查URL是否包含login
        if "login" in response_url.lower():
            return True

        # 检查响应内容是否包含登录相关的关键词
        login_keywords = ["用户登录", "请输入账号", "请输入密码"]

        # 如果同时包含这些关键词，则认为session已过期
        keyword_count = sum(1 for keyword in login_keywords if keyword in response_text)

        # 如果包含所有关键词或者大部分关键词，则认为session已过期
        if keyword_count >= 3:
            return True

        # 也可以检查是否包含其中2个或以上关键词作为过期判断
        # 根据实际情况调整严格程度
        if keyword_count >= 2:
            return True

        return False

    async def handle_session_expired(
        self, student_id: str, response_text: str, response_url: str
    ) -> None:
        """
        处理session过期情况

        Args:
            student_id: 学号
            response_text: 响应内容
            response_url: 响应URL

        Raises:
            SessionExpiredError: 当session过期时抛出
        """
        if self.is_session_expired(response_text, response_url):
            logger.warning(f"检测到学号 {student_id} 的session已过期")
            await self.auth_service.clear_session(student_id)
            raise SessionExpiredError("Session已过期")
