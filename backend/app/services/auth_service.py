"""
认证服务
处理用户认证、会话管理等业务逻辑
"""

import requests
import pickle
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.security import SessionExpiredError
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    async def authenticate_with_school(
        self, student_id: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        通过学校官网验证用户身份并获取Session

        Args:
            student_id: 学号
            password: 密码

        Returns:
            Session数据字典，认证失败返回None
        """
        try:
            # 创建会话
            session = requests.Session()

            # 构造登录数据
            login_data = {
                "userAccount": student_id,
                "userPassword": password,
                "encoded": "",  # 根据学校系统要求调整
            }

            # 发送登录请求
            response = session.post(
                settings.QFNU_LOGIN_URL,
                data=login_data,
                timeout=10,
                allow_redirects=True,
            )

            # 检查登录是否成功
            if self._is_login_successful(response):
                # 返回会话数据
                return {
                    "cookies": session.cookies.get_dict(),
                    "headers": dict(session.headers),
                    "student_id": student_id,
                }
            else:
                logger.warning(f"学号 {student_id} 登录失败")
                return None

        except requests.RequestException as e:
            logger.error(f"学校官网登录请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"认证过程发生未知错误: {e}")
            return None

    def _is_login_successful(self, response: requests.Response) -> bool:
        """
        判断登录是否成功

        Args:
            response: 登录响应

        Returns:
            登录是否成功
        """
        # 根据学校系统的具体响应判断登录是否成功
        # 这里需要根据实际情况调整判断逻辑

        # 检查是否被重定向到登录页面
        if "login" in response.url.lower():
            return False

        # 检查响应内容中是否包含错误信息
        if "用户名或密码错误" in response.text or "登录失败" in response.text:
            return False

        # 检查是否成功进入主页面
        if "主页" in response.text or "欢迎" in response.text:
            return True

        # 默认情况下，如果状态码是200且没有明显的错误标识，则认为成功
        return response.status_code == 200

    async def store_session(
        self, student_id: str, session_data: Dict[str, Any]
    ) -> None:
        """
        存储Session数据到数据库

        Args:
            student_id: 学号
            session_data: Session数据
        """
        try:
            # 序列化Session数据
            serialized_data = pickle.dumps(session_data)

            # 计算过期时间
            expires_at = datetime.now() + timedelta(seconds=settings.SESSION_TIMEOUT)

            # 存储到数据库
            query = """
            INSERT OR REPLACE INTO sessions (student_id, session_data, expires_at, updated_at)
            VALUES (?, ?, ?, ?)
            """

            self.db.execute_update(
                query, (student_id, serialized_data, expires_at, datetime.now())
            )

            logger.info(f"Session已存储，学号: {student_id}")

        except Exception as e:
            logger.error(f"存储Session失败: {e}")
            raise

    async def get_session(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        从数据库获取Session数据

        Args:
            student_id: 学号

        Returns:
            Session数据，不存在或已过期返回None
        """
        try:
            query = """
            SELECT session_data, expires_at FROM sessions 
            WHERE student_id = ? AND expires_at > ?
            """

            result = self.db.execute_query(query, (student_id, datetime.now()))

            if result:
                # 反序列化Session数据
                session_data = pickle.loads(result[0]["session_data"])
                return session_data
            else:
                return None

        except Exception as e:
            logger.error(f"获取Session失败: {e}")
            return None

    async def clear_session(self, student_id: str) -> None:
        """
        清除用户的Session数据

        Args:
            student_id: 学号
        """
        try:
            query = "DELETE FROM sessions WHERE student_id = ?"
            self.db.execute_update(query, (student_id,))

            logger.info(f"Session已清除，学号: {student_id}")

        except Exception as e:
            logger.error(f"清除Session失败: {e}")
            raise

    async def get_or_create_user(
        self, student_id: str, openid: str = None
    ) -> Dict[str, Any]:
        """
        获取或创建用户记录

        Args:
            student_id: 学号
            openid: 微信openid（可选）

        Returns:
            用户信息
        """
        try:
            # 查询现有用户
            query = "SELECT * FROM users WHERE student_id = ?"
            result = self.db.execute_query(query, (student_id,))

            if result:
                return dict(result[0])
            else:
                # 创建新用户
                insert_query = """
                INSERT INTO users (openid, student_id, contribution_preference, created_at)
                VALUES (?, ?, ?, ?)
                """

                self.db.execute_update(
                    insert_query, (openid, student_id, False, datetime.now())
                )

                # 返回新创建的用户信息
                result = self.db.execute_query(query, (student_id,))
                return dict(result[0])

        except Exception as e:
            logger.error(f"获取或创建用户失败: {e}")
            raise

    async def validate_session(self, student_id: str) -> bool:
        """
        验证用户的Session是否仍然有效

        Args:
            student_id: 学号

        Returns:
            Session是否有效
        """
        try:
            session_data = await self.get_session(student_id)

            if not session_data:
                return False

            # 创建请求会话并设置cookies
            session = requests.Session()
            session.cookies.update(session_data.get("cookies", {}))

            # 发送测试请求到需要登录的页面
            test_response = session.get(
                settings.QFNU_GRADE_URL, timeout=10, allow_redirects=False
            )

            # 如果被重定向到登录页面，说明Session已失效
            if (
                test_response.status_code == 302
                and "login" in test_response.headers.get("Location", "").lower()
            ):
                await self.clear_session(student_id)
                return False

            return test_response.status_code == 200

        except requests.RequestException as e:
            logger.warning(f"Session验证请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"Session验证过程发生错误: {e}")
            return False
