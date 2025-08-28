# app/services/classtable.py
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from loguru import logger

from app.schemas.classtable import (
    CourseInfo,
    DayCourses,
    WeekCourses,
    DayClassTableResponse,
    WeekClassTableResponse,
)
from app.services.base import BaseEducationService


class ClassTableService(BaseEducationService):
    """课程表服务类"""

    @staticmethod
    def parse_course_info(course_element) -> Optional[CourseInfo]:
        """
        解析课程信息元素

        Args:
            course_element: BeautifulSoup解析的课程元素

        Returns:
            CourseInfo: 课程信息对象，如果解析失败返回None
        """
        try:
            # 获取title属性中的详细信息
            title = course_element.get("title", "")
            course_name = course_element.get_text(strip=True)

            if not title or not course_name:
                return None

            # 解析title中的信息
            # 格式：课程学分：3<br/>课程属性：任选<br/>课程名称：网络管理<br/>上课时间：第1周 星期一 [02-03-04]节<br/>上课地点：嵌入式实验室204<br/>课堂名称：23网安班,22网安班

            # 使用正则表达式提取各个字段
            credits_match = re.search(r"课程学分：([^<]+)", title)
            property_match = re.search(r"课程属性：([^<]+)", title)
            name_match = re.search(r"课程名称：([^<]+)", title)
            time_match = re.search(r"上课时间：([^<]+)", title)
            location_match = re.search(r"上课地点：([^<]+)", title)
            class_match = re.search(r"课堂名称：([^<]+)", title)

            # 从上课时间中提取星期几
            day_of_week = 0
            period = ""
            if time_match:
                time_info = time_match.group(1)
                # 提取星期信息
                weekday_match = re.search(r"星期([一二三四五六日])", time_info)
                if weekday_match:
                    weekday_map = {
                        "一": 1,
                        "二": 2,
                        "三": 3,
                        "四": 4,
                        "五": 5,
                        "六": 6,
                        "日": 7,
                    }
                    day_of_week = weekday_map.get(weekday_match.group(1), 0)

                # 提取节次信息
                period_match = re.search(r"\[([^\]]+)\]节", time_info)
                if period_match:
                    period = period_match.group(1)

            return CourseInfo(
                course_name=name_match.group(1) if name_match else course_name,
                course_credits=credits_match.group(1) if credits_match else "",
                course_property=property_match.group(1) if property_match else "",
                class_time=time_match.group(1) if time_match else "",
                classroom=location_match.group(1) if location_match else "",
                class_name=class_match.group(1) if class_match else "",
                day_of_week=day_of_week,
                period=period,
            )

        except Exception as e:
            logger.error(f"解析课程信息失败: {e}")
            return None

    @staticmethod
    def parse_week_number(html_content: str) -> int:
        """从HTML中解析当前周数"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            week_element = soup.find("span", class_="main_text main_color")
            if week_element:
                week_text = week_element.get_text()
                week_match = re.search(r"第(\d+)周", week_text)
                if week_match:
                    return int(week_match.group(1))
            return 1
        except Exception as e:
            logger.error(f"解析周数失败: {e}")
            return 1

    @staticmethod
    def calculate_week_dates(query_date: str, week_number: int) -> tuple[str, str]:
        """
        计算指定周的开始和结束日期

        Args:
            query_date: 查询日期字符串
            week_number: 周数

        Returns:
            tuple: (开始日期, 结束日期)
        """
        try:
            date_obj = datetime.strptime(query_date, "%Y-%m-%d")

            # 计算本周一的日期
            days_since_monday = date_obj.weekday()
            monday = date_obj - timedelta(days=days_since_monday)

            # 计算本周日的日期
            sunday = monday + timedelta(days=6)

            return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"计算周日期失败: {e}")
            return query_date, query_date

    @staticmethod
    def parse_html_to_courses(
        html_content: str, query_date: str
    ) -> Dict[str, DayCourses]:
        """
        解析HTML内容为课程表数据

        Args:
            html_content: 教务系统返回的HTML内容
            query_date: 查询日期

        Returns:
            Dict[str, DayCourses]: 以日期为key的课程数据字典
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 解析周数
            week_number = ClassTableService.parse_week_number(html_content)

            # 计算周的开始和结束日期
            start_date, end_date = ClassTableService.calculate_week_dates(
                query_date, week_number
            )

            # 初始化一周的课程数据字典
            week_courses_dict = {}

            # 计算本周每一天的日期
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            for i in range(7):
                day_date = start_date_obj + timedelta(days=i)
                date_str = day_date.strftime("%Y-%m-%d")
                day_courses = DayCourses(date=date_str, day_of_week=i + 1, courses=[])
                week_courses_dict[date_str] = day_courses

            # 查找课程表
            table = soup.find("table", class_="kb_table")
            if not table:
                logger.warning("未找到课程表")
                return week_courses_dict

            # 解析每一行
            tbody = table.find("tbody")  # type: ignore
            if not tbody:
                logger.warning("未找到课程表tbody")
                return week_courses_dict
            rows = tbody.find_all("tr")  # type: ignore

            for row_idx, row in enumerate(rows):
                cells = row.find_all("td")  # type: ignore
                if len(cells) < 8:  # 至少应该有8列（节次+7天）
                    continue

                # 跳过第一列（节次列），处理7天的课程
                for day_idx in range(7):
                    if day_idx + 1 >= len(cells):
                        continue

                    cell = cells[day_idx + 1]
                    course_elements = cell.find_all("p")  # type: ignore

                    for course_element in course_elements:
                        course_info = ClassTableService.parse_course_info(
                            course_element
                        )
                        if course_info:
                            # 如果课程信息中没有指定星期几，使用当前列的索引
                            if course_info.day_of_week == 0:
                                course_info.day_of_week = day_idx + 1

                            # 计算对应的日期
                            day_date = start_date_obj + timedelta(days=day_idx)
                            date_str = day_date.strftime("%Y-%m-%d")

                            # 添加到对应天的课程列表前先检查是否重复
                            if date_str in week_courses_dict:
                                existing_courses = week_courses_dict[date_str].courses

                                # 检查是否存在完全相同的课程
                                is_duplicate = False
                                for existing_course in existing_courses:
                                    if (
                                        existing_course.course_name
                                        == course_info.course_name
                                        and existing_course.course_credits
                                        == course_info.course_credits
                                        and existing_course.course_property
                                        == course_info.course_property
                                        and existing_course.class_time
                                        == course_info.class_time
                                        and existing_course.classroom
                                        == course_info.classroom
                                        and existing_course.class_name
                                        == course_info.class_name
                                        and existing_course.day_of_week
                                        == course_info.day_of_week
                                        and existing_course.period == course_info.period
                                    ):
                                        is_duplicate = True
                                        break

                                # 只有不重复的课程才添加
                                if not is_duplicate:
                                    week_courses_dict[date_str].courses.append(
                                        course_info
                                    )

            logger.info(
                f"成功解析课程表，周数: {week_number}, 日期范围: {start_date} - {end_date}"
            )
            return week_courses_dict

        except Exception as e:
            logger.error(f"解析HTML课程表失败: {e}")
            raise HTTPException(status_code=500, detail=f"解析课程表数据失败: {str(e)}")

    @staticmethod
    def get_classtable(
        session: requests.Session, query_date: str
    ) -> Dict[str, DayCourses]:
        """
        获取指定日期所在周的课程表信息

        Args:
            session: 已登录的教务系统session
            query_date: 查询日期 (YYYY-MM-DD)

        Returns:
            Dict[str, DayCourses]: 以日期为key的课程表数据
        """
        try:
            logger.info(f"开始获取课程表，查询日期: {query_date}")

            # 构建请求
            url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/main_index_loadkb.jsp"

            headers = {
                "Accept": "text/html, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "http://zhjw.qfnu.edu.cn",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain_new.jsp?t1=1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }

            # 请求数据
            data = {"rq": query_date}

            logger.debug(f"发送课程表请求到: {url}")
            logger.debug(f"请求参数: {data}")

            response = session.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            # 检查响应内容
            if not response.text:
                raise HTTPException(status_code=500, detail="教务系统返回空内容")

            logger.debug("课程表请求成功，开始解析HTML")

            # 解析HTML内容
            week_courses_dict = ClassTableService.parse_html_to_courses(
                response.text, query_date
            )

            total_courses = sum(len(day.courses) for day in week_courses_dict.values())
            logger.info(f"课程表获取成功，共解析到 {total_courses} 门课程")
            return week_courses_dict

        except requests.exceptions.RequestException as e:
            logger.error(f"课程表请求失败: {e}")
            raise HTTPException(status_code=503, detail=f"教务系统连接失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取课程表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取课程表失败: {str(e)}")

    @staticmethod
    def get_day_courses(session: requests.Session, query_date: str) -> DayCourses:
        """
        获取指定日期当天的课程表信息

        Args:
            session: 已登录的教务系统session
            query_date: 查询日期 (YYYY-MM-DD)

        Returns:
            DayCourses: 当天课程数据
        """
        try:
            # 获取整周课程表
            week_courses_dict = ClassTableService.get_classtable(session, query_date)

            # 查找指定日期的课程
            if query_date in week_courses_dict:
                day_courses = week_courses_dict[query_date]
                logger.info(
                    f"找到指定日期 {query_date} 的课程，共 {len(day_courses.courses)} 门"
                )
                return day_courses

            # 如果没找到指定日期，创建一个空的当天课程对象
            target_date = datetime.strptime(query_date, "%Y-%m-%d")
            target_weekday = target_date.weekday() + 1  # 转换为1-7的星期表示

            logger.warning(f"未找到指定日期 {query_date} 的课程数据，返回空课程表")
            return DayCourses(date=query_date, day_of_week=target_weekday, courses=[])

        except Exception as e:
            logger.error(f"获取当天课程失败: {e}")
            raise e

    @staticmethod
    def get_week_courses(session: requests.Session, query_date: str) -> WeekCourses:
        """
        获取指定日期所在周的完整课程表信息

        Args:
            session: 已登录的教务系统session
            query_date: 查询日期 (YYYY-MM-DD)

        Returns:
            WeekCourses: 整周课程数据
        """
        try:
            # 获取整周课程表字典
            week_courses_dict = ClassTableService.get_classtable(session, query_date)

            # 解析周数
            # 这里我们需要重新获取HTML来解析周数，但为了效率可以从现有数据推算
            week_number = ClassTableService._calculate_week_number(query_date)

            # 计算周的开始和结束日期
            start_date, end_date = ClassTableService.calculate_week_dates(
                query_date, week_number
            )

            # 构建WeekCourses对象
            days_list = []
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")

            for i in range(7):
                day_date = start_date_obj + timedelta(days=i)
                date_str = day_date.strftime("%Y-%m-%d")

                # 从字典中获取对应日期的课程，如果没有则创建空的
                if date_str in week_courses_dict:
                    day_courses = week_courses_dict[date_str]
                else:
                    day_courses = DayCourses(
                        date=date_str, day_of_week=i + 1, courses=[]
                    )

                days_list.append(day_courses)

            week_courses = WeekCourses(
                week_number=week_number,
                start_date=start_date,
                end_date=end_date,
                days=days_list,
            )

            total_courses = sum(len(day.courses) for day in days_list)
            logger.info(
                f"获取周课程表成功，日期范围: {start_date} - {end_date}, 共 {total_courses} 门课程"
            )

            return week_courses

        except Exception as e:
            logger.error(f"获取周课程表失败: {e}")
            raise e

    @staticmethod
    def _calculate_week_number(query_date: str) -> int:
        """
        简单计算周数（基于日期推算）

        Args:
            query_date: 查询日期 (YYYY-MM-DD)

        Returns:
            int: 周数
        """
        try:
            # 这里使用简单的推算方法
            # 实际项目中可能需要根据学期开始时间来精确计算
            date_obj = datetime.strptime(query_date, "%Y-%m-%d")

            # 假设9月1日为第1周开始（可以根据实际情况调整）
            semester_start = datetime(date_obj.year, 9, 1)
            if date_obj < semester_start:
                # 如果查询日期在9月之前，可能是上学期，使用上一年
                semester_start = datetime(date_obj.year - 1, 9, 1)

            days_diff = (date_obj - semester_start).days
            week_number = (days_diff // 7) + 1

            return max(1, week_number)  # 确保周数至少为1

        except Exception as e:
            logger.warning(f"计算周数失败: {e}, 返回默认值1")
            return 1
