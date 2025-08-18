# hello.py (集成了数据库操作的最终版本)

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
from fastapi import Depends
from scraper import login_to_university, get_grades, calculate_gpa_advanced
from database import save_session, get_session
from auth import get_current_user


app = FastAPI()


class UserLogin(BaseModel):
    student_id: str
    password: str


class GPACalculateRequest(BaseModel):
    semester: str = ""  # 空字符串表示全部学期
    exclude_indices: list[int] = []  # 要排除的课程序号列表
    remove_retakes: bool = False  # 是否去除重修补考，取最高绩点


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/login/")
async def login(form_data: UserLogin):
    session = login_to_university(
        student_id=form_data.student_id, password=form_data.password
    )

    if session is None:
        raise HTTPException(status_code=401, detail="学号或密码错误，登录失败")

    # --- 2. 关键修改点 ---
    try:
        # 登录成功后，将 session 对象保存到数据库
        save_session(student_id=form_data.student_id, session_obj=session)
    finally:
        # 无论如何，关闭这个临时的 session 对象，因为它已经被序列化保存了
        session.close()

    token_data = {"sub": form_data.student_id}
    access_token = jwt.encode(token_data, "1111", algorithm="HS256")

    return {"access_token": access_token, "token_type": "bearer"}


# --- 5. 创建新的 /grades 接口 ---
@app.get("/grades/")
async def read_user_grades(student_id: str = Depends(get_current_user)):
    """
    获取当前登录用户的成绩。
    这个接口受 get_current_user 依赖保护。
    """
    # 因为通过了“安检”，我们已经拿到了验证过的 student_id
    print(f"正在为学号 {student_id} 查询成绩...")

    # 从数据库获取该用户的 session
    session = get_session(student_id=student_id)
    if session is None:
        # 如果数据库里没有session，说明需要重新登录
        raise HTTPException(status_code=401, detail="Session不存在或已失效，请重新登录")

    # 使用 session 获取成绩
    grades_data = get_grades(session=session)
    session.close()  # 使用完后关闭

    if grades_data is None:
        # 爬取失败，可能是学校官网问题或session真的过期了
        # 这里也引导用户重新登录，可以刷新session
        raise HTTPException(
            status_code=500, detail="获取成绩失败，请稍后重试或重新登录"
        )

    return {"student_id": student_id, "grades": grades_data}


@app.post("/calculate-gpa/")
async def calculate_custom_gpa(
    request: GPACalculateRequest, student_id: str = Depends(get_current_user)
):
    """
    自定义GPA计算接口。
    支持指定学期、排除特定课程、处理重修补考等功能。
    """
    print(f"正在为学号 {student_id} 计算自定义GPA...")

    # 从数据库获取该用户的 session
    session = get_session(student_id=student_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Session不存在或已失效，请重新登录")

    # 获取成绩数据
    grades_result = get_grades(session=session, semester=request.semester)
    session.close()

    if not grades_result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=f"获取成绩失败: {grades_result.get('message', '未知错误')}",
        )

    grades_data = grades_result.get("data", [])

    # 计算自定义GPA
    gpa_result = calculate_gpa_advanced(
        grades_data=grades_data,
        exclude_indices=request.exclude_indices,
        remove_retakes=request.remove_retakes,
    )

    return {
        "student_id": student_id,
        "request_params": {
            "semester": request.semester if request.semester else "全部学期",
            "excluded_courses": len(request.exclude_indices),
            "remove_retakes": request.remove_retakes,
        },
        "gpa_result": gpa_result,
        "total_courses_analyzed": len(grades_data),
    }


@app.get("/semesters/")
async def get_available_semesters_api(student_id: str = Depends(get_current_user)):
    """
    获取可用的学期列表。
    """
    from scraper import get_available_semesters

    # 从数据库获取该用户的 session
    session = get_session(student_id=student_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Session不存在或已失效，请重新登录")

    # 获取学期列表
    semesters_result = get_available_semesters(session=session)
    session.close()

    return {"student_id": student_id, "semesters": semesters_result}


if __name__ == "__main__":
    uvicorn.run("hello:app", host="127.0.0.1", port=8000, reload=True)
