# app/services/auth_service.py
import requests
from typing import Optional, Tuple
from app.services.scraper import login_to_university
from app.db.database import save_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    refresh_access_token as core_refresh_access_token,
    logout_user as core_logout_user,
)
from loguru import logger


class AuthService:
    """认证服务类"""

    @staticmethod
    def authenticate_user(
        student_id: str, password: str, client_ip: str
    ) -> Tuple[str, str]:
        """
        用户认证并生成Token

        Args:
            student_id: 学号
            password: 密码
            client_ip: 客户端IP地址

        Returns:
            tuple: (access_token, refresh_token)

        Raises:
            Exception: 当认证失败时抛出异常
        """
        logger.info(f"开始用户认证，学号: {student_id}, 客户端IP: {client_ip}")

        try:
            logger.debug("开始教务系统登录验证...")
            session = login_to_university(student_id=student_id, password=password)

            if session is None:
                logger.warning(f"教务系统登录失败，学号: {student_id}")
                raise Exception("学号或密码错误")

            logger.info(f"教务系统登录成功，学号: {student_id}")

            try:
                # 登录成功后，将 session 的 cookies 保存到数据库
                logger.debug("保存登录会话到数据库...")
                save_session(student_id=student_id, session_obj=session)
                logger.debug("会话保存成功")
            except Exception as e:
                logger.error(f"保存会话到数据库失败: {e}")
                # 即使保存失败，也不影响登录流程
            finally:
                session.close()
                logger.debug("教务系统session已关闭")

            # 创建Token对
            logger.debug("开始创建JWT Token...")
            # 同时在payload中存储明文学号和学号hash
            user_data = {"sub": student_id, "raw_sub": student_id}
            access_token = create_access_token(user_data, client_ip=client_ip)
            refresh_token = create_refresh_token(user_data, client_ip=client_ip)
            logger.info(f"JWT Token创建成功，学号: {student_id}")

            return access_token, refresh_token

        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            raise

    @staticmethod
    def refresh_user_token(refresh_token: str, client_ip: str) -> Tuple[str, str]:
        """
        刷新用户Token

        Args:
            refresh_token: 刷新令牌
            client_ip: 客户端IP地址

        Returns:
            tuple: (new_access_token, new_refresh_token)

        Raises:
            Exception: 当刷新失败时抛出异常
        """
        logger.info(f"开始Token刷新，客户端IP: {client_ip}")

        try:
            logger.debug("开始刷新Token...")
            new_access_token, new_refresh_token = core_refresh_access_token(
                refresh_token, client_ip=client_ip
            )
            logger.info("Token刷新成功")
            return new_access_token, new_refresh_token
        except Exception as e:
            logger.error(f"Token刷新失败: {e}")
            raise

    @staticmethod
    def logout_user(token: str) -> None:
        """
        用户登出

        Args:
            token: 访问令牌

        Raises:
            Exception: 当登出失败时抛出异常
        """
        logger.debug("开始撤销Token...")
        try:
            core_logout_user(token)
            logger.info("用户登出成功")
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            raise


# 创建全局服务实例
auth_service = AuthService()
