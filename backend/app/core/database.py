"""
数据库初始化和管理
SQLite数据库配置和模型定义
"""

import sqlite3
import os
from pathlib import Path
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        # 确保数据目录存在
        db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式的行
        return conn

    def execute_script(self, script: str) -> None:
        """执行SQL脚本"""
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """执行查询语句"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新语句，返回影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount


# 全局数据库管理器实例
db_manager = DatabaseManager()


def init_db():
    """初始化数据库表结构"""
    logger.info("正在初始化数据库...")

    # 创建表的SQL脚本
    create_tables_script = """
    -- 用户表：存储openid与student_id的绑定关系
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        openid TEXT UNIQUE NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        contribution_preference BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 会话表：存储学校官网的Session
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        session_data TEXT NOT NULL,  -- 序列化的Session数据
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 历史课程统计表：存储授权的历史平均分数据
    CREATE TABLE IF NOT EXISTS historical_course_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id TEXT NOT NULL,
        course_name TEXT NOT NULL,
        semester TEXT NOT NULL,  -- 学期，如"2023-2024-1"
        average_score REAL NOT NULL,
        sample_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 课程统计表：存储用户匿名贡献的成绩数据
    CREATE TABLE IF NOT EXISTS course_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id TEXT NOT NULL,
        course_name TEXT NOT NULL,
        score REAL NOT NULL,
        class_id TEXT,  -- 班级ID，用于班内排名
        semester TEXT NOT NULL,
        contributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 创建索引提高查询性能
    CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
    CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);
    CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON sessions(student_id);
    CREATE INDEX IF NOT EXISTS idx_historical_course_id ON historical_course_stats(course_id);
    CREATE INDEX IF NOT EXISTS idx_course_stats_course_id ON course_statistics(course_id);
    CREATE INDEX IF NOT EXISTS idx_course_stats_class_id ON course_statistics(class_id);
    """

    try:
        db_manager.execute_script(create_tables_script)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def get_db():
    """获取数据库连接的依赖注入函数"""
    return db_manager
