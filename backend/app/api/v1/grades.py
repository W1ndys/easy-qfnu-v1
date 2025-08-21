# app/api/v1/grades.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.gpa import (
    GPACalculateRequest,
    GradesResponse,
    GPACalculateResponse,
    SemesterResponse,
    ErrorResponse,
)
from app.services.scraper import (
    get_grades,
    get_available_semesters,
    calculate_gpa_advanced,
)
from app.services.base_service import get_user_session, BaseEducationService
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
    response_model=GradesResponse,
    summary="获取用户全部成绩和GPA分析",
    description="""
获取当前登录用户的全部课程成绩，并返回详细的GPA分析结果。

**功能特点：**
- 获取用户所有学期的课程成绩明细
- 自动计算基础GPA和去除重修后GPA
- 提供详细的学分统计和课程数量信息
- 支持按学期、学年维度的GPA分析
- 计算每个学期的加权平均绩点
- 计算每个学年的加权平均绩点  
- 提供总的有效加权绩点（去除重修补考，取最高绩点）

**认证要求：**
- 需要携带有效的JWT Token（Authorization: Bearer <token>）
- Token必须是通过登录接口获取的有效令牌

**返回数据说明：**
- `data`: 包含所有课程的详细成绩信息
- `gpa_analysis`: 包含基础GPA和去重修GPA的分析结果
- `semester_gpa`: 按学期分组的GPA分析结果
- `yearly_gpa`: 按学年分组的GPA分析结果
- `effective_gpa`: 总的有效加权绩点（去除重修补考，取最高绩点）
- `total_courses`: 总课程数量

**数据更新：**
- 数据直接从教务系统实时获取，确保信息准确性
- 如教务系统更新成绩，下次调用即可获取最新数据
""",
    tags=["成绩"],
    responses={
        200: {
            "description": "成功获取成绩和GPA分析",
            "model": GradesResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "成功获取15条成绩记录",
                        "data": [
                            {
                                "index": "1",
                                "semester": "2023-2024-1",
                                "courseCode": "CS001",
                                "courseName": "数据结构",
                                "groupName": "",
                                "score": "90",
                                "scoreTag": "正常考试",
                                "credit": "4.0",
                                "totalHours": "64",
                                "gpa": "4.0",
                                "retakeSemester": "",
                                "assessmentMethod": "考试",
                                "examType": "正常考试",
                                "courseAttribute": "必修",
                                "courseNature": "专业课",
                                "courseCategory": "专业核心课",
                            }
                        ],
                        "gpa_analysis": {
                            "basic_gpa": {
                                "weighted_gpa": 3.85,
                                "total_credit": 32.0,
                                "course_count": 10,
                                "courses": [],
                            },
                            "no_retakes_gpa": {
                                "weighted_gpa": 3.92,
                                "total_credit": 28.0,
                                "course_count": 9,
                                "courses": [],
                            },
                        },
                        "semester_gpa": {
                            "2023-2024-1": {
                                "weighted_gpa": 3.8,
                                "total_credit": 16.0,
                                "course_count": 5,
                                "courses": [],
                            },
                            "2023-2024-2": {
                                "weighted_gpa": 3.9,
                                "total_credit": 16.0,
                                "course_count": 5,
                                "courses": [],
                            },
                        },
                        "yearly_gpa": {
                            "2023-2024": {
                                "weighted_gpa": 3.85,
                                "total_credit": 32.0,
                                "course_count": 10,
                                "courses": [],
                            },
                        },
                        "effective_gpa": {
                            "weighted_gpa": 3.92,
                            "total_credit": 28.0,
                            "course_count": 9,
                            "courses": [],
                        },
                        "total_courses": 15,
                    }
                }
            },
        },
        401: {
            "description": "未登录或Token失效",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "no_token": {
                            "summary": "未提供Token",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid_token": {
                            "summary": "Token无效或过期",
                            "value": {"detail": "Could not validate credentials"},
                        },
                        "session_expired": {
                            "summary": "教务系统Session过期",
                            "value": {"detail": "Session不存在或已失效，请重新登录"},
                        },
                    }
                }
            },
        },
        503: {
            "description": "教务系统服务不可用",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "获取成绩失败: 教务系统连接超时"}
                }
            },
        },
    },
)
async def get_user_grades_with_gpa(
    session=Depends(get_user_session),
):
    """
    获取用户全部成绩和GPA分析

    返回示例:
    {
        "success": true,
        "message": "成功获取成绩",
        "data": [...],  # 成绩列表
        "gpa": {...}    # GPA统计信息
    }
    """
    try:
        logger.info("开始获取用户成绩和GPA分析...")
        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩")

        logger.info(f"成绩获取成功，共 {grades_result.get('total_courses', 0)} 门课程")
        return grades_result
    except HTTPException:
        # 重新抛出HTTP异常
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

**功能特点：**
- 支持排除指定课程（通过课程序号）
- 支持去除重修补考记录，只保留最高成绩
- 灵活的GPA计算策略，满足不同评估需求
- 基于实时成绩数据进行计算

**使用场景：**
- 申请研究生时需要排除某些课程的GPA计算
- 计算专业核心课程的GPA
- 分析学术表现时去除重修影响
- 生成各种奖学金申请所需的GPA数据

