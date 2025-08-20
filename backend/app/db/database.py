# database.py (Docker适配版)

import pickle
import datetime
import requests
import os
from sqlalchemy import create_engine, Column, String, Integer, BLOB, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base

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
    student_id = Column(String, unique=True, index=True, nullable=False)
    session_data = Column(BLOB, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- 关键修改点在这里 ---


def save_session(student_id: str, session_obj: requests.Session):
    """序列化并保存 session 的 cookies 到数据库"""
    db = SessionLocal()
    try:
        # 只序列化 cookiejar，更稳定、更适合持久化
        pickled_cookies = pickle.dumps(session_obj.cookies)

        db_session = (
            db.query(SessionStore).filter(SessionStore.student_id == student_id).first()
        )

        now = datetime.datetime.now()
        if db_session:
            print(f"正在更新学号 {student_id} 的 session cookies...")
            setattr(db_session, "session_data", pickled_cookies)
            setattr(db_session, "updated_at", now)
        else:
            print(f"正在为学号 {student_id} 创建新的 session cookies 记录...")
            db_session = SessionStore(
                student_id=student_id,
                session_data=pickled_cookies,
                created_at=now,
                updated_at=now,
            )
            db.add(db_session)

        db.commit()
        print("Session cookies 保存成功。")
    finally:
        db.close()


def get_session(student_id: str):
    """从数据库读取 cookies 并重建一个 session 对象"""
    db = SessionLocal()
    try:
        db_session_record = (
            db.query(SessionStore).filter(SessionStore.student_id == student_id).first()
        )
        if db_session_record:
            print(f"成功从数据库找到学号 {student_id} 的 session cookies。")

            # 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # 取出实际的二进制数据
            session_data_bytes = db_session_record.session_data
            # 兼容 memoryview、bytes 及其他类型
            if isinstance(session_data_bytes, memoryview):
                session_data_bytes = session_data_bytes.tobytes()
            elif not isinstance(session_data_bytes, bytes):
                session_data_bytes = bytes(session_data_bytes)

            # 将反序列化后的 cookies 加载到新 session 中
            loaded_cookies = pickle.loads(session_data_bytes)
            new_session.cookies.update(loaded_cookies)

            print("Session 对象重建成功。")
            return new_session
        else:
            print(f"数据库中未找到学号 {student_id} 的 session。")
            return None
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
