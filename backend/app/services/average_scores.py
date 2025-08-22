# app/services/average_scores_service.py
from typing import Optional, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger


Base = declarative_base()


class AverageScore(Base):
    """平均分数据模型"""

    __tablename__ = "average_scores"

    id = Column(Integer, primary_key=True)
    semester = Column(String, nullable=False)
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    teacher = Column(String, nullable=False)
    average_score = Column(Float, nullable=False)
    student_count = Column(Integer, nullable=False)
    update_time = Column(String)


class AverageScoresService:
    """平均分查询服务类"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def _get_db_engine(self):
        """获取数据库引擎"""
        if self.engine is None:
            logger.debug("开始获取数据库引擎...")

            # 使用 Path 对象进行路径操作，确保跨平台兼容性
            current_dir = Path(__file__).resolve().parent.parent.parent
            db_path = current_dir / "data" / "average_scores.db"

            logger.debug(f"数据库路径: {db_path}")

            if not db_path.exists():
                logger.error(f"数据库文件不存在: {db_path}")
                raise FileNotFoundError(f"数据库文件不存在: {db_path}")

            # 使用 as_posix() 确保路径格式正确
            self.engine = create_engine(f"sqlite:///{db_path.as_posix()}")
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.debug("数据库引擎创建成功")

        return self.engine

    def _get_db_session(self) -> Session:
        """获取数据库会话"""
        logger.debug("开始获取数据库会话...")
        try:
            self._get_db_engine()
            session = self.SessionLocal()
            logger.debug("数据库会话创建成功")
            return session
        except Exception as e:
            logger.error(f"创建数据库会话失败: {e}")
            raise

    def query_average_scores(
        self, course_identifier: str, teacher: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询平均分数据

        Args:
            course_identifier: 课程名称或课程代码
            teacher: 教师姓名（可选）

        Returns:
            dict: 结构化的平均分数据

        Raises:
            Exception: 查询失败时抛出异常
        """
        logger.info(
            f"开始查询平均分数据，课程标识: {course_identifier}, 教师: {teacher or '全部'}"
        )

        session = None
        try:
            session = self._get_db_session()
            logger.debug("数据库会话获取成功，开始构建查询...")

            # 构建基础查询
            query = session.query(AverageScore)

            # 构建课程查询条件（课程名称或课程代码）
            course_conditions = AverageScore.course_name.like(
                f"%{course_identifier}%"
            ) | AverageScore.course_code.like(f"%{course_identifier}%")

            # 应用课程查询条件
            query = query.filter(course_conditions)
            logger.debug(f"应用课程查询条件: {course_identifier}")

            # 如果指定了教师，添加教师查询条件
            if teacher and teacher.strip():
                teacher_condition = AverageScore.teacher.like(f"%{teacher.strip()}%")
                query = query.filter(teacher_condition)
                logger.debug(f"应用教师查询条件: {teacher.strip()}")

            # 使用text()函数进行智能排序，让最新的学期越靠前
            # 学期格式：年份-年份-数字，如"2023-2024-1"
            logger.debug("应用智能排序规则...")
            query = query.order_by(
                AverageScore.teacher,
                text("CAST(SUBSTR(semester, 1, 4) AS INTEGER) DESC"),  # 第一个年份降序
                text("CAST(SUBSTR(semester, 6, 4) AS INTEGER) DESC"),  # 第二个年份降序
                text("CAST(SUBSTR(semester, 11) AS INTEGER) DESC"),  # 学期数字降序
            )

            logger.debug("执行数据库查询...")
            results = query.all()
            logger.info(f"查询完成，返回 {len(results)} 条记录")

            if not results:
                # 提供更详细的错误信息
                if teacher and teacher.strip():
                    error_msg = f"未找到课程名称或代码包含'{course_identifier}'且教师姓名包含'{teacher.strip()}'的数据"
                else:
                    error_msg = f"未找到课程名称或代码包含'{course_identifier}'的数据"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            # 构建层级结构：课程->老师->学期->基准人数和平均分
            logger.debug("开始构建数据结构...")
            structured_data = {}

            for record in results:
                course_name = record.course_name
                teacher_name = record.teacher
                semester = record.semester

                # 初始化课程层级
                if course_name not in structured_data:
                    structured_data[course_name] = {}

                # 初始化老师层级
                if teacher_name not in structured_data[course_name]:
                    structured_data[course_name][teacher_name] = {}

                # 添加学期数据
                structured_data[course_name][teacher_name][semester] = {
                    "average_score": record.average_score,
                    "student_count": record.student_count,
                    "update_time": record.update_time,
                }

            logger.info(f"数据结构构建完成，包含 {len(structured_data)} 个课程")
            return structured_data

        except Exception as e:
            logger.error(f"数据库查询过程中发生错误: {e}")
            raise
        finally:
            if session:
                session.close()
                logger.debug("数据库会话已关闭")


# 创建全局服务实例
average_scores_service = AverageScoresService()
