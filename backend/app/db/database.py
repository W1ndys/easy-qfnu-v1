# database.py (最终修正版)

import pickle
import datetime
import requests  # <--- 确保导入了 requests
from sqlalchemy import create_engine, Column, String, BLOB, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ... 数据库设置部分不变 ...
DATABASE_URL = "sqlite:///./sessions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SessionStore(Base):
    __tablename__ = "sessions"
    student_id = Column(String, primary_key=True, index=True)
    session_data = Column(BLOB, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- 关键修改点在这里 ---


def save_session(student_id: str, session_obj: requests.Session):
    """序列化并保存 session 的 cookies 到数据库"""
    db = SessionLocal()
    try:
        # ⚠️ 不再序列化整个 session 对象
        # pickled_session = pickle.dumps(session_obj)
        # ✅ 只序列化 cookiejar，它更稳定、更适合持久化
        pickled_cookies = pickle.dumps(session_obj.cookies)

        db_session = (
            db.query(SessionStore).filter(SessionStore.student_id == student_id).first()
        )

        if db_session:
            print(f"正在更新学号 {student_id} 的 session cookies...")
            db_session.session_data = pickled_cookies
            db_session.created_at = datetime.datetime.now()
        else:
            print(f"正在为学号 {student_id} 创建新的 session cookies 记录...")
            db_session = SessionStore(
                student_id=student_id,
                session_data=pickled_cookies,
                created_at=datetime.datetime.now(),
            )
            db.add(db_session)

        db.commit()
        print("Session cookies 保存成功。")
    finally:
        db.close()


def get_session(student_id: str) -> requests.Session | None:
    """从数据库读取 cookies 并重建一个 session 对象"""
    db = SessionLocal()
    try:
        db_session_record = (
            db.query(SessionStore).filter(SessionStore.student_id == student_id).first()
        )
        if db_session_record:
            print(f"成功从数据库找到学号 {student_id} 的 session cookies。")

            # ✅ 创建一个新的、干净的 Session 对象
            new_session = requests.Session()

            # ⚠️ 将反序列化后的 cookies 加载到新 session 中
            loaded_cookies = pickle.loads(db_session_record.session_data)
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
