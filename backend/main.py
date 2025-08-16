"""
Easy-QFNUJW 微信小程序后端主程序
FastAPI + SQLite 架构
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, grades, schedule, stats
from app.core.security import verify_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时清理资源（如果需要）


# 创建FastAPI应用实例
app = FastAPI(
    title="Easy-QFNUJW API",
    description="曲阜师范大学教务辅助工具后端API",
    version="4.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT认证依赖
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """验证JWT令牌并获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# 注册路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(
    grades.router,
    prefix="/api",
    tags=["成绩查询"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    schedule.router,
    prefix="/api",
    tags=["课表查询"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    stats.router,
    prefix="/api",
    tags=["数据统计"],
    dependencies=[Depends(get_current_user)],
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Easy-QFNUJW API Server", "version": "4.0.0"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "easy-qfnujw-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
