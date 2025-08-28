# database.py (Docker适配版 + 安全hash改进)

import pickle
import datetime
import requests
import os
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, BLOB, TIMESTAMP, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.hash_utils import hash_student_id
from loguru import logger

# 数据库配置 - 支持Docker环境
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/sessions.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 确保数据目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SessionStore(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id_hash = Column(
        String, unique=True, index=True, nullable=False
    )  # 存储学号hash值
    session_data = Column(BLOB, nullable=True)  # 改为允许NULL
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)


class CoursePlanCache(Base):
    __tablename__ = "course_plan_cache"
    student_id_hash = Column(String, primary_key=True, index=True, nullable=False)
    plan_content = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- 关键修改点在这里 ---


def save_session(student_id: str, session_obj: requests.Session):
    """序列化并保存 session 的 cookies 到数据库（使用学号hash）"""
    db = SessionLocal()
    try:
        # 将明文学号转换为hash值
        student_id_hash = hash_student_id(student_id)
        logger.debug(f"保存session - 原始学号: {student_id}, hash: {student_id_hash}")

        # 只序列化 cookiejar，更稳定、更适合持久化
        pickled_cookies = pickle.dumps(session_obj.cookies)

        db_session = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )

        now = datetime.datetime.now()
        if db_session:
            logger.info(
                f"正在更新session cookies - 学号: {student_id}, hash: {student_id_hash}"
            )
            setattr(db_session, "session_data", pickled_cookies)
            setattr(db_session, "updated_at", now)
        else:
            logger.info(
                f"正在创建新session cookies记录 - 学号: {student_id}, hash: {student_id_hash}"
            )
            db_session = SessionStore(
                student_id_hash=student_id_hash,
                session_data=pickled_cookies,
                created_at=now,
                updated_at=now,
            )
            db.add(db_session)

        db.commit()
        logger.info(f"Session cookies保存成功 - 学号: {student_id}")
    except Exception as e:
        logger.error(f"保存session失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_session(student_id: str) -> Optional[requests.Session]:
    """从数据库读取 cookies 并重建一个 session 对象（使用学号hash）"""
    db = SessionLocal()
    try:
        # 将明文学号转换为hash值进行查询
        student_id_hash = hash_student_id(student_id)
        logger.debug(f"查询session - 原始学号: {student_id}, hash: {student_id_hash}")

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )
        if db_session_record:
            logger.info(
                f"成功找到session cookies - 学号: {student_id}, hash: {student_id_hash}"
            )

            # 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # 取出实际的二进制数据 - 明确类型转换
            session_data_raw = db_session_record.session_data

            # 确保数据是bytes类型且不为None
            if session_data_raw is not None:
                # 兼容 memoryview、bytes 及其他类型
                if isinstance(session_data_raw, memoryview):
                    session_data_bytes: bytes = session_data_raw.tobytes()
                elif isinstance(session_data_raw, bytes):
                    session_data_bytes = session_data_raw
                else:
                    # 类型忽略，因为我们知道这里是数据库返回的bytes数据
                    session_data_bytes = bytes(session_data_raw)  # type: ignore

                # 将反序列化后的 cookies 加载到新 session 中
                loaded_cookies = pickle.loads(session_data_bytes)
                new_session.cookies.update(loaded_cookies)

                logger.info(f"Session对象重建成功 - 学号: {student_id}")
                return new_session
            else:
                logger.warning(f"Session数据为空（可能已被清空）- 学号: {student_id}")
                return None
        else:
            logger.info(
                f"数据库中未找到session - 学号: {student_id}, hash: {student_id_hash}"
            )
            return None
    except Exception as e:
        logger.error(f"获取session失败: {e}")
        return None
    finally:
        db.close()


def get_session_by_hash(student_id_hash: str) -> Optional[requests.Session]:
    """通过学号hash值从数据库读取 cookies 并重建一个 session 对象"""
    db = SessionLocal()
    try:
        logger.debug(f"通过hash查询session - 学号hash: {student_id_hash}")

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )
        if db_session_record:
            logger.info(
                f"成功从数据库找到学号hash {student_id_hash} 的 session cookies。"
            )

            # 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # 取出实际的二进制数据 - 明确类型转换
            session_data_raw = db_session_record.session_data

            # 确保数据是bytes类型且不为None
            if session_data_raw is not None:
                # 兼容 memoryview、bytes 及其他类型
                if isinstance(session_data_raw, memoryview):
                    session_data_bytes: bytes = session_data_raw.tobytes()
                elif isinstance(session_data_raw, bytes):
                    session_data_bytes = session_data_raw
                else:
                    # 类型忽略，因为我们知道这里是数据库返回的bytes数据
                    session_data_bytes = bytes(session_data_raw)  # type: ignore

                # 将反序列化后的 cookies 加载到新 session 中
                loaded_cookies = pickle.loads(session_data_bytes)
                new_session.cookies.update(loaded_cookies)

                logger.info("Session 对象重建成功。")
                return new_session
            else:
                logger.warning("Session数据为空（可能已被清空）")
                return None
        else:
            logger.info(f"数据库中未找到学号hash {student_id_hash} 的 session。")
            return None
    except Exception as e:
        logger.error(f"通过hash获取session失败: {e}")
        return None
    finally:
        db.close()


