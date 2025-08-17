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
from app.services.base_service import BaseService
from app.models.grade import Grade, GradeStats, GradeSummary, SemesterGrades

logger = logging.getLogger(__name__)


class GradeService(BaseService):
    """成绩服务类"""

    def __init__(self, db: DatabaseManager):
        super().__init__(db)

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

            # 构造成绩查询请求数据
            data = {
                "kksj": semester if semester else "",  # 开课学期
                "kcxz": "",  # 课程性质
                "kcmc": "",  # 课程名称
                "xsfs": "all",  # 显示方式
            }

            # 设置请求头
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "max-age=0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://zhjw.qfnu.edu.cn",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
            }

            # 发送POST请求
            response = session.post(
                "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list",
                data=data,
                headers=headers,
                timeout=10,
            )

            # 检查session是否过期
            await self.handle_session_expired(student_id, response.text, response.url)

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

            # 查找成绩表格
            grade_table = soup.find("table", {"id": "dataList"})

            if not grade_table:
                logger.warning("未找到成绩表格")
                return grades

            # 解析表格行，跳过表头
            rows = grade_table.find_all("tr")[1:]  # type: ignore

            for row in rows:
                cells = row.find_all("td")  # type: ignore
                if len(cells) >= 10:  # 确保有足够的列
                    try:
                        # 根据新的表格结构调整索引
                        # 列顺序：序号(0), 开课学期(1), 课程编号(2), 课程名称(3), 分组名(4),
                        #        成绩(5), 成绩标识(6), 学分(7), 总学时(8), 绩点(9), ...

                        # 获取基本信息
                        semester = cells[1].get_text(strip=True)
                        course_id = cells[2].get_text(strip=True)
                        course_name = cells[3].get_text(strip=True)
                        score_text = cells[5].get_text(strip=True)
                        credit_text = cells[7].get_text(strip=True)
                        grade_point_text = cells[9].get_text(strip=True)

                        # 解析成绩
                        score = self._parse_score(score_text)

                        # 解析学分
                        try:
                            credit = float(credit_text) if credit_text else 0.0
                        except (ValueError, TypeError):
                            credit = 0.0

                        # 解析绩点
                        try:
                            grade_point = (
                                float(grade_point_text) if grade_point_text else None
                            )
                        except (ValueError, TypeError):
                            grade_point = self._calculate_grade_point(score)

                        # 获取课程类型（课程性质列）
                        course_type = None
                        if len(cells) >= 15:  # 课程性质在第14列（索引13）
                            course_type = cells[14].get_text(strip=True)

                        grade = Grade(
                            course_id=course_id,
                            course_name=course_name,
                            semester=semester,
                            score=score,
                            credit=credit,
                            grade_point=grade_point,
                            course_type=course_type,
                            teacher=None,  # 这个表格中没有教师信息
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
            "优": 95,
            "良好": 85,
            "良": 85,
            "中等": 75,
            "中": 75,
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
