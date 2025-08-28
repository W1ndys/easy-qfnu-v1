# app/api/v1/classtable.py
from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger
import requests
from datetime import datetime

from app.services.classtable import ClassTableService
from app.services.base import get_user_session
from app.schemas.classtable import DayClassTableResponse, WeekClassTableResponse

# 创建路由器
router = APIRouter()


@router.get(
    "/classtable/today",
    response_model=DayClassTableResponse,
    summary="获取今天的课程表",
    description="""
    获取当前日期的课程表信息
    
    ## 功能说明
    - 自动获取当前系统日期的课程安排
    - 返回当天所有课程的详细信息
    - 包含课程时间、地点、学分等完整信息
    
    ## 返回数据包含
    - 课程名称和学分
    - 课程属性（必修/选修等）
    - 上课时间和节次
    - 上课地点
    - 课堂名称
    
    ## 使用场景
    - 学生查看今日课程安排
    - 快速了解当天上课情况
    - 移动端今日课程提醒
    """,
    tags=["课程表"],
    responses={
        200: {
            "description": "成功获取今日课程表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "今日课程表获取成功",
                        "data": {
                            "date": "2025-01-15",
                            "day_of_week": 3,
                            "courses": [
                                {
                                    "course_name": "数据结构",
                                    "course_credits": "3",
                                    "course_property": "必修",
                                    "class_time": "第1周 星期三 [01-02]节",
                                    "classroom": "教学楼A101",
                                    "class_name": "计算机科学与技术2023-1班",
                                    "day_of_week": 3,
                                    "period": "01-02",
                                }
                            ],
                        },
                    }
                }
            },
        },
        401: {
            "description": "用户未登录或登录已过期",
            "content": {
                "application/json": {"example": {"detail": "用户未登录或登录已过期"}}
            },
        },
        503: {
            "description": "教务系统连接失败",
            "content": {
                "application/json": {
                    "example": {"detail": "教务系统连接失败: 连接超时"}
                }
            },
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {"detail": "获取课程表失败: 解析数据错误"}
                }
            },
        },
    },
)
async def get_today_classtable(session: requests.Session = Depends(get_user_session)):
    """
    获取今天的课程表

    ## 接口说明
    此接口自动获取当前日期的课程信息，无需传入任何参数。

    ## 认证要求
    需要用户已登录教务系统，通过session验证身份。

    ## 数据来源
    实时从教务系统获取最新的课程表数据。

    ## 返回字段说明
    - **date**: 日期，格式为 YYYY-MM-DD
    - **day_of_week**: 星期几，1-7分别代表周一到周日
    - **courses**: 当天课程列表
        - **course_name**: 课程名称
        - **course_credits**: 课程学分
        - **course_property**: 课程属性（必修/选修/任选等）
        - **class_time**: 上课时间描述
        - **classroom**: 上课地点
        - **class_name**: 课堂名称（班级信息）
        - **day_of_week**: 星期几
        - **period**: 节次信息（如"01-02"表示第1-2节）

    ## 特殊情况
    - 如果当天没有课程，courses数组为空
    - 如果系统维护，会返回503错误
    - 节假日可能返回空课程表
    """
    try:
        # 获取当前日期
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"收到今日课程表查询请求，日期: {today}")

        # 调用服务获取当天课程
        day_courses = ClassTableService.get_day_courses(session, today)

        logger.info(
            f"今日课程表查询成功，日期: {today}, 课程数: {len(day_courses.courses)}"
        )
        return DayClassTableResponse(
            success=True, message="今日课程表获取成功", data=day_courses
        )

    except Exception as e:
        logger.error(f"今日课程表查询过程中发生错误: {e}")
        error = ClassTableService.handle_service_error(e, "今日课程表查询")
        raise error


