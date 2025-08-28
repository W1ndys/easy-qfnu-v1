# app/services/course_query_logger.py

from typing import Optional, Dict, Any, List
from loguru import logger
import re
from app.db.course_query_database import CourseQueryDatabase
from app.schemas.profile import StudentProfile


class CourseQueryLogger:
    """课程查询记录服务类"""

    @staticmethod
    def extract_grade_from_student_id(student_id: str) -> Optional[str]:
        """
        从学号中提取年级信息

        Args:
            student_id: 学生编号

        Returns:
            str: 年级，如"2021级"，提取失败返回None
        """
        try:
            # 假设学号格式为：20210101001 (前4位为入学年份)
            # 或者其他格式，需要根据实际学号格式调整
            if len(student_id) >= 4:
                year_match = re.match(r"^(\d{4})", student_id)
                if year_match:
                    year = year_match.group(1)
                    return year
            return None
        except Exception as e:
            logger.warning(f"提取年级信息失败: {e}")
            return None

    @staticmethod
    def log_course_queries(
        profile: StudentProfile,
        query_results: Dict[str, Any],
    ) -> None:
        """
        记录课程查询日志

        Args:
            profile: 学生个人信息
            query_results: 查询结果数据
        """
        try:
            # 提取基础信息
            grade = CourseQueryLogger.extract_grade_from_student_id(profile.student_id)
            round_id = query_results.get("select_course_round_id")
            round_title = query_results.get("select_course_round_name")
            semester = getattr(query_results, "semester", None)  # 如果有学期信息

            # 如果年级与选课轮次不匹配，并且不是补选或退选，则跳过记录
            if (
                grade
                and round_title
                and f"{grade}级" not in round_title
                and "补选" not in round_title
                and "退选" not in round_title
            ):
                logger.warning(
                    f"年级{grade}与选课轮次{round_title}不匹配，且不是补选或退选，跳过记录"
                )
                return

            # 遍历每个模块的查询结果
            modules = query_results.get("modules", [])

            for module in modules:
                module_name = module.get("module_name", "")
                courses = module.get("courses", [])

                # 如果该模块有课程结果，记录每门课程
                for course in courses:
                    CourseQueryDatabase.save_query_record(
                        course_id=course.get("course_id"),
                        course_name=course.get("course_name"),
                        module_name=module_name,
                        grade=grade,
                        college=profile.college,
                        major=profile.major,
                        semester=semester,
                        round_id=round_id,
                        round_title=round_title,
                    )

            logger.info(
                f"课程查询记录完成 - 学生: {profile.student_name}, 模块数: {len(modules)}"
            )

        except Exception as e:
            logger.error(f"记录课程查询日志失败: {e}")

    @staticmethod
    def get_query_statistics(limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取查询统计信息

        Args:
            limit: 返回记录数限制

        Returns:
            List[Dict]: 查询记录列表
        """
        return CourseQueryDatabase.get_query_statistics(limit)