**计算规则：**
- 使用学分加权平均方法计算GPA
- 排除的课程不参与GPA计算
- 开启去重修模式时，同一门课程只取最高成绩记录
""",
    tags=["成绩"],
    responses={
        200: {
            "description": "成功计算自定义GPA",
            "model": GPACalculateResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "GPA计算完成",
                        "data": {
                            "weighted_gpa": 3.75,
                            "total_credit": 28.0,
                            "course_count": 8,
                            "courses": [
                                {
                                    "course_name": "数据结构",
                                    "credit": 4.0,
                                    "grade_point": 4.0,
                                    "semester": "2023-2024-1",
                                }
                            ],
                        },
                    }
                }
            },
        },
        401: {"description": "未登录或Token失效", "model": ErrorResponse},
        422: {
            "description": "请求参数格式错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "exclude_indices"],
                                "msg": "ensure this value is greater than or equal to 0",
                                "type": "value_error.number.not_ge",
                            }
                        ]
                    }
                }
            },
        },
        503: {"description": "教务系统服务不可用", "model": ErrorResponse},
    },
)
async def calculate_custom_gpa(
    request: GPACalculateRequest, session=Depends(get_user_session)
):
    """
    自定义GPA计算

    根据用户提供的参数（排除课程、去除重修等）计算定制化的GPA结果。

    Args:
        request: GPA计算请求，包含排除课程列表和是否去除重修的配置
        session: 当前用户的教务系统会话（通过依赖注入获取）

    Returns:
        GPACalculateResponse: 包含计算结果的响应对象

    Raises:
        HTTPException: 当获取成绩失败或计算出错时抛出异常
    """
    try:
        logger.info(
            f"开始自定义GPA计算，排除课程: {request.exclude_indices}, 去重修: {request.remove_retakes}"
        )

        logger.debug("获取用户成绩数据用于GPA计算...")
        grades_result = get_grades(session=session, semester="")
        handle_scraper_error(grades_result, "获取成绩用于计算")

        grades_data = grades_result.get("data", [])
        logger.debug(f"获取到 {len(grades_data)} 条成绩记录")

        logger.debug("开始执行自定义GPA计算...")
        gpa_result = calculate_gpa_advanced(
            grades_data=grades_data,
            exclude_indices=request.exclude_indices,
            remove_retakes=request.remove_retakes,
        )

        # 修复响应格式，将 total_gpa 重命名为 data
        if gpa_result.get("success") and "total_gpa" in gpa_result:
            gpa_result["data"] = gpa_result.pop("total_gpa")
            logger.info("自定义GPA计算完成")
        else:
            logger.warning(f"自定义GPA计算失败: {gpa_result.get('message')}")

        return gpa_result
    except HTTPException:
        # 重新抛出HTTP异常
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
    description="""
获取教务系统中当前用户可查询的所有学期列表。

**功能说明：**
- 返回用户在教务系统中有课程记录的所有学期
- 学期格式为 "YYYY-YYYY-N"（如：2023-2024-1）
- 数据按时间顺序排列，最新学期在前

**学期格式说明：**
- 第一部分：学年起始年份（如2023）
- 第二部分：学年结束年份（如2024） 
- 第三部分：学期序号（1=第一学期，2=第二学期，3=夏季学期）

**使用场景：**
- 前端显示学期选择器
- 按学期筛选成绩数据
- 学期统计分析
- 用户学习进度跟踪

**注意事项：**
- 只返回有课程记录的学期
- 如果用户是新生，可能只有当前学期数据
""",
    tags=["成绩"],
    responses={
        200: {
            "description": "成功获取学期列表",
            "model": SemesterResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "成功获取5个学期",
                        "data": [
                            "2023-2024-2",
                            "2023-2024-1",
                            "2022-2023-2",
                            "2022-2023-1",
                            "2021-2022-2",
                        ],
                    }
                }
            },
        },
        401: {
            "description": "未登录或Token失效",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "no_token": {
                            "summary": "未提供Token",
                            "value": {"detail": "Not authenticated"},
                        },
                        "session_expired": {
                            "summary": "教务系统Session过期",
                            "value": {"detail": "Session不存在或已失效，请重新登录"},
                        },
                    }
                }
            },
        },
        503: {
            "description": "教务系统服务不可用",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "获取学期列表失败: 教务系统响应超时"}
                }
            },
        },
    },
)
async def get_semesters(session=Depends(get_user_session)):
    """
    获取可用学期列表

    从教务系统获取当前用户有课程记录的所有学期，用于前端筛选和统计分析。

    Args:
        session: 当前用户的教务系统会话（通过依赖注入获取）

    Returns:
        SemesterResponse: 包含学期列表的响应对象

    Raises:
        HTTPException: 当获取学期列表失败时抛出异常
    """
    try:
        logger.info("开始获取用户可用学期列表...")
        semesters_result = get_available_semesters(session=session)
        handle_scraper_error(semesters_result, "获取学期列表")

        logger.info(
            f"学期列表获取成功，共 {len(semesters_result.get('data', []))} 个学期"
        )
        return semesters_result
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"获取学期列表过程中发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取学期列表失败: {str(e)}")
    finally:
        BaseEducationService.close_session(session)
