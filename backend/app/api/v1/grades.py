# app/api/v1/grades.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.gpa import GPACalculateRequest
from app.services.scraper import (
    get_grades,
    get_available_semesters,
    calculate_gpa_advanced,
)
from app.db.database import get_session
from app.core.security import get_current_user

router = APIRouter()


# 这是一个可复用的依赖项，用于获取有效的session
def get_user_session(student_id: str = Depends(get_current_user)):
    """依赖项：获取当前用户的教务系统session"""
    session = get_session(student_id=student_id)
    if session is None:
        raise HTTPException(status_code=401, detail="Session不存在或已失效，请重新登录")
    return session


def handle_scraper_error(result: dict, operation_name: str = "操作"):
    """统一处理爬虫函数返回的错误"""
    if not result.get("success", False):
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail=f"{operation_name}失败: {result.get('message', '教务系统错误')}",
        )


@router.get("/grades")
async def get_user_grades_with_gpa(session=Depends(get_user_session)):
    """获取用户全部成绩和GPA分析"""
    try:
        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩")
        return grades_result
    finally:
        session.close()


@router.post("/gpa/calculate")
async def calculate_custom_gpa(
    request: GPACalculateRequest, session=Depends(get_user_session)
):
    """自定义GPA计算"""
    try:
        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩用于计算")

        grades_data = grades_result.get("data", [])
        gpa_result = calculate_gpa_advanced(
            grades_data=grades_data,
            exclude_indices=request.exclude_indices,
            remove_retakes=request.remove_retakes,
        )
        return gpa_result
    finally:
        session.close()


@router.get("/semesters")
async def get_semesters(session=Depends(get_user_session)):
    """获取可用学期列表"""
    try:
        semesters_result = get_available_semesters(session=session)
        handle_scraper_error(semesters_result, "获取学期列表")
        return semesters_result
    finally:
        session.close()
