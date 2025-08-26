# app/api/v1/grades.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.gpa import (
    GPACalculateRequest,
    GradesResponse,  # 注意：此模型可能需要根据新的返回结构进行调整
    GPACalculateResponse,
    SemesterResponse,
    ErrorResponse,
)
from app.services.scraper import (
    get_grades,
    get_available_semesters,
    calculate_gpa_advanced,
)
from app.services.base import get_user_session, BaseEducationService
from loguru import logger

router = APIRouter()


def handle_scraper_error(result: dict, operation_name: str = "操作"):
    """统一处理爬虫函数返回的错误"""
    if not result.get("success", False):
        error_msg = f"{operation_name}失败: {result.get('message', '教务系统错误')}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail=error_msg,
        )


@router.get(
    "/grades",
    response_model=GradesResponse,  # 建议根据新结构调整此模型
    summary="获取用户全部成绩和GPA分析",
    description="""
获取当前登录用户的全部课程成绩，并返回精简且修正后的GPA分析结果。

**核心变更:**
- 修复了学年/学期GPA未考虑重修情况的BUG。
- 移除了冗余的`gpa_analysis`和`effective_gpa`字段，结构更清晰。

**返回字段说明:**
- `data`: 包含所有课程的 **原始** 详细成绩信息。
- `basic_gpa`: 基于 **全部原始成绩** 计算的加权平均绩点、总学分等。
- `effective_gpa`: **去除重修/补考，只取课程最高绩点** 后计算的有效加权平均绩点。
- `yearly_gpa`: 基于 **有效绩点** 规则，按学年统计的绩点信息。
- `semester_gpa`: 基于 **有效绩点** 规则，按学期统计的绩点信息。
""",
    tags=["成绩"],
    responses={
        200: {
            "description": "成功获取成绩和修正后的GPA分析",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "成功获取15条原始成绩记录",
                        "data": [
                            {
                                "index": "1",
                                "semester": "2023-2024-1",
                                "courseCode": "CS001",
                                "courseName": "数据结构",
                                "score": "90",
                                "credit": "4.0",
                                "gpa": "4.0",
                                "examType": "正常考试",
                            }
                        ],
                        "basic_gpa": {
                            "weighted_gpa": 3.85,
                            "total_credit": 32.0,
                            "course_count": 10,
                        },
                        "effective_gpa": {
                            "weighted_gpa": 3.92,
                            "total_credit": 28.0,
                            "course_count": 9,
                        },
                        "yearly_gpa": {
                            "2023-2024": {
                                "weighted_gpa": 3.92,
                                "total_credit": 28.0,
                                "course_count": 9,
                            }
                        },
                        "semester_gpa": {
                            "2023-2024-1": {
                                "weighted_gpa": 4.0,
                                "total_credit": 16.0,
                                "course_count": 5,
                            },
                            "2023-2024-2": {
                                "weighted_gpa": 3.85,
                                "total_credit": 12.0,
                                "course_count": 4,
                            },
                        },
                    }
                }
            },
        },
        401: {"description": "未登录或Token失效", "model": ErrorResponse},
        503: {"description": "教务系统服务不可用", "model": ErrorResponse},
    },
)
async def get_user_grades_with_gpa(
    session=Depends(get_user_session),
):
    """获取用户全部成绩和重构后的GPA分析"""
    try:
        logger.info("开始获取用户成绩和GPA分析...")
        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩")

        logger.info(f"成绩及GPA分析获取成功")
        grades_result["message"] = "这是一个确认代码已更新的测试消息"
        return grades_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户成绩过程中发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取成绩失败: {str(e)}")
    finally:
        BaseEducationService.close_session(session)


@router.post(
    "/gpa/calculate",
    response_model=GPACalculateResponse,
    summary="自定义GPA计算",
    description="""
根据用户指定的条件计算定制化的GPA结果。
- 支持选择指定课程进行GPA计算（通过课程序号）
- 支持去除重修补考记录，只保留最高成绩
""",
    tags=["成绩"],
    responses={
        200: {"description": "成功计算自定义GPA", "model": GPACalculateResponse},
        401: {"description": "未登录或Token失效", "model": ErrorResponse},
        503: {"description": "教务系统服务不可用", "model": ErrorResponse},
    },
)
async def calculate_custom_gpa(
    request: GPACalculateRequest, session=Depends(get_user_session)
):
    """自定义GPA计算"""
    try:
        logger.info(
            f"开始自定义GPA计算，选中课程: {request.include_indices}, 去重修: {request.remove_retakes}"
        )

        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩用于计算")

        grades_data = grades_result.get("data", [])
        logger.debug(f"获取到 {len(grades_data)} 条成绩记录")

        gpa_result = calculate_gpa_advanced(
            grades_data=grades_data,
            include_indices=request.include_indices,
            remove_retakes=request.remove_retakes,
        )

        if gpa_result.get("success") and "total_gpa" in gpa_result:
            gpa_result["data"] = gpa_result.pop("total_gpa")
            logger.info("自定义GPA计算完成")
        else:
            logger.warning(f"自定义GPA计算失败: {gpa_result.get('message')}")

        return gpa_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"自定义GPA计算过程中发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"GPA计算失败: {str(e)}")
    finally:
        BaseEducationService.close_session(session)


@router.get(
    "/semesters",
    response_model=SemesterResponse,
    summary="获取可用学期列表",
    description="获取教务系统中当前用户可查询的所有学期列表。",
    tags=["成绩"],
    responses={
        200: {"description": "成功获取学期列表", "model": SemesterResponse},
        401: {"description": "未登录或Token失效", "model": ErrorResponse},
        503: {"description": "教务系统服务不可用", "model": ErrorResponse},
    },
)
async def get_semesters(session=Depends(get_user_session)):
    """获取可用学期列表"""
    try:
        logger.info("开始获取用户可用学期列表...")
        semesters_result = get_available_semesters(session=session)
        handle_scraper_error(semesters_result, "获取学期列表")

        logger.info(
            f"学期列表获取成功，共 {len(semesters_result.get('data', []))} 个学期"
        )
        return semesters_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取学期列表过程中发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取学期列表失败: {str(e)}")
    finally:
        BaseEducationService.close_session(session)
