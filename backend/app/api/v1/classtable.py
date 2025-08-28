# app/api/v1/classtable.py
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.schemas.gpa import ErrorResponse as GPAErrorResponse
from app.schemas.classtable import (
    ClassTableResponse,
    ClassTableInfoResponse,
    ErrorResponse,
)
from app.services.classtable import ClassTableService
from app.core.security import get_current_user
from app.services.classtable import ClassTableService
from app.services.base import get_user_session

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/classtable",
    summary="📅 获取课程表",
    description="""
    ## 获取指定日期所在周的课程表数据
    
    ### 功能说明
    - 📊 根据日期获取完整的一周课程表
    - 🔄 教务系统会自动返回该日期所在周的所有课程
    - 📱 返回前端友好的JSON格式，直接支持课程表组件渲染
    - ⏰ 如果不指定日期，将使用当前日期
    
    ### 数据特点
    - 📍 包含课程位置和时间信息，便于前端渲染
    - 📈 提供统计信息，如总课程数、每日分布等
    - 🕐 包含详细的时间段定义和精确的课程时间信息
    - 🔗 支持跨大节课程的自动去重和时间合并
    - 📋 保留原始数据，便于调试和扩展
    """,
    response_model=ClassTableResponse,
    responses={
        200: {
            "description": "✅ 课程表获取成功",
            "model": ClassTableResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "课程表获取成功",
                        "data": {
                            "week_info": {"current_week": 1, "total_weeks": 20},
                            "time_slots": [
                                {
                                    "period": 1,
                                    "name": "第一大节",
                                    "time": "08:00-09:40",
                                    "slots": [1, 2],
                                }
                            ],
                            "weekdays": [{"id": 1, "name": "星期一", "short": "周一"}],
                            "courses": [
                                {
                                    "id": "course_1",
                                    "name": "网络管理",
                                    "location": "嵌入式实验室204",
                                    "classroom": "嵌入式实验室204",
                                    "credits": "3",
                                    "course_type": "任选",
                                    "class_name": "23网安班,22网安班",
                                    "weeks": [1],
                                    "time_info": {
                                        "weekday": 1,
                                        "weekday_name": "星期一",
                                        "period": 1,
                                        "period_name": "第一大节",
                                        "time_slots": [2, 3, 4],
                                        "actual_periods": [2, 3, 4],
                                        "start_time": "08:55",
                                        "end_time": "11:40",
                                        "is_cross_period": True,
                                    },
                                    "style": {
                                        "row": 1,
                                        "col": 1,
                                        "row_span": 1,
                                        "col_span": 1,
                                    },
                                    "raw_data": {
                                        "course_name": "网络管理",
                                        "credits": "3",
                                        "course_type": "任选",
                                        "time_detail": "第1周 星期一 [02-03-04]节",
                                        "location": "嵌入式实验室204",
                                        "class_name": "23网安班,22网安班",
                                        "weeks": [1],
                                        "actual_periods": [2, 3, 4],
                                    },
                                }
                            ],
                            "stats": {
                                "total_courses": 1,
                                "total_hours": 2,
                                "courses_by_day": {"星期一": 1, "星期二": 0},
                            },
                        },
                    }
                }
            },
        },
        400: {"description": "❌ 请求参数错误", "model": ErrorResponse},
        401: {"description": "🔒 未授权访问或登录已过期", "model": ErrorResponse},
        500: {"description": "⚠️ 服务器内部错误", "model": ErrorResponse},
    },
    tags=["📚 课程表管理"],
)
async def get_class_table(
    date: Optional[str] = Query(
        None,
        description="📅 查询日期，格式：YYYY-MM-DD。教务系统会返回该日期所在周的完整课程表。如果不提供，则使用当前日期",
        example="2025-01-15",
        regex="^\\d{4}-\\d{2}-\\d{2}$",
    ),
    current_user: str = Depends(get_current_user),
):
    """
    获取课程表数据

    - **date**: 查询的日期，格式为 YYYY-MM-DD
    - 如果不提供日期，将使用当前日期
    - 教务系统会自动返回该日期所在周的完整课程表
    - 返回前端友好的课程表数据结构
    """
    try:
        # 获取用户hash用于日志记录
        user_hash = current_user

        # 如果没有提供日期，使用当前日期
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            logger.info(f"用户 {user_hash} 查询课程表，使用当前日期: {date}")
        else:
            logger.info(f"用户 {user_hash} 查询课程表，指定日期: {date}")

        # 获取用户session
        session = get_user_session(user_hash)
        if not session:
            logger.error(f"用户 {user_hash} 的session不存在或已过期")
            raise HTTPException(status_code=401, detail="用户会话已过期，请重新登录")

        # 调用课程表服务
        result = ClassTableService.get_class_table_data(session, date)

        if result["success"]:
            logger.info(f"用户 {user_hash} 课程表获取成功，日期: {date}")
            return {
                "success": True,
                "message": "课程表获取成功",
                "data": result["data"],
            }
        else:
            logger.warning(f"用户 {user_hash} 课程表获取失败: {result['message']}")
            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"获取课程表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取课程表失败: {str(e)}")


