# app/db/course_query_database.py

import os
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger

# 课程查询记录数据库配置
COURSE_QUERY_DB_PATH = os.getenv("COURSE_QUERY_DB_PATH", "./data/course_queries.db")
COURSE_QUERY_DB_URL = f"sqlite:///{COURSE_QUERY_DB_PATH}"

# 确保数据目录存在
os.makedirs(os.path.dirname(COURSE_QUERY_DB_PATH), exist_ok=True)

# 创建引擎和会话
course_query_engine = create_engine(
    COURSE_QUERY_DB_URL, connect_args={"check_same_thread": False}
)
CourseQuerySessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=course_query_engine
)
CourseQueryBase = declarative_base()


class CourseQueryRecord(CourseQueryBase):
    """课程查询记录表"""

    __tablename__ = "course_query_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String, nullable=True, comment="课程编号")
    course_name = Column(String, nullable=True, comment="课程名称")
    module_name = Column(String, nullable=False, comment="所属模块")
    grade = Column(String, nullable=True, comment="查询者年级")
    college = Column(String, nullable=True, comment="查询者学院")
    major = Column(String, nullable=True, comment="查询者专业")
    semester = Column(String, nullable=True, comment="选课学期")
    round_id = Column(String, nullable=True, comment="轮次ID")
    round_title = Column(String, nullable=True, comment="轮次标题")

    # 添加复合唯一约束：course_id, grade, college, major, semester, round_id
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "grade",
            "college",
            "major",
            "semester",
            "round_id",
            name="uq_course_query_composite",
        ),
    )


def init_course_query_db():
    """初始化课程查询记录数据库"""
    try:
        CourseQueryBase.metadata.create_all(bind=course_query_engine)
        logger.info("课程查询记录数据库初始化成功")
    except Exception as e:
        logger.error(f"课程查询记录数据库初始化失败: {e}")
        raise


def get_course_query_db():
    """获取数据库会话"""
    db = CourseQuerySessionLocal()
    try:
        yield db
    finally:
        db.close()


class CourseQueryDatabase:
    """课程查询记录数据库操作类"""

    @staticmethod
    def save_query_record(
        course_id: Optional[str],
        course_name: Optional[str],
        module_name: str,
        grade: Optional[str],
        college: Optional[str],
        major: Optional[str],
        semester: Optional[str],
        round_id: Optional[str],
        round_title: Optional[str],
    ) -> bool:
        """
        保存课程查询记录
        如果记录已存在（基于复合唯一约束），则不重复插入

        Returns:
            bool: 保存是否成功（包括已存在的情况）
        """
        db = CourseQuerySessionLocal()
        try:
            # 先检查是否已存在相同的记录
            existing_record = (
                db.query(CourseQueryRecord)
                .filter(
                    CourseQueryRecord.course_id == course_id,
                    CourseQueryRecord.grade == grade,
                    CourseQueryRecord.college == college,
                    CourseQueryRecord.major == major,
                    CourseQueryRecord.semester == semester,
                    CourseQueryRecord.round_id == round_id,
                )
                .first()
            )

            if existing_record:
                logger.debug(
                    f"课程查询记录已存在，跳过插入: {course_name} - {module_name}"
                )
                return True

            # 插入新记录
            record = CourseQueryRecord(
                course_id=course_id,
                course_name=course_name,
                module_name=module_name,
                grade=grade,
                college=college,
                major=major,
                semester=semester,
                round_id=round_id,
                round_title=round_title,
            )

            db.add(record)
            db.commit()
            logger.info(f"课程查询记录保存成功: {course_name} - {module_name}")
            return True

        except Exception as e:
            logger.error(f"保存课程查询记录失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_query_statistics(limit: int = 100) -> list:
        """
        获取查询统计信息

        Args:
            limit: 返回记录数限制

        Returns:
            list: 查询记录列表
        """
        db = CourseQuerySessionLocal()
        try:
            records = (
                db.query(CourseQueryRecord)
                .order_by(CourseQueryRecord.id.desc())
                .limit(limit)
                .all()
            )

            result = []
            for record in records:
                result.append(
                    {
                        "id": record.id,
                        "course_id": record.course_id,
                        "course_name": record.course_name,
                        "module_name": record.module_name,
                        "grade": record.grade,
                        "college": record.college,
                        "major": record.major,
                        "semester": record.semester,
                        "round_id": record.round_id,
                        "round_title": record.round_title,
                    }
                )

            return result

        except Exception as e:
            logger.error(f"获取查询统计失败: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_course_popularity_by_college(college: Optional[str] = None) -> list:
        """
        获取课程热度统计（按学院筛选）

        Args:
            college: 学院名称，为None时统计所有学院

        Returns:
            list: 课程热度统计列表
        """
        db = CourseQuerySessionLocal()
        try:
            query = db.query(
                CourseQueryRecord.course_id,
                CourseQueryRecord.course_name,
                CourseQueryRecord.college.label("query_count"),
            ).filter(CourseQueryRecord.course_id.isnot(None))

            if college:
                query = query.filter(CourseQueryRecord.college == college)

            # 按课程分组统计
            from sqlalchemy import func

            records = (
                query.group_by(
                    CourseQueryRecord.course_id, CourseQueryRecord.course_name
                )
                .order_by(func.count().desc())
                .all()
            )

            result = []
            for record in records:
                result.append(
                    {
                        "course_id": record.course_id,
                        "course_name": record.course_name,
                        "query_count": len(
                            [r for r in records if r.course_id == record.course_id]
                        ),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"获取课程热度统计失败: {e}")
            return []
        finally:
            db.close()
