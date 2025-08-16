"""
课表服务
处理课程表查询相关的业务逻辑
"""

import requests
import logging
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

from app.core.config import settings
from app.core.security import SessionExpiredError
from app.core.database import DatabaseManager
from app.services.auth_service import AuthService
from app.models.schedule import Schedule, CourseInfo, ScheduleResponse, CourseCapacity

logger = logging.getLogger(__name__)


class ScheduleService:
    """课表服务类"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.auth_service = AuthService(db)

    async def get_student_schedule(
        self,
        student_id: str,
        week: Optional[int] = None,
        semester: Optional[str] = None,
    ) -> ScheduleResponse:
        """
        获取学生课程表

        Args:
            student_id: 学号
            week: 周次
            semester: 学期

        Returns:
            课表响应数据
        """
        try:
            # 获取用户的Session
            session_data = await self.auth_service.get_session(student_id)
            if not session_data:
                raise SessionExpiredError("Session不存在或已过期")

            # 创建请求会话
            session = requests.Session()
            session.cookies.update(session_data.get("cookies", {}))

            # 构造课表查询参数
            params = {}
            if week:
                params["zc"] = str(week)
            if semester:
                params["xnxq01id"] = semester

            # 发送课表查询请求
            response = session.get(
                settings.QFNU_SCHEDULE_URL, params=params, timeout=10
            )

            # 检查是否需要重新登录
            if "login" in response.url.lower():
                await self.auth_service.clear_session(student_id)
                raise SessionExpiredError("Session已过期")

            # 解析课表数据
            schedule_data = self._parse_schedule_html(response.text)

            # 获取当前周次和学期信息
            current_week = week or self._get_current_week()
            current_semester = semester or self._get_current_semester()

            logger.info(f"成功获取学号 {student_id} 的课表数据")

            return ScheduleResponse(
                schedule=schedule_data,
                current_week=current_week,
                semester=current_semester,
            )

        except requests.RequestException as e:
            logger.error(f"获取课表请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取课表过程发生错误: {e}")
            raise

    def _parse_schedule_html(self, html_content: str) -> List[Schedule]:
        """
        解析课表页面HTML，提取课表数据

        Args:
            html_content: 课表页面HTML内容

        Returns:
            解析出的课表列表
        """
        schedule_list = []

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 查找课表表格（根据实际页面结构调整）
            schedule_table = soup.find("table", {"id": "kbtable"}) or soup.find(
                "table", class_="kbcontent"
            )

            if not schedule_table:
                logger.warning("未找到课表表格")
                return schedule_list

            # 解析课表网格
            rows = schedule_table.find_all("tr")

            for row_idx, row in enumerate(rows[1:], 1):  # 跳过表头
                cells = row.find_all(["td", "th"])

                for col_idx, cell in enumerate(cells[1:], 1):  # 跳过时间列
                    course_divs = cell.find_all("div", class_="kbcontent")

                    for course_div in course_divs:
                        course_text = course_div.get_text(strip=True)
                        if course_text and course_text != "&nbsp;":
                            schedule_item = self._parse_course_text(
                                course_text, col_idx, row_idx
                            )
                            if schedule_item:
                                schedule_list.append(schedule_item)

        except Exception as e:
            logger.error(f"解析课表HTML时出错: {e}")

        return schedule_list

    def _parse_course_text(
        self, course_text: str, week_day: int, time_slot: int
    ) -> Optional[Schedule]:
        """
        解析课程文本信息

        Args:
            course_text: 课程文本
            week_day: 星期几
            time_slot: 时间段

        Returns:
            课程表条目
        """
        try:
            # 使用正则表达式解析课程信息
            # 典型格式：高等数学(1-16周)张三老师A101
            lines = course_text.split("\n")
            if not lines:
                return None

            course_name = lines[0].strip()
            teacher = ""
            location = ""
            weeks = ""

            # 提取教师、地点、周次信息
            for line in lines[1:]:
                line = line.strip()
                if "周" in line:
                    weeks = line
                elif re.match(r"[A-Z]\d+", line):  # 教室格式
                    location = line
                else:
                    teacher = line

            # 生成时间信息
            start_time, end_time, class_period = self._get_time_info(time_slot)

            course_info = CourseInfo(
                course_id=f"{course_name}_{week_day}_{time_slot}",  # 临时ID
                course_name=course_name,
                teacher=teacher,
                location=location,
            )

            return Schedule(
                course_info=course_info,
                week_day=week_day,
                start_time=start_time,
                end_time=end_time,
                weeks=weeks,
                class_period=class_period,
            )

        except Exception as e:
            logger.warning(f"解析课程文本失败: {e}")
            return None

    def _get_time_info(self, time_slot: int) -> tuple[str, str, str]:
        """
        根据时间段获取具体时间信息

        Args:
            time_slot: 时间段序号

        Returns:
            (开始时间, 结束时间, 节次)
        """
        time_mapping = {
            1: ("08:00", "08:45", "1节"),
            2: ("08:55", "09:40", "2节"),
            3: ("10:00", "10:45", "3节"),
            4: ("10:55", "11:40", "4节"),
            5: ("14:00", "14:45", "5节"),
            6: ("14:55", "15:40", "6节"),
            7: ("16:00", "16:45", "7节"),
            8: ("16:55", "17:40", "8节"),
            9: ("19:00", "19:45", "9节"),
            10: ("19:55", "20:40", "10节"),
        }

        return time_mapping.get(time_slot, ("00:00", "00:00", f"{time_slot}节"))

    def _get_current_week(self) -> int:
        """
        获取当前周次（这里需要根据学校的校历来实现）

        Returns:
            当前周次
        """
        # 简单实现：假设学期开始日期
        # 实际应用中需要根据学校校历配置
        semester_start = datetime(2024, 9, 1)  # 假设学期开始日期
        current_date = datetime.now()
        weeks_passed = (current_date - semester_start).days // 7
        return max(1, min(weeks_passed + 1, 20))  # 限制在1-20周

    def _get_current_semester(self) -> str:
        """
        获取当前学期

        Returns:
            当前学期字符串
        """
        current_date = datetime.now()
        year = current_date.year

        # 简单判断学期
        if current_date.month >= 9 or current_date.month <= 1:
            return f"{year}-{year+1}-1"  # 第一学期
        else:
            return f"{year-1}-{year}-2"  # 第二学期

    async def get_today_courses(self, student_id: str) -> List[Schedule]:
        """
        获取今日课程

        Args:
            student_id: 学号

        Returns:
            今日课程列表
        """
        try:
            # 获取完整课表
            full_schedule = await self.get_student_schedule(student_id)

            # 获取今天是星期几
            today_weekday = datetime.now().weekday() + 1  # 转换为1-7

            # 筛选今日课程
            today_courses = [
                course
                for course in full_schedule.schedule
                if course.week_day == today_weekday
            ]

            # 按时间排序
            today_courses.sort(key=lambda x: x.start_time)

            return today_courses

        except Exception as e:
            logger.error(f"获取今日课程失败: {e}")
            raise

    def get_current_date(self) -> str:
        """
        获取当前日期

        Returns:
            格式化的当前日期
        """
        return datetime.now().strftime("%Y-%m-%d")

    async def get_course_capacity(
        self, student_id: str, course_id: str
    ) -> CourseCapacity:
        """
        获取课程容量信息

        Args:
            student_id: 学号
            course_id: 课程ID

        Returns:
            课程容量信息
        """
        try:
            # 获取用户的Session
            session_data = await self.auth_service.get_session(student_id)
            if not session_data:
                raise SessionExpiredError("Session不存在或已过期")

            # 创建请求会话
            session = requests.Session()
            session.cookies.update(session_data.get("cookies", {}))

            # 构造选课查询URL
            capacity_url = f"{settings.QFNU_LOGIN_URL.replace('/jsxsd/xk/LoginToXk', '/jsxsd/xsxk/xsxk_index')}"

            # 发送容量查询请求
            response = session.get(
                capacity_url, params={"course_id": course_id}, timeout=10
            )

            # 检查是否需要重新登录
            if "login" in response.url.lower():
                await self.auth_service.clear_session(student_id)
                raise SessionExpiredError("Session已过期")

            # 解析容量信息（这里需要根据实际页面结构实现）
            capacity_info = self._parse_capacity_html(response.text, course_id)

            return capacity_info

        except requests.RequestException as e:
            logger.error(f"获取课程容量请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取课程容量过程发生错误: {e}")
            raise

    def _parse_capacity_html(
        self, html_content: str, course_id: str
    ) -> CourseCapacity:
        """
        解析课程容量页面HTML

        Args:
            html_content: 页面HTML内容
            course_id: 课程ID

        Returns:
            课程容量信息
        """
        # 默认返回模拟数据，实际应用中需要根据页面结构解析
        return CourseCapacity(
            course_id=course_id,
            course_name="示例课程",
            total_capacity=50,
            enrolled_count=35,
            available_spots=15,
            is_full=False,
        )
