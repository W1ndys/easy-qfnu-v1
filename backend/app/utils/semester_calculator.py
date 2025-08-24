# app/utils/semester_calculator.py

import datetime
from typing import Dict, Tuple
from loguru import logger


class SemesterCalculator:
    """学期计算器类 - 用于计算各年级当前所在学期"""

    def __init__(self):
        self.semester_data: Dict[int, int] = {}
        self.last_update_time: datetime.datetime = None
        self.current_year: int = None
        self.current_month: int = None
        self.logger = logger

    def get_current_semester_info(self) -> Tuple[int, int]:
        """
        获取当前学期信息

        Returns:
            tuple: (当前年份, 当前月份)
        """
        now = datetime.datetime.now()
        return now.year, now.month

    def calculate_semester_for_grade(
        self, grade_year: int, current_year: int, current_month: int
    ) -> int:
        """
        计算指定年级在当前时间的学期数

        Args:
            grade_year: 年级年份 (如2022表示2022级)
            current_year: 当前年份
            current_month: 当前月份 (1-12)

        Returns:
            int: 当前学期数 (1-8)

        学期划分规则:
        - 第1学期: 入学年8月-次年1月 (8,9,10,11,12,1月)
        - 第2学期: 入学年次年2月-7月 (2,3,4,5,6,7月)
        - 第3学期: 入学年次年8月-第三年1月
        - 以此类推...
        - 8月暑假和1月寒假都算在奇数学期里
        """

        # 计算从入学到现在经过了多少年
        years_passed = current_year - grade_year

        # 根据月份判断当前处于哪个学期阶段
        if current_month >= 9:  # 9-12月，属于秋季学期
            semester_in_year = 1  # 奇数学期
        elif current_month >= 8:  # 8月，暑假，算作下一个秋季学期（奇数学期）
            semester_in_year = 1  # 奇数学期
        elif current_month >= 2:  # 2-7月，属于春季学期
            semester_in_year = 2  # 偶数学期
        else:  # 1月，寒假，算作上一年的春季学期的延续，但实际是奇数学期的结束
            semester_in_year = 1
            years_passed -= 1  # 1月属于上一学年

        # 计算总学期数
        total_semester = years_passed * 2 + semester_in_year

        # 确保学期数在合理范围内 (1-8学期)
        if total_semester < 1:
            total_semester = 1
        elif total_semester > 8:
            total_semester = 8

        return total_semester

    def generate_semester_data(self) -> Dict[int, int]:
        """
        生成所有年级的学期数据字典

        Returns:
            dict: {年级年份: 当前学期数}
        """
        current_year, current_month = self.get_current_semester_info()
        semester_dict = {}

        # 计算当年到前五年的数据 (包含当年，共6年)
        for i in range(6):
            grade_year = current_year - i
            semester_num = self.calculate_semester_for_grade(
                grade_year, current_year, current_month
            )
            semester_dict[grade_year] = semester_num

        return semester_dict

    def update_semester_data(self, force_update: bool = False) -> None:
        """
        更新学期数据

        Args:
            force_update: 是否强制更新
        """
        current_year, current_month = self.get_current_semester_info()

        # 检查是否需要更新 (月份或年份发生变化时才更新)
        if (
            not force_update
            and self.last_update_time
            and self.current_year == current_year
            and self.current_month == current_month
        ):
            self.logger.debug("学期数据无需更新")
            return

        self.logger.info(
            f"开始更新学期数据 - 当前时间: {current_year}年{current_month}月"
        )

        # 生成新的学期数据
        new_data = self.generate_semester_data()

        # 更新缓存
        self.semester_data = new_data
        self.last_update_time = datetime.datetime.now()
        self.current_year = current_year
        self.current_month = current_month

        # 记录更新结果
        self.logger.info("学期数据更新完成:")
        for grade_year, semester in self.semester_data.items():
            self.logger.info(f"  {grade_year}级 -> 第{semester}学期")

    def get_semester_for_grade(self, grade_year: int) -> int:
        """
        获取指定年级的当前学期数

        Args:
            grade_year: 年级年份

        Returns:
            int: 当前学期数，如果年级不存在则返回1
        """
        # 确保数据是最新的
        self.update_semester_data()

        return self.semester_data.get(grade_year, 1)

    def get_all_semester_data(self) -> Dict[int, int]:
        """
        获取所有年级的学期数据

        Returns:
            dict: {年级年份: 当前学期数}
        """
        # 确保数据是最新的
        self.update_semester_data()

        return self.semester_data.copy()

    def get_semester_info_string(self) -> str:
        """
        获取学期信息的字符串表示

        Returns:
            str: 格式化的学期信息
        """
        self.update_semester_data()

        info_lines = [
            f"学期数据 (更新时间: {self.last_update_time.strftime('%Y-%m-%d %H:%M:%S')})"
        ]
        for grade_year in sorted(self.semester_data.keys(), reverse=True):
            semester = self.semester_data[grade_year]
            info_lines.append(f"{grade_year}级: 第{semester}学期")

        return "\n".join(info_lines)


# 创建全局实例
semester_calculator = SemesterCalculator()


def get_semester_calculator() -> SemesterCalculator:
    """获取学期计算器实例"""
    return semester_calculator


def init_semester_calculator() -> None:
    """初始化学期计算器 (在应用启动时调用)"""
    logger.info("正在初始化学期计算器...")
    semester_calculator.update_semester_data(force_update=True)
    logger.info("学期计算器初始化完成")
    logger.info(f"\n{semester_calculator.get_semester_info_string()}")


if __name__ == "__main__":
    # 测试代码
    calc = SemesterCalculator()

    print("=== 学期计算器测试 ===")
    print(f"当前时间: {datetime.datetime.now().strftime('%Y年%m月')}")
    print()

    # 测试数据生成
    calc.update_semester_data(force_update=True)
    print(calc.get_semester_info_string())
    print()

    # 测试单个年级查询
    test_grades = [2025, 2024, 2023, 2022, 2021, 2020]
    for grade in test_grades:
        semester = calc.get_semester_for_grade(grade)
        print(f"{grade}级当前是第{semester}学期")
