# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth as auth_router
from app.api.v1 import grades as grades_router
from app.db.database import init_db

# 创建FastAPI应用实例
app = FastAPI(title="Easy-QFNUJW API", version="1.0.0")

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Easy-QFNUJW API"}


# 使用 include_router 将各个API模块挂载到主应用上
# prefix="/api/v1" 表示这个模块下所有接口的URL都会以/api/v1开头
# tags=["认证"] 用于在API文档中进行分组，非常方便
app.include_router(auth_router.router, prefix="/api/v1", tags=["认证"])
app.include_router(grades_router.router, prefix="/api/v1", tags=["成绩"])

if __name__ == "__main__":
    # 这里的 "app.main:app" 指向的是 app文件夹下的main.py文件中的app实例
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
