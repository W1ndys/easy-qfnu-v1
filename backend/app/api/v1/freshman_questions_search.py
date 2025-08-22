"""
新生题库搜索API模块

本模块提供基于语义搜索的题库查询功能，支持通过关键词搜索相关题目和答案。
使用向量相似度匹配算法，为用户提供最相关的搜索结果。

作者: W1ndys
创建时间: 2024
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from loguru import logger

from app.services.freshman_questions_search import question_search_service

# 创建API路由器，用于题库搜索相关接口
router = APIRouter(tags=["题库搜索"])


class QuestionSearchRequest(BaseModel):
    """
    题库搜索请求数据模型

    用于封装客户端发送的搜索请求参数，包括搜索关键词、
    返回结果数量和相似度阈值等配置信息。

    Attributes:
        query (str): 搜索关键词，支持中文和英文
        topk (int): 返回的最大结果数量，默认为3，范围1-10
        threshold (float): 相似度阈值，默认为0.55，范围0-1
    """

    query: str = Field(..., description="搜索关键词，不能为空", example="计算机网络")
    topk: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="返回结果数量，范围1-10",
        example=3,
    )
    threshold: Optional[float] = Field(
        default=0.55,
        ge=0,
        le=1,
        description="相似度阈值，范围0-1，值越高结果越精确",
        example=0.55,
    )


class QuestionSearchResponse(BaseModel):
    """
    题库搜索响应数据模型

    封装搜索结果和相关元数据，为客户端提供结构化的响应信息。

    Attributes:
        ok (bool): 请求是否成功
        query (str): 原始搜索关键词
        topk (int): 实际返回的最大结果数量
        threshold (float): 使用的相似度阈值
        count (int): 实际返回的结果数量
        results (List[Dict]): 搜索结果列表，每个结果包含题目、答案、相似度等信息
    """

    ok: bool = Field(description="请求是否成功", example=True)
    query: str = Field(description="搜索关键词", example="计算机网络")
    topk: int = Field(description="返回结果数量", example=3)
    threshold: float = Field(description="相似度阈值", example=0.55)
    count: int = Field(description="实际返回的结果数量", example=2)
    results: List[Dict[str, Any]] = Field(
        description="搜索结果列表",
        example=[
            {
                "question": "什么是计算机网络？",
                "answer": "计算机网络是指将地理位置不同的具有独立功能的多台计算机及其外部设备...",
                "similarity": 0.85,
                "source": "教材第一章",
            }
        ],
    )


@router.post(
    "/freshman-question-search",
    response_model=QuestionSearchResponse,
    summary="题库搜索（POST方式）",
    description="根据输入的关键词，使用语义搜索算法查找相似度最高的题目及其答案",
)
async def search_questions(request: QuestionSearchRequest):
    """
    题库搜索接口（POST方式）

    使用向量相似度算法，根据输入的关键词搜索题库中最相关的题目和答案。
    支持中文和英文关键词搜索，返回按相似度排序的结果列表。

    Args:
        request (QuestionSearchRequest): 搜索请求参数
            - query: 搜索关键词，必填
            - topk: 返回结果数量，可选，默认3
            - threshold: 相似度阈值，可选，默认0.55

    Returns:
        QuestionSearchResponse: 搜索结果响应
            - ok: 请求状态
            - query: 原始搜索词
            - topk: 返回数量
            - threshold: 相似度阈值
            - count: 实际结果数
            - results: 题目和答案列表

    Raises:
        HTTPException:
            - 400: 参数验证失败（关键词为空、topk或threshold超出范围）
            - 500: 服务器内部错误

    Example:
        POST /api/v1/freshman-question-search
        {
            "query": "计算机网络",
            "topk": 5,
            "threshold": 0.6
        }
    """
    try:
        logger.info(f"接收到题库搜索请求: {request.query}")

        # 参数验证
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")

        if request.topk < 1 or request.topk > 10:
            raise HTTPException(status_code=400, detail="topk参数必须在1-10之间")

        if request.threshold < 0 or request.threshold > 1:
            raise HTTPException(status_code=400, detail="threshold参数必须在0-1之间")

        # 执行搜索
        results = question_search_service.search_questions(
            query=request.query.strip(), topk=request.topk, threshold=request.threshold
        )

        response = QuestionSearchResponse(
            ok=True,
            query=request.query.strip(),
            topk=request.topk,
            threshold=request.threshold,
            count=len(results),
            results=results,
        )

        logger.info(f"题库搜索完成，返回 {len(results)} 个结果")
        return response

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"题库搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get(
    "/freshman-question-search",
    response_model=QuestionSearchResponse,
    summary="题库搜索（GET方式）",
    description="通过URL参数进行题库搜索，适用于简单的搜索场景",
)
async def search_questions_get(
    query: str = Query(
        ...,
        description="搜索关键词，支持中文和英文",
        example="计算机网络",
        min_length=1,
        max_length=100,
    ),
    topk: int = Query(
        default=3,
        ge=1,
        le=10,
        description="返回的最大结果数量，默认3个",
        example=3,
    ),
    threshold: float = Query(
        default=0.55,
        ge=0,
        le=1,
        description="相似度阈值，默认0.55，值越高结果越精确",
        example=0.55,
    ),
):
    """
    题库搜索接口（GET方式）

    通过URL查询参数进行题库搜索，功能与POST接口相同，
    但更适合于简单的搜索场景和第三方集成。

    Args:
        query (str): 搜索关键词，长度1-100字符
        topk (int): 返回结果数量，范围1-10，默认3
        threshold (float): 相似度阈值，范围0-1，默认0.55

    Returns:
        QuestionSearchResponse: 与POST接口相同的响应格式

    Raises:
        HTTPException: 与POST接口相同的异常处理

    Example:
        GET /api/v1/freshman-question-search?query=计算机网络&topk=5&threshold=0.6
    """
    # 构造请求对象并复用POST接口的逻辑
    request = QuestionSearchRequest(query=query, topk=topk, threshold=threshold)
    return await search_questions(request)
