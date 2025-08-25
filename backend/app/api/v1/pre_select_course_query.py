# app/api/v1/pre_select_course_query.py
from typing import Optional, Any, List, Dict

from fastapi import APIRouter, Depends
import requests
from pydantic import BaseModel, Field

from app.services.base import get_user_session, BaseEducationService
from app.services.pre_select_course_query import pre_select_course_query

router = APIRouter(tags=["预选课查询"])


class PreSelectCourseQueryRequest(BaseModel):
    course_id_or_name: str = Field(
        ..., description="课程名称或课程ID", example="大学物理B 或 PHY1001"
    )
    teacher_name: Optional[str] = Field(None, description="教师姓名", example="张三")
    week_day: Optional[str] = Field(
        None, description="上课星期(1-7 或 中文周几)", example="3"
    )
    class_period: Optional[str] = Field(
        None, description="上课节次(起止或单节)", example="3-4"
    )
    select_semester: Optional[str] = Field(
        None, description="选课学期(可选)", example="2024-2025-1"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "course_id_or_name": "大学英语A",
                "teacher_name": "李四",
                "week_day": "2",
                "class_period": "1-2",
                "select_semester": "2024-2025-1",
            }
        }


class ModuleResult(BaseModel):
    module: str = Field(
        ..., description="模块标识，如 knjxk/bxqjhxk/xxxk/ggxxkxk/fawxk"
    )
    module_name: str = Field(..., description="模块名称")
    count: int = Field(..., description="该模块返回的课程条目数")
    aaData: List[Dict[str, Any]] = Field(..., description="原始课程数据数组")


class QueryErrorItem(BaseModel):
    module: str = Field(..., description="发生错误的模块标识")
    status: int = Field(..., description="HTTP状态码或-1")
    message: str = Field(..., description="错误描述")


class PreSelectCourseQueryData(BaseModel):
    jx0502zbid: str = Field(..., description="选课轮次编号")
    modules: List[ModuleResult] = Field(..., description="各模块的查询结果")
    errors: List[QueryErrorItem] = Field(
        default_factory=list, description="查询过程中产生的错误列表"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "jx0502zbid": "a1b2c3d4e5",
                "modules": [
                    {
                        "module": "bxqjhxk",
                        "module_name": "本学期计划选课",
                        "count": 1,
                        "aaData": [
                            {
                                "kch": "PHY1001",
                                "kcmc": "大学物理B",
                                "skls": "张三",
                                "sksj": "1-16周 周三 3-4节",
                                "xkrs": "60",
                                "syrs": "10",
                                "czOper": "...",
                            }
                        ],
                    }
                ],
                "errors": [
                    {"module": "ggxxkxk", "status": 404, "message": "接口未开放/不存在"}
                ],
            }
        }


class PreSelectCourseQueryResponse(BaseModel):
    ok: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    data: PreSelectCourseQueryData = Field(..., description="查询结果数据体")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误信息")


@router.post(
    "/pre-select-course/query",
    response_model=PreSelectCourseQueryResponse,
    summary="预选课查询",
    description="根据课程名称或课程ID(必填)，可选的教师、上课星期、上课节次进行查询。会遍历多个选课模块并返回结果与模块来源。",
    responses={
        401: {"model": ErrorResponse, "description": "未授权或Session失效"},
        403: {"model": ErrorResponse, "description": "无权限"},
        404: {"model": ErrorResponse, "description": "接口未开放/不存在或未找到"},
        502: {"model": ErrorResponse, "description": "教务系统服务异常"},
        503: {"model": ErrorResponse, "description": "教务系统连接超时"},
        504: {"model": ErrorResponse, "description": "请求超时"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
)
def pre_select_course_query_api(
    payload: PreSelectCourseQueryRequest,
    session: requests.Session = Depends(get_user_session),
):
    """
    - 需要已登录的教务系统Session（通过鉴权后自动注入）
    - 查询顺序：专业内跨年级、本学期计划、选修、公选、计划外
    """
    try:
        data_dict = pre_select_course_query(
            session=session,
            course_id_or_name=payload.course_id_or_name,
            teacher_name=payload.teacher_name,
            week_day=payload.week_day,
            class_period=payload.class_period,
            select_semester=payload.select_semester,
        )
        return {
            "ok": True,
            "message": "查询成功",
            "data": data_dict,
        }
    except Exception as e:
        raise BaseEducationService.handle_service_error(e, operation_name="预选课查询")