@router.get(
    "/classtable/current",
    summary="⏰ 获取当前周课程表",
    description="""
    ## 快速获取当前周课程表
    
    ### 功能说明
    - 🚀 便捷接口，无需指定日期参数
    - 📅 自动使用今天的日期获取课程表
    - 🔄 等同于调用 `/classtable` 而不指定日期参数
    - 📱 适合移动端和快速查询场景
    
    ### 使用场景
    - 📲 移动端应用的"今日课程"功能
    - 🏠 首页显示当前周课程概览
    - ⚡ 快速查询，无需计算日期
    """,
    response_model=ClassTableResponse,
    responses={
        200: {"description": "✅ 当前周课程表获取成功", "model": ClassTableResponse},
        401: {"description": "🔒 未授权访问或登录已过期", "model": ErrorResponse},
        500: {"description": "⚠️ 服务器内部错误", "model": ErrorResponse},
    },
    tags=["📚 课程表管理"],
)
async def get_current_class_table(
    current_user: str = Depends(get_current_user),
):
    """
    获取当前周的课程表数据

    - 自动使用当前日期查询课程表
    - 教务系统返回当前日期所在周的完整课程表
    - 便捷接口，等同于不带参数调用 /classtable
    """
    try:
        user_hash = current_user
        logger.info(f"用户 {user_hash} 查询当前周课程表")

        # 获取用户session
        session = get_user_session(user_hash)
        if not session:
            logger.error(f"用户 {user_hash} 的session不存在或已过期")
            raise HTTPException(status_code=401, detail="用户会话已过期，请重新登录")

        # 调用便捷方法
        result = ClassTableService.get_current_week_class_table(session)

        if result["success"]:
            logger.info(f"用户 {user_hash} 当前周课程表获取成功")
            return {
                "success": True,
                "message": "当前周课程表获取成功",
                "data": result["data"],
            }
        else:
            logger.warning(
                f"用户 {user_hash} 当前周课程表获取失败: {result['message']}"
            )
            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前周课程表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取当前周课程表失败: {str(e)}")


