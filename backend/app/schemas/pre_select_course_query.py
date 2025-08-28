from pydantic import BaseModel
from typing import Optional


class CourseQueryRecord(BaseModel):
    course_id: Optional[str]
    course_name: Optional[str]
    module_name: str
    grade: Optional[str]
    college: Optional[str]
    major: Optional[str]
    semester: Optional[str]
    round_id: Optional[str]
    round_title: Optional[str]


class CourseQueryRecordResponse(BaseModel):
    success: bool
    message: str
