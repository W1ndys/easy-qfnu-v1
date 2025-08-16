"""
成绩服务
处理成绩查询和统计相关的业务逻辑
"""

import requests
import logging
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re

from app.core.config import settings
from app.core.security import SessionExpiredError
from app.core.database import DatabaseManager
from app.services.auth_service import AuthService
from app.models.grade import Grade, GradeStats, GradeSummary, SemesterGrades

logger = logging.getLogger(__name__)


class GradeService:
    """成绩服务类"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.auth_service = AuthService(db)

    async def get_student_grades(
        self, student_id: str, semester: Optional[str] = None
    ) -> List[Grade]:
        """
        获取学生成绩信息

        Args:
            student_id: 学号
            semester: 可选的学期参数

        Returns:
            成绩列表
        """
        try:
            # 获取用户的Session
            session_data = await self.auth_service.get_session(student_id)
            if not session_data:
                raise SessionExpiredError("Session不存在或已过期")

            # 创建请求会话
            session = requests.Session()
            session.cookies.update(session_data.get("cookies", {}))

            # 构造成绩查询请求
            params = {}
            if semester:
                params["xnxq01id"] = semester

            # 发送成绩查询请求
            response = session.get(settings.QFNU_GRADE_URL, params=params, timeout=10)

            # 检查是否需要重新登录
            if "login" in response.url.lower():
                await self.auth_service.clear_session(student_id)
                raise SessionExpiredError("Session已过期")

            # 解析成绩数据
            grades = self._parse_grades_html(response.text)

            logger.info(f"成功获取学号 {student_id} 的 {len(grades)} 门课程成绩")
            return grades

        except requests.RequestException as e:
            logger.error(f"获取成绩请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取成绩过程发生错误: {e}")
            raise

    def _parse_grades_html(self, html_content: str) -> List[Grade]:
        """
        解析成绩页面HTML，提取成绩数据

        Args:
            html_content: 成绩页面HTML内容

        Returns:
            解析出的成绩列表
        """
        grades = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 查找成绩表格（根据实际页面结构调整）
            grade_table = soup.find("table", {"id": "dataList"}) or soup.find(
                "table", class_="displayTag"
            )

            if not grade_table:
                logger.warning("未找到成绩表格")
                return grades

            # 解析表格行
            rows = grade_table.find_all("tr")[1:]  # 跳过表头

            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 6:  # 确保有足够的列
                    try:
                        # 根据实际表格结构调整索引
                        grade = Grade(
                            course_id=cells[1].get_text(strip=True),
                            course_name=cells[2].get_text(strip=True),
                            semester=cells[0].get_text(strip=True),
                            score=self._parse_score(cells[4].get_text(strip=True)),
                            credit=float(cells[3].get_text(strip=True) or 0),
                            grade_point=self._calculate_grade_point(
                                self._parse_score(cells[4].get_text(strip=True))
                            ),
                            course_type=(
                                cells[5].get_text(strip=True)
                                if len(cells) > 5
                                else None
                            ),
                            teacher=(
                                cells[6].get_text(strip=True)
                                if len(cells) > 6
                                else None
                            ),
                        )
                        grades.append(grade)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"解析成绩行时出错: {e}")
                        continue

        except Exception as e:
            logger.error(f"解析成绩HTML时出错: {e}")

        return grades

    def _parse_score(self, score_text: str) -> float:
        """
        解析成绩文本，处理各种格式的成绩

        Args:
            score_text: 成绩文本

        Returns:
            数值化的成绩
        """
        score_text = score_text.strip()

        # 处理等级制成绩
        grade_mapping = {
            "优秀": 95,
            "良好": 85,
            "中等": 75,
            "及格": 65,
            "不及格": 50,
            "通过": 80,
            "未通过": 50,
        }

        if score_text in grade_mapping:
            return grade_mapping[score_text]

        # 提取数字成绩
        number_match = re.search(r"(\d+(?:\.\d+)?)", score_text)
        if number_match:
            return float(number_match.group(1))

        # 默认返回0
        return 0.0

    def _calculate_grade_point(self, score: float) -> float:
        """
        根据成绩计算绩点

        Args:
            score: 成绩

        Returns:
            绩点
        """
        if score >= 95:
            return 4.0
        elif score >= 90:
            return 3.7
        elif score >= 85:
            return 3.3
        elif score >= 80:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 70:
            return 2.3
        elif score >= 65:
            return 2.0
        elif score >= 60:
            return 1.0
        else:
            return 0.0

    async def calculate_grade_stats(self, grades: List[Grade]) -> GradeStats:
        """
        计算成绩统计信息

        Args:
            grades: 成绩列表

        Returns:
            统计信息
        """
        if not grades:
            return GradeStats(
                total_courses=0,
                total_credits=0.0,
                gpa=0.0,
                weighted_average=0.0,
                failed_courses=0,
                excellent_courses=0,
            )

        total_courses = len(grades)
        total_credits = sum(grade.credit for grade in grades)
        failed_courses = sum(1 for grade in grades if grade.score < 60)
        excellent_courses = sum(1 for grade in grades if grade.score >= 90)

        # 计算GPA（学分加权）
        total_grade_points = sum(
            grade.credit * (grade.grade_point or 0) for grade in grades
        )
        gpa = total_grade_points / total_credits if total_credits > 0 else 0.0

        # 计算加权平均分
        total_weighted_score = sum(grade.credit * grade.score for grade in grades)
        weighted_average = (
            total_weighted_score / total_credits if total_credits > 0 else 0.0
        )

        return GradeStats(
            total_courses=total_courses,
            total_credits=total_credits,
            gpa=round(gpa, 2),
            weighted_average=round(weighted_average, 2),
            failed_courses=failed_courses,
            excellent_courses=excellent_courses,
        )

    async def calculate_summary_stats(self, grades: List[Grade]) -> GradeSummary:
        """
        计算成绩摘要统计

        Args:
            grades: 成绩列表

        Returns:
            摘要统计信息
        """
        # 按学期分组
        semester_groups = {}
        for grade in grades:
            if grade.semester not in semester_groups:
                semester_groups[grade.semester] = []
            semester_groups[grade.semester].append(grade)

        # 计算每学期统计
        semester_stats = []
        for semester, semester_grades in semester_groups.items():
            semester_total_credits = sum(grade.credit for grade in semester_grades)
            semester_gpa_points = sum(
                grade.credit * (grade.grade_point or 0) for grade in semester_grades
            )
            semester_weighted_score = sum(
                grade.credit * grade.score for grade in semester_grades
            )

            semester_gpa = (
                semester_gpa_points / semester_total_credits
                if semester_total_credits > 0
                else 0.0
            )
            semester_average = (
                semester_weighted_score / semester_total_credits
                if semester_total_credits > 0
                else 0.0
            )

            semester_stats.append(
                SemesterGrades(
                    semester=semester,
                    grades=semester_grades,
                    semester_gpa=round(semester_gpa, 2),
                    semester_average=round(semester_average, 2),
                    semester_credits=semester_total_credits,
                )
            )

        # 排序学期
        semester_stats.sort(key=lambda x: x.semester)

        # 计算总体统计
        overall_stats = await self.calculate_grade_stats(grades)

        return GradeSummary(overall_stats=overall_stats, semester_stats=semester_stats)
