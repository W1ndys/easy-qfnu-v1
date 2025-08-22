# app/main.py

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
import sys
import os
from app.services.scheduler import scheduler

# 日志系统完善
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# 以启动时间命名日志文件
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

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

from app.api.v1 import auth as auth_router
from app.api.v1 import grades as grades_router
from app.api.v1 import average_scores as average_scores_router
from app.api.v1 import course_plan as course_plan_router
from app.db.database import init_db
from app.services.feishu import send_feishu_msg

logger.info("正在创建FastAPI应用实例...")
# 创建FastAPI应用实例
app = FastAPI(title="Easy-QFNUJW API", version="1.0.0")
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
    ],
    allow_origin_regex=r"^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$|^https?:\/\/([a-zA-Z0-9-]+\.)*easy-qfnu\.top(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS中间件配置完成")

# 初始化数据库
logger.info("正在初始化数据库...")
try:
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


# 使用 include_router 将各个API模块挂载到主应用上
logger.info("正在注册API路由...")
# prefix="/api/v1" 表示这个模块下所有接口的URL都会以/api/v1开头
# tags=["认证"] 用于在API文档中进行分组，非常方便
app.include_router(auth_router.router, prefix="/api/v1", tags=["认证"])
logger.info("认证路由注册完成")

app.include_router(grades_router.router, prefix="/api/v1", tags=["成绩"])
logger.info("成绩路由注册完成")

app.include_router(average_scores_router.router, prefix="/api/v1", tags=["平均分查询"])
logger.info("平均分查询路由注册完成")

app.include_router(course_plan_router.router, prefix="/api/v1", tags=["培养方案"])
logger.info("培养方案路由注册完成")
logger.info("所有API路由注册完成")

# 使用 FastAPI 生命周期事件来启动定时任务和发送通知
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动事件触发，正在初始化服务...")

    # 启动定时任务
    logger.info("正在启动定时任务...")
    try:
        scheduler.add_session_cleanup_job(cleanup_hours=2, interval_hours=2)
        logger.info("Session清理定时任务已添加")
    except Exception as e:
        logger.error(f"添加Session清理定时任务失败: {e}")

    scheduler.start()
    logger.info("定时任务启动完成")

    # 发送飞书通知
    try:
        send_feishu_msg(
            "Easy-QFNUJW API 启动成功",
            f"Easy-QFNUJW API 启动成功，当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
        logger.info("飞书启动通知发送成功")
    except Exception as e:
        logger.error(f"发送飞书启动通知失败: {e}")

    yield

    # 关闭时执行
    logger.info("应用关闭事件触发，正在清理资源...")
    try:
        scheduler.stop()
        logger.info("定时任务已停止")
    except Exception as e:
        logger.error(f"停止定时任务失败: {e}")


# 创建FastAPI应用实例时使用lifespan
app = FastAPI(title="Easy-QFNUJW API", version="1.0.0", lifespan=lifespan)

if __name__ == "__main__":
    logger.info("正在启动Uvicorn服务...")

    # 根据环境变量决定是否启用reload
    reload_mode = os.getenv("RELOAD_MODE", "false").lower() == "true"
    logger.info(f"服务配置: host=127.0.0.1, port=8000, reload={reload_mode}")

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=reload_mode,  # 使用环境变量控制
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
