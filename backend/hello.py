# hello.py (这是完整修改后的文件)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt

# 1. 从我们的业务逻辑文件中导入登录函数
from scraper import login_to_university

app = FastAPI()


class UserLogin(BaseModel):
    student_id: str
    password: str


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# ... 其他GET接口 ...


@app.post("/login/")
async def login(form_data: UserLogin):
    # 2. 调用真实的登录函数
    success = login_to_university(
        student_id=form_data.student_id, password=form_data.password
    )

    # 3. 根据登录结果，返回不同响应
    if not success:
        # 如果登录失败，抛出一个HTTPException
        # 这会自动向前端返回一个 401 Unauthorized 错误
        raise HTTPException(status_code=401, detail="学号或密码错误，登录失败")

    # 如果登录成功，生成一个(伪)JWT Token
    # 这里的 "YOUR_SECRET_KEY" 应该是一个复杂且保密的字符串
    token_data = {"sub": form_data.student_id}
    access_token = jwt.encode(token_data, "YOUR_SECRET_KEY", algorithm="HS256")

    return {"access_token": access_token, "token_type": "bearer"}
