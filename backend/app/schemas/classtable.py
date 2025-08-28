# app/schemas/classtable.py
from pydantic import BaseModel, Field
from typing import List, Optional


class CourseInfo(BaseModel):
    """单个课程信息模型"""

    course_name: str = Field(..., description="课程名称")
    course_credits: str = Field(..., description="课程学分")
    course_property: str = Field(..., description="课程属性")
    class_time: str = Field(..., description="上课时间")
    classroom: str = Field(..., description="上课地点")
    class_name: str = Field(..., description="课堂名称")
    day_of_week: int = Field(..., description="星期几(1-7)")
    period: str = Field(..., description="节次信息")


class DayCourses(BaseModel):
    """某一天的课程信息"""

    date: str = Field(..., description="日期(YYYY-MM-DD)")
    day_of_week: int = Field(..., description="星期几(1-7)")
    courses: List[CourseInfo] = Field(default=[], description="当天的课程列表")


class WeekCourses(BaseModel):
    """一周的课程信息"""

    week_number: int = Field(..., description="第几周")
    start_date: str = Field(..., description="本周开始日期(YYYY-MM-DD)")
    end_date: str = Field(..., description="本周结束日期(YYYY-MM-DD)")
    days: List[DayCourses] = Field(default=[], description="一周七天的课程")


class DayClassTableResponse(BaseModel):
    """单日课程表查询响应模型"""

    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[DayCourses] = Field(None, description="单日课程数据")


class WeekClassTableResponse(BaseModel):
    """周课程表查询响应模型"""

    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[WeekCourses] = Field(None, description="周课程数据")
