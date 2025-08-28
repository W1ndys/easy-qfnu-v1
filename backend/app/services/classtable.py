# app/services/classtable.py
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime


class ClassTableService:
    """课程表服务类"""

    @staticmethod
    def validate_and_format_date(date_str: str) -> Optional[str]:
        """
        验证并格式化日期字符串

        Args:
            date_str: 输入的日期字符串

        Returns:
            str: 格式化后的日期字符串 (YYYY-MM-DD)，失败返回None
        """
        try:
            # 支持多种日期格式
            date_formats = [
                "%Y-%m-%d",  # 2025-09-05
                "%Y/%m/%d",  # 2025/09/05
                "%Y.%m.%d",  # 2025.09.05
                "%Y%m%d",  # 20250905
            ]

            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            logger.error(f"无效的日期格式: {date_str}")
            return None

        except Exception as e:
            logger.error(f"日期验证失败: {str(e)}")
            return None

    @staticmethod
    def parse_class_table_html(html_content: str) -> Dict[str, Any]:
        """
        解析课程表HTML内容，转换为JSON格式

        Args:
            html_content: 课程表HTML内容

        Returns:
            Dict: 包含课程表信息的字典
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 查找课程表table
            table = soup.find("table", class_="kb_table")
            if not table:
                logger.error("未找到课程表table元素")
                return {"success": False, "message": "未找到课程表", "data": {}}

            # 初始化结果数据结构 - 前端友好的格式
            result = {
                "success": True,
                "message": "获取成功",
                "data": {
                    "week_info": {
                        "current_week": 1,  # 当前周数
                        "total_weeks": 20,  # 总周数
                    },
                    "time_slots": [
                        {
                            "period": 1,
                            "name": "第一大节",
                            "time": "08:00-09:40",
                            "slots": [1, 2],
                        },
                        {
                            "period": 2,
                            "name": "第二大节",
                            "time": "10:00-11:40",
                            "slots": [3, 4],
                        },
                        {
                            "period": 3,
                            "name": "第三大节",
                            "time": "14:00-15:40",
                            "slots": [5, 6],
                        },
                        {
                            "period": 4,
                            "name": "第四大节",
                            "time": "16:00-17:40",
                            "slots": [7, 8],
                        },
                        {
                            "period": 5,
                            "name": "第五大节",
                            "time": "19:00-21:30",
                            "slots": [9, 10, 11],
                        },
                        {
                            "period": 6,
                            "name": "网课时段",
                            "time": "自由安排",
                            "slots": [12, 13],
                        },
                    ],
                    "weekdays": [
                        {"id": 1, "name": "星期一", "short": "周一"},
                        {"id": 2, "name": "星期二", "short": "周二"},
                        {"id": 3, "name": "星期三", "short": "周三"},
                        {"id": 4, "name": "星期四", "short": "周四"},
                        {"id": 5, "name": "星期五", "short": "周五"},
                        {"id": 6, "name": "星期六", "short": "周六"},
                        {"id": 7, "name": "星期日", "short": "周日"},
                    ],
                    "courses": [],  # 课程列表
                    "stats": {
                        "total_courses": 0,
                        "total_hours": 0,
                        "courses_by_day": {},
                    },
                },
            }

            # 提取周数信息
            week_info = soup.find("span", class_="main_text main_color")
            if week_info:
                week_text = week_info.get_text()
                week_match = re.search(r"第(\d+)周", week_text)
                if week_match:
                    result["data"]["week_info"]["current_week"] = int(
                        week_match.group(1)
                    )

                # 提取总周数
                total_week_match = re.search(r"/(\d+)周", week_text)
                if total_week_match:
                    result["data"]["week_info"]["total_weeks"] = int(
                        total_week_match.group(1)
                    )

            # 获取表格body
            tbody = table.find("tbody")  # type: ignore
            if not tbody:
                return result

            # 定义时间段映射
            time_periods = {
                "第一大节": {
                    "period": 1,
                    "time_slots": [1, 2],
                    "name": "第一大节(01,02小节)",
                },
                "第二大节": {
                    "period": 2,
                    "time_slots": [3, 4],
                    "name": "第二大节(03,04小节)",
                },
                "第三大节": {
                    "period": 3,
                    "time_slots": [5, 6],
                    "name": "第三大节(05,06小节)",
                },
                "第四大节": {
                    "period": 4,
                    "time_slots": [7, 8],
                    "name": "第四大节(07,08小节)",
                },
                "第五大节": {
                    "period": 5,
                    "time_slots": [9, 10, 11],
                    "name": "第五大节(09,10,11小节)",
                },
                "网课不限时": {
                    "period": 6,
                    "time_slots": [12, 13],
                    "name": "网课不限时(12,13小节)",
                },
            }

            # 星期映射
            weekdays = [
                "星期一",
                "星期二",
                "星期三",
                "星期四",
                "星期五",
                "星期六",
                "星期日",
            ]

            # 解析每一行
            rows = tbody.find_all("tr")  # type: ignore
            for row_index, row in enumerate(rows):
                cells = row.find_all("td")  # type: ignore
                if len(cells) < 8:  # 应该有8列（时间段+7天）
                    continue

                # 获取时间段信息
                period_cell = cells[0]
                period_text = period_cell.get_text(strip=True)

                # 确定时间段
                current_period = None
                for period_name, period_info in time_periods.items():
                    if period_name in period_text:
                        current_period = period_info
                        break

                if not current_period:
                    continue

                # 解析每一天的课程
                for day_index, cell in enumerate(cells[1:], 0):  # 跳过第一列（时间段）
                    if day_index >= 7:  # 只处理7天
                        break

                    weekday = weekdays[day_index]

                    # 查找课程信息
                    course_elements = cell.find_all("p")  # type: ignore

                    for course_element in course_elements:
                        course_info = ClassTableService._parse_course_info(
                            course_element
                        )
                        if course_info:
                            # 构建前端友好的课程对象
                            frontend_course = {
                                "id": f"course_{len(result['data']['courses']) + 1}",  # 唯一ID
                                "name": course_info["course_name"],
                                "teacher": course_info.get("teacher", ""),  # 教师信息
                                "location": course_info["location"],
                                "classroom": course_info["location"],  # 别名
                                "credits": course_info["credits"],
                                "course_type": course_info["course_type"],
                                "class_name": course_info["class_name"],
                                "weeks": course_info["weeks"],
                                "time_info": {
                                    "weekday": day_index + 1,  # 1-7
                                    "weekday_name": weekday,
                                    "period": current_period["period"],
                                    "period_name": current_period["name"],
                                    "time_slots": current_period["time_slots"],
                                    "start_time": ClassTableService._get_period_time(
                                        current_period["period"]
                                    )["start"],
                                    "end_time": ClassTableService._get_period_time(
                                        current_period["period"]
                                    )["end"],
                                },
                                "style": {
                                    "row": current_period["period"],  # 第几大节 (1-6)
                                    "col": day_index + 1,  # 第几天 (1-7)
                                    "row_span": 1,  # 占几行
                                    "col_span": 1,  # 占几列
                                },
                                "raw_data": course_info,  # 保留原始数据
                            }

                            result["data"]["courses"].append(frontend_course)
                            result["data"]["stats"]["total_courses"] += 1

                            # 统计每天的课程数
                            day_key = weekday
                            if day_key not in result["data"]["stats"]["courses_by_day"]:
                                result["data"]["stats"]["courses_by_day"][day_key] = 0
                            result["data"]["stats"]["courses_by_day"][day_key] += 1

            # 计算总学时
            result["data"]["stats"]["total_hours"] = (
                result["data"]["stats"]["total_courses"] * 2
            )  # 假设每门课2学时

            logger.info(
                f"课程表解析完成，共解析到{result['data']['stats']['total_courses']}门课程"
            )
            return result

        except Exception as e:
            logger.error(f"解析课程表HTML时出错: {str(e)}")
            return {"success": False, "message": f"解析失败: {str(e)}", "data": {}}

    @staticmethod
    def _parse_course_info(course_element) -> Optional[Dict[str, Any]]:
        """
        解析单个课程信息

        Args:
            course_element: 课程的p元素

        Returns:
            Dict: 课程信息字典，如果解析失败返回None
        """
        try:
            # 获取课程名称
            course_name = course_element.get_text(strip=True)
            if not course_name:
                return None

            # 获取title属性中的详细信息
            title = course_element.get("title", "")
            if not title:
                return None

            course_info = {
                "course_name": course_name,
                "credits": "",
                "course_type": "",
                "time_detail": "",
                "location": "",
                "class_name": "",
                "weeks": [],
            }

            # 解析title中的信息
            title_lines = title.split("<br/>")
            for line in title_lines:
                line = line.strip()
                if line.startswith("课程学分："):
                    course_info["credits"] = line.replace("课程学分：", "")
                elif line.startswith("课程属性："):
                    course_info["course_type"] = line.replace("课程属性：", "")
                elif line.startswith("上课时间："):
                    time_detail = line.replace("上课时间：", "")
                    course_info["time_detail"] = time_detail
                    # 提取周数信息
                    week_match = re.search(r"第(\d+)周", time_detail)
                    if week_match:
                        course_info["weeks"] = [int(week_match.group(1))]
                elif line.startswith("上课地点："):
                    course_info["location"] = line.replace("上课地点：", "")
                elif line.startswith("课堂名称："):
                    course_info["class_name"] = line.replace("课堂名称：", "")

            return course_info

        except Exception as e:
            logger.error(f"解析课程信息时出错: {str(e)}")
            return None

    @staticmethod
    def _get_period_time(period: int) -> Dict[str, str]:
        """
        获取时间段的具体时间

        Args:
            period: 时间段编号 (1-6)

        Returns:
            Dict: 包含开始和结束时间的字典
        """
        time_mapping = {
            1: {"start": "08:00", "end": "09:40"},
            2: {"start": "10:00", "end": "11:40"},
            3: {"start": "14:00", "end": "15:40"},
            4: {"start": "16:00", "end": "17:40"},
            5: {"start": "19:00", "end": "21:30"},
            6: {"start": "自由", "end": "安排"},
        }
        return time_mapping.get(period, {"start": "未知", "end": "时间"})

    @staticmethod
    def get_class_table_data(session: requests.Session, date: str) -> Dict[str, Any]:
        """
        获取课程表数据

        Args:
            session: 请求会话
            date: 日期字符串 (格式: YYYY-MM-DD)

        Returns:
            Dict: 包含课程表信息的字典
        """
        try:
            # 验证并格式化日期
            formatted_date = ClassTableService.validate_and_format_date(date)
            if not formatted_date:
                return {
                    "success": False,
                    "message": f"无效的日期格式: {date}，请使用 YYYY-MM-DD 格式",
                    "data": {},
                }

            logger.info(f"正在获取日期 {formatted_date} 的课程表数据")

            # 课程表接口URL
            url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/main_index_loadkb.jsp"

            # 请求头设置
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Accept": "text/html, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "http://zhjw.qfnu.edu.cn",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain_new.jsp?t1=1",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            }

            # 请求数据
            data = {"rq": formatted_date}  # 日期参数，格式：YYYY-MM-DD

            # 发送POST请求
            response = session.post(
                url=url,
                headers=headers,
                data=data,
                timeout=30,  # 30秒超时
                allow_redirects=True,
            )

            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"请求失败，状态码: {response.status_code}")
                return {
                    "success": False,
                    "message": f"请求失败，状态码: {response.status_code}",
                    "data": {},
                }

            # 检查响应内容
            html_content = response.text
            if not html_content or "table" not in html_content:
                logger.warning("响应内容为空或不包含课程表数据")
                return {
                    "success": False,
                    "message": "未获取到有效的课程表数据",
                    "data": {},
                }

            logger.info("成功获取课程表HTML内容，开始解析...")

            # 调用解析函数
            result = ClassTableService.parse_class_table_html(html_content)

            if result["success"]:
                logger.info(
                    f"课程表数据获取成功，共{result['data']['stats']['total_courses']}门课程"
                )
            else:
                logger.error(f"课程表数据解析失败: {result['message']}")

            return result

        except requests.exceptions.Timeout:
            logger.error("请求超时")
            return {"success": False, "message": "请求超时，请稍后重试", "data": {}}

        except requests.exceptions.ConnectionError:
            logger.error("网络连接错误")
            return {
                "success": False,
                "message": "网络连接失败，请检查网络连接",
                "data": {},
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return {"success": False, "message": f"网络请求失败: {str(e)}", "data": {}}

        except Exception as e:
            logger.error(f"获取课程表数据时出错: {str(e)}")
            return {"success": False, "message": f"获取失败: {str(e)}", "data": {}}

    @staticmethod
    def get_current_week_class_table(session: requests.Session) -> Dict[str, Any]:
        """
        获取当前周的课程表数据

        Args:
            session: 已登录的请求会话

        Returns:
            Dict: 课程表数据
        """
        from datetime import datetime

        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        return ClassTableService.get_class_table_data(session, current_date)
