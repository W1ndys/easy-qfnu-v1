import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

Base = declarative_base()


class Question(Base):
    """题库数据模型"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    question = Column(Text, nullable=False)
    optionA = Column(Text, nullable=True)
    optionB = Column(Text, nullable=True)
    optionC = Column(Text, nullable=True)
    optionD = Column(Text, nullable=True)
    optionAnswer = Column(String, nullable=True)


class QuestionSearchService:
    """题库搜索服务类"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def _get_db_engine(self):
        """获取数据库引擎"""
        if self.engine is None:
            logger.debug("开始获取题库数据库引擎...")

            # 获取数据库路径：API文件的上上上层的data目录
            current_dir = Path(__file__).resolve().parent.parent.parent
            db_path = current_dir / "data" / "freshman_questions.db"

            logger.debug(f"题库数据库路径: {db_path}")

            if not db_path.exists():
                logger.error(f"题库数据库文件不存在: {db_path}")
                raise FileNotFoundError(f"题库数据库文件不存在: {db_path}")

            self.engine = create_engine(f"sqlite:///{db_path.as_posix()}")
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.debug("题库数据库引擎创建成功")

        return self.engine

    def _get_db_session(self) -> Session:
        """获取数据库会话"""
        logger.debug("开始获取题库数据库会话...")
        try:
            self._get_db_engine()
            session = self.SessionLocal()
            logger.debug("题库数据库会话创建成功")
            return session
        except Exception as e:
            logger.error(f"创建题库数据库会话失败: {e}")
            raise

    @staticmethod
    def normalize_text(text: str) -> str:
        """文本标准化处理"""
        if text is None:
            return ""
        text = unicodedata.normalize("NFKC", str(text)).strip().lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff\s]", "", text)
        return text

    @staticmethod
    def char_set(text: str) -> set:
        """获取字符集合"""
        return set(ch for ch in text if ch.strip())

    @staticmethod
    def similarity(a: str, b: str) -> float:
        """计算两个文本的相似度"""
        if not a or not b:
            return 0.0
        a_norm = QuestionSearchService.normalize_text(a)
        b_norm = QuestionSearchService.normalize_text(b)
        if not a_norm or not b_norm:
            return 0.0

        ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
        set_a, set_b = QuestionSearchService.char_set(
            a_norm
        ), QuestionSearchService.char_set(b_norm)
        jacc = (len(set_a & set_b) / len(set_a | set_b)) if (set_a | set_b) else 0.0

        contain_bonus = 0.0
        if a_norm in b_norm or b_norm in a_norm:
            contain_bonus = 0.15

        score = 0.7 * ratio + 0.3 * jacc + contain_bonus
        return min(score, 1.0)

    @staticmethod
    def extract_answer_struct(question_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取答案结构"""
        letter = (question_data.get("optionAnswer") or "").strip()
        text = question_data.get(f"option{letter}") if letter else None
        return {"letter": letter or None, "text": text}

    def search_questions(
        self, query: str, topk: int = 3, threshold: float = 0.55
    ) -> List[Dict[str, Any]]:
        """
        搜索相似题目

        Args:
            query: 搜索关键词
            topk: 返回前k个结果
            threshold: 相似度阈值

        Returns:
            List[Dict]: 搜索结果列表
        """
        logger.info(
            f"开始搜索题目，关键词: {query}, topk: {topk}, threshold: {threshold}"
        )

        session = None
        try:
            session = self._get_db_session()

            # 查询所有题目
            questions = session.query(Question).all()
            logger.debug(f"从数据库加载了 {len(questions)} 道题目")

            # 计算相似度并筛选
            results: List[Tuple[float, Question]] = []
            for question in questions:
                question_text = (question.question or "").strip()
                score = self.similarity(query, question_text)
                if score >= threshold:
                    results.append((score, question))

            # 按相似度排序并取前topk个
            results.sort(key=lambda x: x[0], reverse=True)
            results = results[:topk]

            # 构建返回结果
            formatted_results = []
            for score, question in results:
                question_data = {
                    "type": question.type,
                    "question": question.question,
                    "optionA": question.optionA,
                    "optionB": question.optionB,
                    "optionC": question.optionC,
                    "optionD": question.optionD,
                    "optionAnswer": question.optionAnswer,
                }

                result_item = {
                    "score": round(float(score), 6),
                    "type": question.type,
                    "question": question.question,
                    "options": {
                        k[-1]: question_data.get(k)
                        for k in ["optionA", "optionB", "optionC", "optionD"]
                        if question_data.get(k)
                    },
                    "answer": self.extract_answer_struct(question_data),
                }
                formatted_results.append(result_item)

            logger.info(f"搜索完成，返回 {len(formatted_results)} 个结果")
            return formatted_results

        except Exception as e:
            logger.error(f"搜索题目时发生错误: {e}")
            raise
        finally:
            if session:
                session.close()
                logger.debug("题库数据库会话已关闭")


# 创建全局服务实例
question_search_service = QuestionSearchService()
