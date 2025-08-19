# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException
from app.schemas.user import UserLogin, Token
from app.services.scraper import login_to_university
from app.db.database import save_session

# ⬇️ 导入我们新建的 create_access_token 函数
from app.core.security import create_access_token

router = APIRouter()


@router.post("/login", response_model=Token, summary="用户登录获取Token")
async def login_for_access_token(form_data: UserLogin):
    """
    用户登录接口。
    验证成功后，保存session并返回JWT Token。
    """
    session = login_to_university(
        student_id=form_data.student_id, password=form_data.password
    )

    if session is None:
        raise HTTPException(status_code=401, detail="学号或密码错误，登录失败")

    try:
        # 登录成功后，将 session 的 cookies 保存到数据库
        save_session(student_id=form_data.student_id, session_obj=session)
    finally:
        session.close()

    # ⬇️ 调用封装好的函数来创建Token
    access_token = create_access_token(data={"sub": form_data.student_id})

    return {"access_token": access_token, "token_type": "bearer"}
