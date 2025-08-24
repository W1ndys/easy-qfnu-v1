# app/main.py

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
import sys
import os
from contextlib import asynccontextmanager
from app.middleware.origin_validation import OriginValidationMiddleware

# 日志系统完善
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
# 以启动时间命名日志文件
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
# 使用 Loguru 时间占位符，日志轮转命名为 YYYY-MM-DD_hh-mm-ss（Windows 不允许 :）
LOG_PATH = os.path.join(LOG_DIR, "{time:YYYY-MM-DD_hh-mm-ss}.log")

# 移除默认的logger
logger.remove()
# 控制台日志
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
# 文件日志，保留7天，自动轮转
logger.add(
    LOG_PATH,
    rotation="10 MB",
    retention="7 days",
    level=LOG_LEVEL,
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {process} | {thread} | {name}:{function}:{line} - {message}",
)

# 加载环境变量 - 必须在导入其他模块之前
logger.info("正在加载环境变量...")
load_dotenv()
logger.info("环境变量加载完成")


# 先定义 lifespan 函数
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动事件触发，正在初始化服务...")
    # 启动阶段标记为未就绪
    app.state.ready = False

    # 启动定时任务
    logger.info("正在启动定时任务...")
    try:
        from app.services.scheduler import scheduler

        scheduler.add_session_cleanup_job(cleanup_hours=2, interval_hours=2)
        logger.info("Session清理定时任务已添加")

        scheduler.add_semester_update_job()
        logger.info("学期数据更新定时任务已添加")

        scheduler.start()
        logger.info("定时任务启动完成")
    except Exception as e:
        logger.error(f"启动定时任务失败: {e}")

    # 初始化学期计算器
    try:
        from app.utils.semester_calculator import init_semester_calculator

        init_semester_calculator()
        logger.info("学期计算器初始化完成")
    except Exception as e:
        logger.error(f"初始化学期计算器失败: {e}")

    # 发送飞书通知
    try:
        from app.services.feishu import send_feishu_msg

        send_feishu_msg(
            "Easy-QFNUJW API 启动成功",
            f"Easy-QFNUJW API 启动成功，当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
        logger.info("飞书启动通知发送成功")
    except Exception as e:
        logger.error(f"发送飞书启动通知失败: {e}")

    # 启动流程结束，标记为就绪
    app.state.ready = True
    logger.info("应用准备就绪")
    yield

    # 关闭时执行
    logger.info("应用关闭事件触发，正在清理资源...")
    # 关闭前标记为未就绪
    app.state.ready = False
    try:
        from app.services.scheduler import scheduler

        scheduler.stop()
        logger.info("定时任务已停止")
    except Exception as e:
        logger.error(f"停止定时任务失败: {e}")


# 创建FastAPI应用实例
logger.info("正在创建FastAPI应用实例...")
app = FastAPI(title="Easy-QFNUJW API", version="1.0.0", lifespan=lifespan)
logger.info("FastAPI应用实例创建成功")

# 配置CORS中间件
logger.info("正在配置CORS中间件...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:*",
        "http://127.0.0.1:*",
        "https://easy-qfnu.top",
        "http://easy-qfnu.top",
        "https://*.easy-qfnu.top",
        "http://*.easy-qfnu.top",
        "https://servicewechat.com",
        "https://*.servicewechat.com",
    ],
    allow_origin_regex=r"^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$|^https?:\/\/([a-zA-Z0-9-]+\.)*easy-qfnu\.top(:\d+)?$|^https:\/\/([a-zA-Z0-9-]+\.)*servicewechat\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,  # 预检缓存 24h，减少频次
)
logger.info("CORS中间件配置完成")

# 添加来源验证中间件（可通过环境变量控制开关）
logger.info("正在添加来源验证中间件...")
origin_validation_enabled = (
    os.getenv("ORIGIN_VALIDATION_ENABLED", "true").lower() == "true"
)
if origin_validation_enabled:
    app.add_middleware(OriginValidationMiddleware)
    logger.info("来源验证中间件添加完成")
else:
    logger.warning("已禁用来源验证中间件（ORIGIN_VALIDATION_ENABLED=false）")

# 初始化数据库
logger.info("正在初始化数据库...")
try:
    from app.db.database import init_db

    init_db()
    logger.info("数据库初始化成功")
except Exception as e:
    logger.error(f"数据库初始化失败: {e}")
    raise


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    logger.info(
        f"收到请求: {request.method} {request.url} - 客户端IP: {request.client.host if request.client else 'unknown'}"
    )

    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"请求处理完成: {request.method} {request.url} - 状态码: {response.status_code} - 处理时间: {process_time:.3f}秒"
        )
        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"请求处理异常: {request.method} {request.url} - 错误: {e} - 处理时间: {process_time:.3f}秒"
        )
        raise


@app.get("/", tags=["Root"])
def read_root():
    logger.info("访问根路径 /")
    return {"message": "Welcome to Easy-QFNUJW API"}


# 健康检查与就绪检查
@app.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}


@app.get("/readyz", tags=["Health"])
def readyz():
    if getattr(app.state, "ready", False):
        return {"status": "ready"}
    return Response(status_code=503)


# 全局预检请求兜底，防止被其它中间件拦截导致 CORS 失败
@app.options("/{path:path}")
async def preflight_handler(path: str):
    return Response(status_code=200)


# 使用模块化路由注册
logger.info("正在注册API路由...")
try:
    from app.api.v1 import api_router

    app.include_router(api_router, prefix="/api/v1")
    logger.info("所有API路由注册完成")

    # 验证路由注册
    logger.info(f"应用路由数量: {len(app.routes)}")
    for route in app.routes:
        if hasattr(route, "path"):
            logger.debug(
                f"路由: {route.path} - 方法: {getattr(route, 'methods', 'N/A')}"
            )
        elif hasattr(route, "path_regex"):
            logger.debug(
                f"路由: {getattr(route, 'path_regex', 'unknown')} - 方法: {getattr(route, 'methods', 'N/A')}"
            )

except Exception as e:
    logger.error(f"API路由注册失败: {e}")
    raise


if __name__ == "__main__":
    logger.info("正在启动Uvicorn服务...")

    # 根据环境变量决定是否启用reload
    reload_mode = os.getenv("RELOAD_MODE", "false").lower() == "true"
    # 监听地址/端口可配置，默认 0.0.0.0:8000，避免反向代理连接失败导致 502
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    logger.info(f"服务配置: host={host}, port={port}, reload={reload_mode}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload_mode,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
