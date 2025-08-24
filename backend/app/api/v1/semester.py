from fastapi import APIRouter
from app.utils.semester_calculator import get_semester_calculator
from loguru import logger

router = APIRouter()


@router.get(
    "/semester-info",
    summary="获取学期信息",
    description="获取所有年级的当前学期数据",
    tags=["学期工具"],
)
async def get_semester_info():
    """
    获取学期信息

    返回所有年级（当年到前五年）的当前学期数据

    Returns:
        dict: 包含学期数据的响应
    """
    try:
        logger.info("请求获取学期信息")
        calculator = get_semester_calculator()

        # 获取所有学期数据
        semester_data = calculator.get_all_semester_data()

        # 获取详细信息字符串
        info_string = calculator.get_semester_info_string()

        # 构造响应
        response = {
            "success": True,
            "message": "学期信息获取成功",
            "data": {
                "semester_mapping": semester_data,
                "info_string": info_string,
                "last_update": (
                    calculator.last_update_time.isoformat()
                    if calculator.last_update_time
                    else None
                ),
            },
        }

        logger.info("学期信息获取成功")
        return response

    except Exception as e:
        logger.error(f"获取学期信息失败: {e}")
        return {
            "success": False,
            "message": f"获取学期信息失败: {str(e)}",
            "data": None,
        }


@router.get(
    "/semester-info/{grade_year}",
    summary="获取指定年级学期信息",
    description="获取指定年级的当前学期数",
    tags=["学期工具"],
)
async def get_grade_semester_info(grade_year: int):
    """
    获取指定年级的学期信息

    Args:
        grade_year: 年级年份，如2022表示2022级

    Returns:
        dict: 包含指定年级学期数据的响应
    """
    try:
        logger.info(f"请求获取{grade_year}级的学期信息")
        calculator = get_semester_calculator()

        # 获取指定年级的学期数
        semester_num = calculator.get_semester_for_grade(grade_year)

        response = {
            "success": True,
            "message": f"{grade_year}级学期信息获取成功",
            "data": {
                "grade_year": grade_year,
                "current_semester": semester_num,
                "last_update": (
                    calculator.last_update_time.isoformat()
                    if calculator.last_update_time
                    else None
                ),
            },
        }

        logger.info(f"{grade_year}级当前是第{semester_num}学期")
        return response

    except Exception as e:
        logger.error(f"获取{grade_year}级学期信息失败: {e}")
        return {
            "success": False,
            "message": f"获取{grade_year}级学期信息失败: {str(e)}",
            "data": None,
        }


@router.post(
    "/semester-info/refresh",
    summary="刷新学期数据",
    description="强制刷新学期计算器的数据",
    tags=["学期工具"],
)
async def refresh_semester_data():
    """
    刷新学期数据

    强制重新计算所有年级的学期数据

    Returns:
        dict: 刷新操作的结果
    """
    try:
        logger.info("请求强制刷新学期数据")
        calculator = get_semester_calculator()

        # 强制更新数据
        calculator.update_semester_data(force_update=True)

        # 获取更新后的数据
        semester_data = calculator.get_all_semester_data()
        info_string = calculator.get_semester_info_string()

        response = {
            "success": True,
            "message": "学期数据刷新成功",
            "data": {
                "semester_mapping": semester_data,
                "info_string": info_string,
                "last_update": calculator.last_update_time.isoformat(),
            },
        }

        logger.info("学期数据刷新成功")
        return response

    except Exception as e:
        logger.error(f"刷新学期数据失败: {e}")
        return {
            "success": False,
            "message": f"刷新学期数据失败: {str(e)}",
            "data": None,
        }
