# app/services/base_service.py
import requests
from fastapi import HTTPException, Depends
from app.db.database import get_session, get_session_by_hash
from app.core.security import get_current_user
from loguru import logger
from typing import Optional


class BaseEducationService:
    """教务系统服务基类，提供通用的session管理和错误处理"""

    @staticmethod
    def get_user_session(
        student_id_hash: str = Depends(get_current_user),
    ) -> requests.Session:
        """
        依赖项：获取当前用户的教务系统session

        Args:
            student_id_hash: 学生ID的hash值（从JWT Token中获取）

        Returns:
            requests.Session: 已登录的教务系统session

        Raises:
            HTTPException: 当session不存在或已失效时抛出401异常
        """
        logger.debug(f"获取用户 {student_id_hash[:8]}**** 的教务系统session...")

        # 使用hash值查询session
        session = get_session_by_hash(student_id_hash=student_id_hash)
        if session is None:
            logger.warning(f"用户 {student_id_hash[:8]}**** 的session不存在或已失效")
            raise HTTPException(
                status_code=401, detail="Session不存在或已失效，请重新登录"
            )

        logger.debug(f"用户 {student_id_hash[:8]}**** 的session获取成功")
        return session

    @staticmethod
    def handle_service_error(
        error: Exception, operation_name: str = "操作"
    ) -> HTTPException:
        """
        统一处理服务层错误，转换为适当的HTTPException

        Args:
            error: 原始异常
            operation_name: 操作名称

        Returns:
            HTTPException: 转换后的HTTP异常
        """
        error_msg = str(error)

        # 判断错误类型并返回相应的HTTP状态码
        if "session" in error_msg.lower() or "登录" in error_msg:
            logger.error(f"{operation_name}失败: {error_msg}")
            return HTTPException(status_code=401, detail=f"Session已失效，请重新登录")
        elif (
            "网络" in error_msg or "连接" in error_msg or "timeout" in error_msg.lower()
        ):
            logger.error(f"{operation_name}失败: {error_msg}")
            return HTTPException(
                status_code=503, detail=f"{operation_name}失败: 教务系统连接超时"
            )
        elif "未找到" in error_msg or "not found" in error_msg.lower():
            logger.warning(f"{operation_name}失败: {error_msg}")
            return HTTPException(status_code=404, detail=error_msg)
        else:
            logger.error(f"{operation_name}过程中发生未知错误: {error_msg}")
            return HTTPException(
                status_code=500, detail=f"{operation_name}失败: {error_msg}"
            )

    @staticmethod
    def close_session(session: Optional[requests.Session]):
        """
        安全关闭session

        Args:
            session: 要关闭的session对象
        """
        if session:
            try:
                session.close()
                logger.debug("教务系统session已关闭")
            except Exception as e:
                logger.warning(f"关闭session时发生错误: {e}")


# 创建依赖项函数
def get_user_session(
    student_id_hash: str = Depends(get_current_user),
) -> requests.Session:
    """全局依赖项：获取用户session"""
    return BaseEducationService.get_user_session(student_id_hash)
