"""
来源验证中间件模块

用于验证HTTP请求的来源，防止跨域攻击和非法访问。
支持多种验证策略，包括Origin头、Referer头和User-Agent检测。

作者: W1ndys
创建时间: 2024
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import re


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """
    来源验证中间件

    验证HTTP请求的来源是否合法，支持多种验证策略：
    1. Origin头验证
    2. Referer头验证
    3. User-Agent检测（移动端特殊处理）
    4. Host头验证
    """

    def __init__(self, app):
        super().__init__(app)
        # 允许的域名模式
        self.allowed_patterns = [
            r"^https?://localhost(:\d+)?/?.*$",
            r"^https?://127\.0\.0\.1(:\d+)?/?.*$",
            r"^https?://([a-zA-Z0-9-]+\.)*easy-qfnu\.top(:\d+)?/?.*$",
            r"^https://servicewechat\.com/?.*$",  # 微信小程序
        ]

        # 特殊路径白名单（不需要验证来源的路径）
        self.whitelist_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

        # 移动端User-Agent模式（这些请求通常没有完整的Origin信息）
        self.mobile_user_agent_patterns = [
            r".*Mobile.*",
            r".*Android.*",
            r".*iPhone.*",
            r".*iPad.*",
            r".*MicroMessenger.*",  # 微信
            r".*QQ.*",
            r".*Alipay.*",
        ]

        logger.info("来源验证中间件初始化完成")

    async def dispatch(self, request: Request, call_next):
        """
        处理请求的中间件逻辑

        Args:
            request (Request): FastAPI请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            Response: HTTP响应对象
        """
        try:
            # 获取请求信息
            path = request.url.path
            method = request.method
            user_agent = request.headers.get("user-agent", "")
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")
            host = request.headers.get("host")

            logger.debug(
                f"请求详情 - Method: {method}, Path: {path}, "
                f"Origin: {origin}, Referer: {referer}, Host: {host}, "
                f"User-Agent: {user_agent[:100]}..."  # 截取前100字符避免日志过长
            )

            # 检查是否在白名单路径中
            if path in self.whitelist_paths:
                logger.debug(f"路径 {path} 在白名单中，跳过来源验证")
                return await call_next(request)

            # 检查是否为移动端请求
            is_mobile = self._is_mobile_request(user_agent)
            if is_mobile:
                logger.debug(f"检测到移动端请求，User-Agent: {user_agent[:50]}...")

            # 验证来源
            validation_result = self._validate_request_origin(
                origin, referer, host, user_agent, is_mobile
            )

            if validation_result["allowed"]:
                logger.debug(f"来源验证通过 - 原因: {validation_result['reason']}")
                return await call_next(request)
            else:
                # 来源验证失败，记录详细信息
                logger.warning(
                    f"来源验证失败 - Path: {path}, Method: {method}, "
                    f"Origin: {origin}, Referer: {referer}, Host: {host}, "
                    f"User-Agent: {user_agent[:100]}..., "
                    f"原因: {validation_result['reason']}"
                )

                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "访问被拒绝：无效的请求来源",
                        "error_code": "INVALID_ORIGIN",
                        "reason": validation_result["reason"],
                    },
                )

        except Exception as e:
            logger.error(f"来源验证中间件处理异常: {e}")
            # 发生异常时允许请求通过，避免影响正常功能
            return await call_next(request)

    def _validate_request_origin(
        self, origin: str, referer: str, host: str, user_agent: str, is_mobile: bool
    ) -> dict:
        """
        验证请求来源

        Args:
            origin (str): Origin头
            referer (str): Referer头
            host (str): Host头
            user_agent (str): User-Agent头
            is_mobile (bool): 是否为移动端请求

        Returns:
            dict: 验证结果 {"allowed": bool, "reason": str}
        """
        # 如果是本地开发环境，直接允许
        if host and ("localhost" in host or "127.0.0.1" in host):
            return {"allowed": True, "reason": "本地开发环境"}

        # 优先检查Origin头
        if origin and self._is_allowed_origin(origin):
            return {"allowed": True, "reason": f"Origin头验证通过: {origin}"}

        # 检查Referer头
        if referer and self._is_allowed_origin(referer):
            return {"allowed": True, "reason": f"Referer头验证通过: {referer}"}

        # 对于移动端请求，采用更宽松的策略
        if is_mobile:
            # 移动端请求通常没有完整的Origin信息，特别是微信小程序、APP内嵌浏览器等
            logger.debug("移动端请求采用宽松验证策略")

            # 检查Host头是否为允许的域名
            if host and self._is_allowed_host(host):
                return {"allowed": True, "reason": f"移动端Host头验证通过: {host}"}

            # 如果是微信或其他已知的移动端应用，可以进一步放宽
            if any(
                pattern in user_agent for pattern in ["MicroMessenger", "QQ", "Alipay"]
            ):
                return {
                    "allowed": True,
                    "reason": f"已知移动端应用: {user_agent[:30]}...",
                }

        # 对于没有Origin和Referer的请求（可能是直接API调用）
        if not origin and not referer:
            # 在生产环境中，可以根据实际需求决定是否允许
            logger.debug("无Origin和Referer信息的请求，可能是直接API调用")
            return {"allowed": True, "reason": "直接API调用（无来源信息）"}

        # 所有验证都失败
        return {
            "allowed": False,
            "reason": f"所有验证策略均失败 - Origin: {origin}, Referer: {referer}, Host: {host}",
        }

    def _is_mobile_request(self, user_agent: str) -> bool:
        """
        检测是否为移动端请求

        Args:
            user_agent (str): User-Agent字符串

        Returns:
            bool: 是否为移动端请求
        """
        if not user_agent:
            return False

        for pattern in self.mobile_user_agent_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        return False

    def _is_allowed_origin(self, origin: str) -> bool:
        """
        检查来源URL是否被允许

        Args:
            origin (str): 来源URL

        Returns:
            bool: 是否允许该来源
        """
        if not origin:
            return False

        # 规范化URL（移除尾部斜杠）
        origin = origin.rstrip("/")

        # 检查是否匹配允许的模式
        for pattern in self.allowed_patterns:
            if re.match(pattern, origin, re.IGNORECASE):
                logger.debug(f"来源 {origin} 匹配模式 {pattern}")
                return True

        logger.debug(f"来源 {origin} 不匹配任何允许的模式")
        return False

    def _is_allowed_host(self, host: str) -> bool:
        """
        检查Host头是否被允许

        Args:
            host (str): Host头值

        Returns:
            bool: 是否允许该Host
        """
        if not host:
            return False

        # 允许的主机模式
        allowed_hosts = [
            r"^localhost(:\d+)?$",
            r"^127\.0\.0\.1(:\d+)?$",
            r"^([a-zA-Z0-9-]+\.)*easy-qfnu\.top(:\d+)?$",
        ]

        for pattern in allowed_hosts:
            if re.match(pattern, host, re.IGNORECASE):
                logger.debug(f"Host {host} 匹配模式 {pattern}")
                return True

        logger.debug(f"Host {host} 不匹配任何允许的模式")
        return False
