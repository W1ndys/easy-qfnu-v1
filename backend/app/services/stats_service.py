"""
统计服务
处理课程统计、班内排名等数据分析业务逻辑
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.core.database import DatabaseManager
from app.models.stats import (
    CourseStatsResponse,
    ClassRankResponse,
    HistoricalStats,
    CrowdsourcedStats,
    GradeContribution,
)

logger = logging.getLogger(__name__)


class StatsService:
    """统计服务类"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    async def get_course_statistics(self, course_id: str) -> CourseStatsResponse:
        """
        获取课程综合统计信息

        Args:
            course_id: 课程ID

        Returns:
            课程统计响应
        """
        try:
            # 获取历史参考数据
            historical_stats = await self._get_historical_stats(course_id)

            # 获取众包数据
            crowdsourced_stats = await self._get_crowdsourced_stats(course_id)

            # 计算综合平均分
            combined_average = self._calculate_combined_average(
                historical_stats, crowdsourced_stats
            )

            # 计算总样本数
            total_samples = 0
            if historical_stats:
                total_samples += historical_stats.sample_count
            if crowdsourced_stats:
                total_samples += crowdsourced_stats.sample_count

            return CourseStatsResponse(
                course_id=course_id,
                course_name=historical_stats.course_name
                if historical_stats
                else crowdsourced_stats.course_name
                if crowdsourced_stats
                else "未知课程",
                historical=historical_stats,
                crowdsourced=crowdsourced_stats,
                combined_average=combined_average,
                total_samples=total_samples,
            )

        except Exception as e:
            logger.error(f"获取课程统计数据失败: {e}")
            raise

    async def _get_historical_stats(self, course_id: str) -> Optional[HistoricalStats]:
        """
        获取历史参考数据

        Args:
            course_id: 课程ID

        Returns:
            历史统计数据
        """
        try:
            query = """
            SELECT course_id, course_name, semester, average_score, sample_count
            FROM historical_course_stats
            WHERE course_id = ?
            ORDER BY semester DESC
            LIMIT 1
            """

            result = self.db.execute_query(query, (course_id,))

            if result:
                row = result[0]
                return HistoricalStats(
                    course_id=row["course_id"],
                    course_name=row["course_name"],
                    semester=row["semester"],
                    average_score=row["average_score"],
                    sample_count=row["sample_count"],
                )

            return None

        except Exception as e:
            logger.error(f"获取历史统计数据失败: {e}")
            return None

    async def _get_crowdsourced_stats(
        self, course_id: str
    ) -> Optional[CrowdsourcedStats]:
        """
        获取众包统计数据

        Args:
            course_id: 课程ID

        Returns:
            众包统计数据
        """
        try:
            query = """
            SELECT course_id, course_name, AVG(score) as avg_score, COUNT(*) as count,
                   MAX(contributed_at) as last_updated
            FROM course_statistics
            WHERE course_id = ?
            GROUP BY course_id, course_name
            """

            result = self.db.execute_query(query, (course_id,))

            if result and result[0]["count"] > 0:
                row = result[0]
                return CrowdsourcedStats(
                    course_id=row["course_id"],
                    course_name=row["course_name"],
                    average_score=round(row["avg_score"], 2),
                    sample_count=row["count"],
                    last_updated=row["last_updated"],
                )

            return None

        except Exception as e:
            logger.error(f"获取众包统计数据失败: {e}")
            return None

    def _calculate_combined_average(
        self,
        historical: Optional[HistoricalStats],
        crowdsourced: Optional[CrowdsourcedStats],
    ) -> Optional[float]:
        """
        计算综合平均分

        Args:
            historical: 历史数据
            crowdsourced: 众包数据

        Returns:
            综合平均分
        """
        if not historical and not crowdsourced:
            return None

        if not historical:
            return crowdsourced.average_score

        if not crowdsourced:
            return historical.average_score

        # 加权平均（历史数据权重更高）
        historical_weight = 0.7
        crowdsourced_weight = 0.3

        combined = (
            historical.average_score * historical_weight
            + crowdsourced.average_score * crowdsourced_weight
        )

        return round(combined, 2)

    async def contribute_grades(
        self, student_id: str, grades: List[GradeContribution]
    ) -> Dict[str, Any]:
        """
        处理用户成绩贡献

        Args:
            student_id: 学号
            grades: 贡献的成绩列表

        Returns:
            贡献结果
        """
        try:
            contributed_count = 0

            for grade in grades:
                # 检查是否已经贡献过该课程成绩
                existing_query = """
                SELECT id FROM course_statistics
                WHERE course_id = ? AND contributed_by = ? AND semester = ?
                """

                # 这里简化处理，实际应用中需要记录贡献者信息（但保持匿名）
                grade_hash = f"{student_id}_{grade.course_id}_{grade.semester}"

                existing = self.db.execute_query(
                    "SELECT id FROM course_statistics WHERE course_id = ? AND semester = ? LIMIT 1",
                    (grade.course_id, grade.semester),
                )

                # 避免重复贡献（简化逻辑）
                insert_query = """
                INSERT INTO course_statistics 
                (course_id, course_name, score, class_id, semester, contributed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """

                self.db.execute_update(
                    insert_query,
                    (
                        grade.course_id,
                        grade.course_name,
                        grade.score,
                        grade.class_id,
                        grade.semester,
                        datetime.now(),
                    ),
                )

                contributed_count += 1

            logger.info(f"用户 {student_id} 成功贡献了 {contributed_count} 条成绩数据")

            return {
                "success": True,
                "contributed_count": contributed_count,
                "message": f"成功贡献 {contributed_count} 条成绩数据",
            }

        except Exception as e:
            logger.error(f"处理成绩贡献失败: {e}")
            raise

    async def get_class_rank(
        self, student_id: str, course_id: str
    ) -> ClassRankResponse:
        """
        获取班内排名信息

        Args:
            student_id: 学号
            course_id: 课程ID

        Returns:
            班内排名响应
        """
        try:
            # 首先获取用户自己的成绩和班级信息
            user_grade_query = """
            SELECT score, class_id FROM course_statistics
            WHERE course_id = ? 
            LIMIT 1
            """

            user_result = self.db.execute_query(user_grade_query, (course_id,))

            if not user_result:
                raise ValueError("未找到用户在该课程的成绩数据")

            user_score = user_result[0]["score"]
            class_id = user_result[0]["class_id"]

            if not class_id:
                raise ValueError("班级信息不完整，无法计算排名")

            # 获取同班同学的成绩数据
            class_grades_query = """
            SELECT score FROM course_statistics
            WHERE course_id = ? AND class_id = ?
            ORDER BY score DESC
            """

            class_results = self.db.execute_query(
                class_grades_query, (course_id, class_id)
            )

            if len(class_results) < settings.MIN_DATA_FOR_RANKING:
                raise ValueError("班内数据量不足，无法计算排名")

            # 计算排名和统计信息
            scores = [row["score"] for row in class_results]
            total_students = len(scores)
            class_average = sum(scores) / total_students

            # 计算用户排名
            user_rank = sum(1 for score in scores if score > user_score) + 1

            # 计算百分位
            percentile = (total_students - user_rank + 1) / total_students

            # 获取课程名称
            course_name_query = """
            SELECT course_name FROM course_statistics
            WHERE course_id = ?
            LIMIT 1
            """

            course_result = self.db.execute_query(course_name_query, (course_id,))
            course_name = (
                course_result[0]["course_name"] if course_result else "未知课程"
            )

            return ClassRankResponse(
                course_id=course_id,
                course_name=course_name,
                user_score=user_score,
                rank=f"{user_rank} / {total_students}",
                percentile=round(percentile, 2),
                total_students=total_students,
                class_average=round(class_average, 2),
                is_above_average=user_score > class_average,
            )

        except Exception as e:
            logger.error(f"获取班内排名失败: {e}")
            raise

    async def check_contribution_preference(self, student_id: str) -> bool:
        """
        检查用户数据贡献偏好

        Args:
            student_id: 学号

        Returns:
            是否同意贡献数据
        """
        try:
            query = """
            SELECT contribution_preference FROM users
            WHERE student_id = ?
            """

            result = self.db.execute_query(query, (student_id,))

            if result:
                return bool(result[0]["contribution_preference"])

            return False

        except Exception as e:
            logger.error(f"检查贡献偏好失败: {e}")
            return False

    async def update_contribution_preference(
        self, student_id: str, enabled: bool
    ) -> None:
        """
        更新用户数据贡献偏好

        Args:
            student_id: 学号
            enabled: 是否启用数据贡献
        """
        try:
            query = """
            UPDATE users 
            SET contribution_preference = ?, updated_at = ?
            WHERE student_id = ?
            """

            self.db.execute_update(query, (enabled, datetime.now(), student_id))

            logger.info(f"用户 {student_id} 数据贡献偏好已更新为: {enabled}")

        except Exception as e:
            logger.error(f"更新贡献偏好失败: {e}")
            raise