def delete_session(student_id: str) -> bool:
    """清空指定学号的session数据，保留记录行（使用学号hash）"""
    db = SessionLocal()
    try:
        # 将明文学号转换为hash值
        student_id_hash = hash_student_id(student_id)
        logger.debug(
            f"清空session数据 - 原始学号: {student_id}, hash: {student_id_hash}"
        )

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )

        if db_session_record:
            # 只清空session_data，保留记录行
            setattr(db_session_record, "session_data", None)
            setattr(db_session_record, "updated_at", datetime.datetime.now())
            db.commit()
            logger.info(
                f"成功清空session数据 - 学号: {student_id}, hash: {student_id_hash}"
            )
            return True
        else:
            logger.info(
                f"数据库中未找到要清空的session - 学号: {student_id}, hash: {student_id_hash}"
            )
            return False

    except Exception as e:
        logger.error(f"清空session数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def cleanup_expired_sessions(hours_ago: int = 2) -> int:
    """
    清理指定小时数之前的过期session数据，保留记录行

    Args:
        hours_ago: 清理多少小时前的session，默认2小时

    Returns:
        int: 被清理的session数量
    """
    db = SessionLocal()
    try:
        # 计算截止时间
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
        logger.info(
            f"开始清理 {hours_ago} 小时前的过期session数据，截止时间: {cutoff_time}"
        )

        # 查询并清空过期的session数据
        expired_sessions = (
            db.query(SessionStore).filter(SessionStore.updated_at < cutoff_time).all()
        )

        cleaned_count = 0
        for session in expired_sessions:
            # 只清空session_data，保留记录行
            empty_cookies = pickle.dumps({})  # 序列化空字典
            setattr(session, "session_data", empty_cookies)
            setattr(session, "updated_at", datetime.datetime.now())
            cleaned_count += 1

        db.commit()
        logger.info(f"成功清理 {cleaned_count} 个过期session数据")
        return cleaned_count

    except Exception as e:
        logger.error(f"清理过期session数据失败: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def delete_session_by_hash(student_id_hash: str) -> bool:
    """通过学号hash值清空session数据，保留记录行"""
    db = SessionLocal()
    try:
        logger.debug(f"通过hash清空session数据 - 学号hash: {student_id_hash}")

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )

        if db_session_record:
            # 只清空session_data，保留记录行
            setattr(db_session_record, "session_data", None)
            setattr(db_session_record, "updated_at", datetime.datetime.now())
            db.commit()
            logger.info(f"成功清空学号hash {student_id_hash} 的session数据")
            return True
        else:
            logger.info(f"数据库中未找到学号hash {student_id_hash} 的session")
            return False

    except Exception as e:
        logger.error(f"通过hash清空session数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_course_plan(student_id: str) -> Optional[dict]:
    """获取用户的培养方案缓存"""
    db = SessionLocal()
    try:
        student_id_hash = hash_student_id(student_id)
        cache_item = (
            db.query(CoursePlanCache)
            .filter(CoursePlanCache.student_id_hash == student_id_hash)
            .first()
        )

        if cache_item:
            # 检查缓存是否在30天内
            updated_at_value = cache_item.updated_at
            if isinstance(updated_at_value, datetime.datetime) and (
                datetime.datetime.now() - updated_at_value
            ) < datetime.timedelta(days=30):
                logger.info(f"找到有效的培养方案缓存 - 学号: {student_id}")
                return {
                    "plan_content": cache_item.plan_content,
                    "updated_at": cache_item.updated_at,
                }
        logger.info(f"未找到有效的培养方案缓存 - 学号: {student_id}")
        return None
    except Exception as e:
        logger.error(f"获取培养方案缓存失败: {e}")
        return None
    finally:
        db.close()


def save_course_plan(student_id: str, plan_content: str):
    """保存或更新用户的培养方案缓存"""
    db = SessionLocal()
    try:
        student_id_hash = hash_student_id(student_id)
        now = datetime.datetime.now()

        cache_item = (
            db.query(CoursePlanCache)
            .filter(CoursePlanCache.student_id_hash == student_id_hash)
            .first()
        )

        if cache_item:
            setattr(cache_item, "plan_content", plan_content)
            setattr(cache_item, "updated_at", now)
            logger.info(f"更新培养方案缓存 - 学号: {student_id}")
        else:
            cache_item = CoursePlanCache(
                student_id_hash=student_id_hash,
                plan_content=plan_content,
                updated_at=now,
            )
            db.add(cache_item)
            logger.info(f"新建培养方案缓存 - 学号: {student_id}")

        db.commit()
    except Exception as e:
        logger.error(f"保存培养方案缓存失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def delete_course_plan(student_id: str) -> bool:
    """删除用户的培养方案缓存"""
    db = SessionLocal()
    try:
        student_id_hash = hash_student_id(student_id)
        cache_item = (
            db.query(CoursePlanCache)
            .filter(CoursePlanCache.student_id_hash == student_id_hash)
            .first()
        )

        if cache_item:
            db.delete(cache_item)
            db.commit()
            logger.info(f"删除培养方案缓存 - 学号: {student_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"删除培养方案缓存失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
