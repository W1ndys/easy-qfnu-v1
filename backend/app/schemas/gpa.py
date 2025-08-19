# app/schemas/gpa.py
from pydantic import BaseModel
from typing import List, Optional


class GPACalculateRequest(BaseModel):
    exclude_indices: List[int] = []  # 要排除的课程序号列表
    remove_retakes: bool = False  # 是否去除重修补考，取最高绩点
