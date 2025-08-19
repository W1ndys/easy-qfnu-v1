# app/main.py
import uvicorn
from fastapi import FastAPI
from app.api.v1 import auth as auth_router
from app.api.v1 import grades as grades_router

# 创建FastAPI应用实例
app = FastAPI(title="Easy-QFNUJW API", version="1.0.0")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Easy-QFNUJW API"}


# 使用 include_router 将各个API模块挂载到主应用上
# prefix="/api/v1" 表示这个模块下所有接口的URL都会以/api/v1开头
# tags=["Authentication"] 用于在API文档中进行分组，非常方便
app.include_router(auth_router.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(grades_router.router, prefix="/api/v1", tags=["Grades & GPA"])

if __name__ == "__main__":
    # 这里的 "app.main:app" 指向的是 app文件夹下的main.py文件中的app实例
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