@router.get(
    "/classtable/week",
    response_model=WeekClassTableResponse,
    summary="获取指定日期所在周的课程表",
    description="""
    获取指定日期所在周的完整课程表信息
    
    ## 功能说明
    - 根据传入的日期，获取该日期所在周的完整课程表
    - 返回一周七天的完整课程安排
    - 自动计算周数和周的起止日期
    
    ## 参数说明
    - **query_date**: 查询日期，格式为 YYYY-MM-DD
    - 可以是一周中的任意一天，系统会自动计算整周范围
    
    ## 返回数据包含
    - 周数信息
    - 周的起止日期
    - 一周七天的课程详情
    - 每天的课程列表
    
    ## 使用场景
    - 查看完整周课程表
    - 课程表展示界面
    - 周计划安排
    """,
    tags=["课程表"],
    responses={
        200: {
            "description": "成功获取周课程表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "周课程表获取成功",
                        "data": {
                            "week_number": 3,
                            "start_date": "2025-01-13",
                            "end_date": "2025-01-19",
                            "days": [
                                {
                                    "date": "2025-01-13",
                                    "day_of_week": 1,
                                    "courses": [
                                        {
                                            "course_name": "高等数学",
                                            "course_credits": "4",
                                            "course_property": "必修",
                                            "class_time": "第3周 星期一 [01-02]节",
                                            "classroom": "教学楼B201",
                                            "class_name": "数学2023-1班",
                                            "day_of_week": 1,
                                            "period": "01-02",
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                }
            },
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {"detail": "日期格式无效，请使用 YYYY-MM-DD 格式"}
                }
            },
        },
        401: {"description": "用户未登录或登录已过期"},
        503: {"description": "教务系统连接失败"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_week_classtable(
    query_date: str = Query(
        ...,
        description="查询日期，格式：YYYY-MM-DD。可以是一周中的任意一天，系统会自动计算整周范围。",
        example="2025-01-15",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    ),
    session: requests.Session = Depends(get_user_session),
):
    """
    获取指定日期所在周的完整课程表

    ## 接口说明
    根据传入的日期，获取该日期所在周（周一到周日）的完整课程表信息。

    ## 参数详解
    - **query_date**: 查询日期
        - 格式：YYYY-MM-DD
        - 示例：2025-01-15
        - 可以是一周中的任意一天
        - 系统会自动计算该日期所在周的周一到周日

    ## 认证要求
    需要用户已登录教务系统，通过session验证身份。

    ## 数据来源
    实时从教务系统获取最新的课程表数据。

    ## 返回字段说明
    ### 外层结构
    - **week_number**: 周数（第几周）
    - **start_date**: 本周开始日期（周一）
    - **end_date**: 本周结束日期（周日）
    - **days**: 一周七天的课程数组

    ### 每天课程结构 (days数组元素)
    - **date**: 该天日期，格式为 YYYY-MM-DD
    - **day_of_week**: 星期几，1-7分别代表周一到周日
    - **courses**: 该天的课程列表

    ### 课程信息结构 (courses数组元素)
    - **course_name**: 课程名称
    - **course_credits**: 课程学分
    - **course_property**: 课程属性
        - 必修：必修课程
        - 选修：专业选修
        - 任选：任意选修
        - 其他：按教务系统实际返回
    - **class_time**: 上课时间完整描述
        - 格式：第X周 星期X [XX-XX]节
        - 示例：第3周 星期一 [01-02]节
    - **classroom**: 上课地点/教室
    - **class_name**: 课堂名称（通常包含班级信息）
    - **day_of_week**: 星期几（与父级day_of_week一致）
    - **period**: 节次信息
        - 格式：XX-XX
        - 示例：01-02（第1-2节）

    ## 特殊情况处理
    - 某天没有课程时，该天的courses数组为空
    - 节假日或调课时按教务系统实际安排返回
    - 跨周课程会在对应周显示

    ## 前端使用建议
    1. **表格展示**: 可以按照days数组构建7列的周课程表
    2. **日历视图**: 使用date字段与日历组件结合
    3. **课程提醒**: 根据period字段设置课程提醒时间
    4. **筛选功能**: 可按course_property过滤必修/选修课程
    5. **详情展示**: 点击课程可显示classroom、class_name等详细信息

    ## 错误处理
    - 400: 日期格式错误，请检查是否为YYYY-MM-DD格式
    - 401: 用户未登录，需要重新登录
    - 503: 教务系统连接失败，可稍后重试
    - 500: 服务器错误，联系管理员
    """
    try:
        logger.info(f"收到周课程表查询请求，日期: {query_date}")

        # 验证日期格式
        try:
            datetime.strptime(query_date, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"无效的日期格式: {query_date}")
            raise HTTPException(
                status_code=400, detail="日期格式无效，请使用 YYYY-MM-DD 格式"
            )

        # 调用服务获取周课程表
        week_courses = ClassTableService.get_week_courses(session, query_date)

        logger.info(
            f"周课程表查询成功，日期: {query_date}, 周数: {week_courses.week_number}"
        )
        return WeekClassTableResponse(
            success=True, message="周课程表获取成功", data=week_courses
        )

    except Exception as e:
        logger.error(f"周课程表查询过程中发生错误: {e}")
        error = ClassTableService.handle_service_error(e, "周课程表查询")
        raise error
