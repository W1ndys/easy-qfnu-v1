# database.py (Docker适配版 + 安全hash改进)

import pickle
import datetime
import requests
import os
from typing import Optional, Union
from sqlalchemy import create_engine, Column, String, Integer, BLOB, TIMESTAMP
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
    session_data = Column(BLOB, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- 关键修改点在这里 ---


def save_session(student_id: str, session_obj: requests.Session):
    """序列化并保存 session 的 cookies 到数据库（使用学号hash）"""
    db = SessionLocal()
    try:
        # 将明文学号转换为hash值
        student_id_hash = hash_student_id(student_id)
        logger.debug(f"保存session - 学号hash: {student_id_hash[:8]}****")

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
                f"正在更新学号hash {student_id_hash[:8]}**** 的 session cookies..."
            )
            setattr(db_session, "session_data", pickled_cookies)
            setattr(db_session, "updated_at", now)
        else:
            logger.info(
                f"正在为学号hash {student_id_hash[:8]}**** 创建新的 session cookies 记录..."
            )
            db_session = SessionStore(
                student_id_hash=student_id_hash,
                session_data=pickled_cookies,
                created_at=now,
                updated_at=now,
            )
            db.add(db_session)

        db.commit()
        logger.info("Session cookies 保存成功。")
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
        logger.debug(f"查询session - 学号hash: {student_id_hash[:8]}****")

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )
        if db_session_record:
            logger.info(
                f"成功从数据库找到学号hash {student_id_hash[:8]}**** 的 session cookies。"
            )

            # 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # 取出实际的二进制数据 - 明确类型转换
            session_data_raw = db_session_record.session_data

            # 确保数据是bytes类型
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
                logger.warning("Session数据为空")
                return None
        else:
            logger.info(
                f"数据库中未找到学号hash {student_id_hash[:8]}**** 的 session。"
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
        logger.debug(f"通过hash查询session - 学号hash: {student_id_hash[:8]}****")

        db_session_record = (
            db.query(SessionStore)
            .filter(SessionStore.student_id_hash == student_id_hash)
            .first()
        )
        if db_session_record:
            logger.info(
                f"成功从数据库找到学号hash {student_id_hash[:8]}**** 的 session cookies。"
            )

            # 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # 取出实际的二进制数据 - 明确类型转换
            session_data_raw = db_session_record.session_data

            # 确保数据是bytes类型
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
                logger.warning("Session数据为空")
                return None
        else:
            logger.info(
                f"数据库中未找到学号hash {student_id_hash[:8]}**** 的 session。"
            )
            return None
    except Exception as e:
        logger.error(f"通过hash获取session失败: {e}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
