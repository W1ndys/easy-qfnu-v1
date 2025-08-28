# app/api/v1/pre_select_course_query.py
from typing import Optional, Any, List, Dict

from fastapi import APIRouter, Depends
import requests
from pydantic import BaseModel, Field, model_validator

from app.services.base import get_user_session, BaseEducationService
from app.services.pre_select_course_query import pre_select_course_query
from app.services.profile import ProfileService
from app.services.course_query_logger import CourseQueryLogger
from loguru import logger

router = APIRouter(tags=["预选课查询"])


class PreSelectCourseQueryRequest(BaseModel):
    course_id_or_name: Optional[str] = Field(None, description="课程名称或课程ID")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    week_day: Optional[str] = Field(None, description="上课星期(1-7)")
    class_period: Optional[str] = Field(None, description="上课节次(起止或单节)")

    @model_validator(mode="after")
    def _at_least_one_filter(self):
        cid = (self.course_id_or_name or "").strip()
        tname = (self.teacher_name or "").strip()
        if not cid and not tname:
            raise ValueError("course_id_or_name 与 teacher_name 至少提供一个")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                # 二选一示例：只填课程名/号或只填教师名均可
                "course_id_or_name": "Python",
                "teacher_name": "",
                "week_day": "",
                "class_period": "",
            }
        }


# class CourseScheduleItem(BaseModel):
#     ...（暂不需要）

# class CourseArrangement(BaseModel):
#     ...（暂不需要）


class CourseItem(BaseModel):
    # 必需字段（前端显示用）
    course_id: Optional[str] = Field(None, description="课程编号")
    course_name: Optional[str] = Field(None, description="课程名")
    group_name: Optional[str] = Field(None, description="分组名")
    credits: Optional[int] = Field(None, description="学分")
    teacher_name: Optional[str] = Field(None, description="上课老师")
    time_text: Optional[str] = Field(None, description="上课时间")
    location: Optional[str] = Field(None, description="上课地点")
    campus_name: Optional[str] = Field(None, description="上课校区")
    remain_count: Optional[int] = Field(None, description="剩余量")
    time_conflict: Optional[str] = Field(None, description="时间冲突")
    # 其余字段暂不返回
    # teacher_id: Optional[str] = Field(None, description="教师ID")
    # plan_capacity: Optional[int] = Field(None, description="排课容量")
    # selected_count: Optional[int] = Field(None, description="已选人数")
    # max_capacity: Optional[int] = Field(None, description="最大容量")
    # conflict_text: Optional[str] = Field(None, description="时间冲突文本")
    # remark: Optional[str] = Field(None, description="备注")
    # operation_html: Optional[str] = Field(None, description="操作HTML片段")
    # course_intro: Optional[str] = Field(None, description="课程简介")
    # term_id: Optional[str] = Field(None, description="学期ID")
    # jxb_id: Optional[str] = Field(None, description="教学班ID")
    # jx0504id: Optional[int] = Field(None, description="教学安排ID")
    # teaching_unit_id: Optional[str] = Field(None, description="教学单位ID")
    # schedule_zc_xq_jc: List[CourseScheduleItem] = Field(default_factory=list, description="周-星期-节次列表")
    # arrangements: List[CourseArrangement] = Field(default_factory=list, description="排课安排")


class ModuleResult(BaseModel):
    module: str = Field(
        ..., description="模块标识，如 knjxk/bxqjhxk/xxxk/ggxxkxk/fawxk"
    )
    module_name: str = Field(..., description="模块名称")
    count: int = Field(..., description="该模块返回的课程条目数")
    courses: List[CourseItem] = Field(..., description="解析后的课程数组")


class QueryErrorItem(BaseModel):
    module: str = Field(..., description="发生错误的模块标识")
    status: int = Field(..., description="HTTP状态码或-1")
    message: str = Field(..., description="错误描述")


class PreSelectCourseQueryData(BaseModel):
    jx0502zbid: str = Field(..., description="选课轮次编号")
    jx0502zbmc: str = Field(..., description="选课轮次名称")
    modules: List[ModuleResult] = Field(..., description="各模块的查询结果")
    errors: List[QueryErrorItem] = Field(
        default_factory=list, description="查询过程中产生的错误列表"
    )


class Config:
    json_schema_extra = {
        "example": {
            "jx0502zbid": "XXXXXX",  # 脱敏后的标识符
            "jx0502zbmc": "XXXXXX",  # 脱敏后的名称
            "modules": [
                {
                    "module": "XXXXXX",  # 脱敏后的模块代码
                    "module_name": "本学期计划选课",
                    "count": 2,
                    "courses": [
                        {
                            "course_id": "XXXXXX",  # 脱敏后的课程ID
                            "course_name": "戏剧影视评论",
                            "group_name": "XXXXXX",  # 脱敏后的班级名称
                            "credits": 3,
                            "teacher_name": "XXXXXX",  # 脱敏后的教师姓名
                            "time_text": "1-18周 星期一 5-7节",
                            "location": "XXXXXX",  # 脱敏后的教室位置
                            "campus_name": "XXXXXX",  # 脱敏后的校区名称
                            "remain_count": 13,
                            "time_conflict": "无时间冲突",
                        },
                        {
                            "course_id": "XXXXXX",  # 脱敏后的课程ID
                            "course_name": "美国文学",
                            "group_name": "XXXXXX",  # 脱敏后的班级名称
                            "credits": 2,
                            "teacher_name": "XXXXXX",  # 脱敏后的教师姓名
                            "time_text": "1-18周 星期一 3-4节",
                            "location": "XXXXXX",  # 脱敏后的教室位置
                            "campus_name": "XXXXXX",  # 脱敏后的校区名称
                            "remain_count": 3,
                            "time_conflict": "与'XXXXXX'冲突",  # 脱敏后的冲突信息
                        },
                    ],
                }
            ],
            "errors": [],
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
    description="课程号或名称、教师至少填写一项；可选：上课星期、节次。系统会遍历多个选课模块并返回结果与模块来源。",
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
        # 执行预选课查询
        data_dict = pre_select_course_query(
            session=session,
            course_id_or_name=payload.course_id_or_name,
            teacher_name=payload.teacher_name,
            week_day=payload.week_day,
            class_period=payload.class_period,
        )

        # 获取学生个人信息用于记录查询日志
        try:
            profile_result = ProfileService.get_student_profile(session)
            if profile_result.get("success") and profile_result.get("data"):
                profile = profile_result["data"]

                CourseQueryLogger.log_course_queries(
                    profile=profile,
                    query_results=data_dict,
                )
        except Exception as log_error:
            # 记录日志失败不影响正常的查询结果返回
            logger.warning(f"记录课程查询日志失败: {log_error}")

        return {
            "ok": True,
            "message": "查询成功",
            "data": data_dict,
        }
    except Exception as e:
        raise BaseEducationService.handle_service_error(e, operation_name="预选课查询")
