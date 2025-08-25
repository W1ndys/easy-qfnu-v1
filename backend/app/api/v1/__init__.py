from fastapi import APIRouter
from loguru import logger

# 导入所有路由模块
try:
    from .auth import router as auth_router

    logger.debug("认证路由模块导入成功")
except ImportError as e:
    logger.error(f"导入认证路由模块失败: {e}")
    auth_router = None

try:
    from .grades import router as grades_router

    logger.debug("成绩路由模块导入成功")
except ImportError as e:
    logger.error(f"导入成绩路由模块失败: {e}")
    grades_router = None

try:
    from .average_scores import router as average_scores_router

    logger.debug("平均分路由模块导入成功")
except ImportError as e:
    logger.error(f"导入平均分路由模块失败: {e}")
    average_scores_router = None

try:
    from .course_plan import router as course_plan_router

    logger.debug("课程规划路由模块导入成功")
except ImportError as e:
    logger.error(f"导入课程规划路由模块失败: {e}")
    course_plan_router = None

try:
    from .freshman_questions_search import router as freshman_questions_search_router

    logger.debug("题库搜索路由模块导入成功")
except ImportError as e:
    logger.error(f"导入题库搜索路由模块失败: {e}")
    freshman_questions_search_router = None

try:
    from .semester import router as semester_router

    logger.debug("学期工具路由模块导入成功")
except ImportError as e:
    logger.error(f"导入学期工具路由模块失败: {e}")
    semester_router = None

try:
    from .profile import router as profile_router

    logger.debug("个人信息路由模块导入成功")
except ImportError as e:
    logger.error(f"导入个人信息路由模块失败: {e}")
    profile_router = None

try:
    from .pre_select_course_query import router as pre_select_course_query_router

    logger.debug("预选课查询路由模块导入成功")
except ImportError as e:
    logger.error(f"导入预选课查询路由模块失败: {e}")
    pre_select_course_query_router = None


# 创建主API路由器
api_router = APIRouter()

# 路由配置列表，格式：(router, prefix, name)
ROUTER_CONFIGS = [
    (auth_router, "", "认证"),
    (grades_router, "", "成绩"),
    (average_scores_router, "", "平均分查询"),
    (course_plan_router, "", "培养方案"),
    (freshman_questions_search_router, "/question", "题库搜索"),
    (semester_router, "", "学期工具"),
    (profile_router, "", "个人信息"),
    (pre_select_course_query_router, "", "预选课查询"),
]


def register_routes():
    """统一注册所有路由"""
    registered_count = 0
    failed_count = 0

    logger.info("开始注册API路由...")

    for router, prefix, name in ROUTER_CONFIGS:
        if router is None:
            logger.warning(f"跳过注册{name}路由：模块导入失败")
            failed_count += 1
            continue

        try:
            api_router.include_router(router, prefix=prefix)
            logger.info(
                f"{name}路由注册成功" + (f" (前缀: {prefix})" if prefix else "")
            )
            registered_count += 1
        except Exception as e:
            logger.error(f"{name}路由注册失败: {e}")
            failed_count += 1

    logger.info(f"路由注册完成: 成功 {registered_count} 个，失败 {failed_count} 个")
    return registered_count, failed_count


# 自动注册路由
register_routes()
