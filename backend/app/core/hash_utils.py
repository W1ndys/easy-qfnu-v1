# app/core/hash_utils.py

import hashlib
import os
from loguru import logger

# 从环境变量读取盐值，如果没有则使用默认值（生产环境中应该设置环境变量）
HASH_SALT = os.getenv("STUDENT_ID_SALT", "STUDENT_ID_SALT")


def hash_student_id(student_id: str) -> str:
    """
    对学号进行安全哈希处理

    Args:
        student_id: 明文学号

    Returns:
        str: 学号的SHA256哈希值
    """
    if not student_id or not isinstance(student_id, str):
        raise ValueError("学号不能为空且必须是字符串")

    # 使用学号 + 盐值进行SHA256哈希
    combined = f"{student_id}{HASH_SALT}"
    hash_value = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    logger.debug(f"学号哈希处理完成: {student_id} -> {hash_value}")
    return hash_value


def verify_student_id(student_id: str, hash_value: str) -> bool:
    """
    验证学号与哈希值是否匹配

    Args:
        student_id: 明文学号
        hash_value: 已存储的哈希值

    Returns:
        bool: 是否匹配
    """
    if not student_id or not hash_value:
        return False

    try:
        calculated_hash = hash_student_id(student_id)
        is_match = calculated_hash == hash_value

        if is_match:
            logger.debug(f"学号验证成功: {student_id}")
        else:
            logger.warning(f"学号验证失败: {student_id}")

        return is_match
    except Exception as e:
        logger.error(f"学号验证过程中发生错误: {e}")
        return False


def get_student_id_for_display(hash_value: str) -> str:
    """
    返回用于显示的脱敏学号标识符
    （由于是单向哈希，无法反推明文，这里返回哈希值的前8位作为标识）

    Args:
        hash_value: 学号哈希值

    Returns:
        str: 用于显示的标识符
    """
    if not hash_value:
        return "未知用户"

    return f"用户_{hash_value[:8]}"