@router.get(
    "/classtable/info",
    summary="ℹ️ 获取课程表基础信息",
    description="""
    ## 获取课程表配置信息
    
    ### 功能说明
    - 📋 返回课程表的基础配置信息
    - ⏰ 包含时间段定义（第一大节、第二大节等）
    - 📅 包含星期定义（星期一到星期日）
    - 🛠️ 用于前端初始化课程表组件
    
    ### 返回数据
    - **time_slots**: 6个时间段的完整定义
    - **weekdays**: 7天的完整定义
    
    ### 使用场景
    - 🔧 前端组件初始化
    - 📱 移动端课程表框架搭建
    - 🎨 课程表UI渲染配置
    
    ### 特点
    - 🌐 无需登录认证
    - ⚡ 快速响应
    - 📊 静态配置数据
    """,
    response_model=ClassTableInfoResponse,
    responses={
        200: {
            "description": "✅ 基础信息获取成功",
            "model": ClassTableInfoResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "课程表基础信息获取成功",
                        "data": {
                            "time_slots": [
                                {
                                    "period": 1,
                                    "name": "第一大节",
                                    "time": "08:00-09:40",
                                    "slots": [1, 2],
                                },
                                {
                                    "period": 2,
                                    "name": "第二大节",
                                    "time": "10:00-11:40",
                                    "slots": [3, 4],
                                },
                                {
                                    "period": 3,
                                    "name": "第三大节",
                                    "time": "14:00-15:40",
                                    "slots": [5, 6],
                                },
                                {
                                    "period": 4,
                                    "name": "第四大节",
                                    "time": "16:00-17:40",
                                    "slots": [7, 8],
                                },
                                {
                                    "period": 5,
                                    "name": "第五大节",
                                    "time": "19:00-21:30",
                                    "slots": [9, 10, 11],
                                },
                                {
                                    "period": 6,
                                    "name": "网课时段",
                                    "time": "自由安排",
                                    "slots": [12, 13],
                                },
                            ],
                            "weekdays": [
                                {"id": 1, "name": "星期一", "short": "周一"},
                                {"id": 2, "name": "星期二", "short": "周二"},
                                {"id": 3, "name": "星期三", "short": "周三"},
                                {"id": 4, "name": "星期四", "short": "周四"},
                                {"id": 5, "name": "星期五", "short": "周五"},
                                {"id": 6, "name": "星期六", "short": "周六"},
                                {"id": 7, "name": "星期日", "short": "周日"},
                            ],
                        },
                    }
                }
            },
        },
        500: {"description": "⚠️ 服务器内部错误", "model": ErrorResponse},
    },
    tags=["📚 课程表管理"],
)
async def get_class_table_info():
    """
    获取课程表基础信息

    - 返回时间段定义
    - 返回星期定义
    - 用于前端初始化课程表结构
    """
    try:
        logger.info("获取课程表基础信息")

        return {
            "success": True,
            "message": "课程表基础信息获取成功",
            "data": {
                "time_slots": [
                    {
                        "period": 1,
                        "name": "第一大节",
                        "time": "08:00-09:40",
                        "slots": [1, 2],
                    },
                    {
                        "period": 2,
                        "name": "第二大节",
                        "time": "10:00-11:40",
                        "slots": [3, 4],
                    },
                    {
                        "period": 3,
                        "name": "第三大节",
                        "time": "14:00-15:40",
                        "slots": [5, 6],
                    },
                    {
                        "period": 4,
                        "name": "第四大节",
                        "time": "16:00-17:40",
                        "slots": [7, 8],
                    },
                    {
                        "period": 5,
                        "name": "第五大节",
                        "time": "19:00-21:30",
                        "slots": [9, 10, 11],
                    },
                    {
                        "period": 6,
                        "name": "网课时段",
                        "time": "自由安排",
                        "slots": [12, 13],
                    },
                ],
                "weekdays": [
                    {"id": 1, "name": "星期一", "short": "周一"},
                    {"id": 2, "name": "星期二", "short": "周二"},
                    {"id": 3, "name": "星期三", "short": "周三"},
                    {"id": 4, "name": "星期四", "short": "周四"},
                    {"id": 5, "name": "星期五", "short": "周五"},
                    {"id": 6, "name": "星期六", "short": "周六"},
                    {"id": 7, "name": "星期日", "short": "周日"},
                ],
            },
        }

    except Exception as e:
        logger.error(f"获取课程表基础信息时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取课程表基础信息失败: {str(e)}")
