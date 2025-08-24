# app/services/course_plan_service.py
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any
from loguru import logger
import json
from app.db import database as db


class CoursePlanService:
    """培养方案服务类"""

    @staticmethod
    def get_course_plan_data(
        session: requests.Session, student_id: str
    ) -> Dict[str, Any]:
        """
        获取培养方案数据，优先从缓存读取

        Args:
            session: 已登录的教务系统session
            student_id: 学号

        Returns:
            dict: 包含培养方案数据的字典

        Raises:
            Exception: 当获取或解析失败时抛出异常
        """
        logger.info(f"开始获取学号 {student_id} 的培养方案...")

        # 1. 尝试从缓存获取
        cached_plan = db.get_course_plan(student_id)
        if cached_plan:
            logger.info(f"成功从缓存中获取到学号 {student_id} 的培养方案。")
            return {
                "success": True,
                "message": "从缓存加载培养方案成功",
                "data": json.loads(cached_plan["plan_content"]),
                "updated_at": cached_plan["updated_at"].isoformat(),
                "source": "cache",
            }

        logger.info(f"缓存未命中，从教务系统实时获取学号 {student_id} 的培养方案。")
        # 2. 缓存未命中，从网络获取
        try:
            url = "http://zhjw.qfnu.edu.cn/jsxsd/pyfa/topyfamx"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            }

            resp = session.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                logger.error(f"培养方案页面获取失败，状态码: {resp.status_code}")
                raise Exception(f"页面获取失败，状态码: {resp.status_code}")

            logger.debug("培养方案页面获取成功，开始解析...")
            data_dict = CoursePlanService._extract_course_plan_from_html(resp.text)

            if "error" in data_dict:
                logger.warning(f"解析失败: {data_dict['error']}")
                raise Exception(data_dict["error"])

            # 3. 保存到缓存
            try:
                plan_content_json = json.dumps(data_dict, ensure_ascii=False)
                db.save_course_plan(student_id, plan_content_json)
                logger.info(f"已将学号 {student_id} 的新培养方案存入缓存。")
            except Exception as e:
                logger.error(f"培养方案存入缓存失败: {e}")
                # 缓存失败不应影响主流程，仅记录日志

            total_modules = len(data_dict.get("modules", []))
            total_courses = sum(
                len(m.get("courses", [])) for m in data_dict.get("modules", [])
            )
            logger.info(
                f"培养方案解析完成: 模块数={total_modules}, 课程数={total_courses}"
            )

            return {
                "success": True,
                "message": f"成功解析{total_modules}个模块，共{total_courses}门课程",
                "data": data_dict,
                "source": "live",
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取培养方案时发生错误: {e}")
            raise

    @staticmethod
    def _extract_course_plan_from_html(html_content: str) -> Dict[str, Any]:
        """
        从培养方案HTML内容中提取课程设置总表并转换为结构化字典

        Args:
            html_content: HTML内容字符串

        Returns:
            dict: 结构化的培养方案数据
            {
              "modules": [ ... ],
              "incomplete_modules": [ ... ],
              "module_course_counts": [ ... ]
            }
        """
        logger.debug("开始解析培养方案HTML内容...")

        soup = BeautifulSoup(html_content, "html.parser")

        table = soup.find("table", {"id": "dataList"})
        if not table:
            return {"error": "未找到课程表格，可能是教务session过期，请重新登录"}

        modules = []
        current_module = None

        rows = table.find_all("tr")  # type: ignore
        for row in rows:
            cells = row.find_all(["td", "th"])  # type: ignore

            if len(cells) > 0:
                first_cell = cells[0]
                first_cell_text = first_cell.get_text().strip()

                if (
                    first_cell.get("rowspan")  # type: ignore
                    and "(" in first_cell_text
                    and ("应修" in first_cell_text or "已修" in first_cell_text)
                ):
                    module_match = re.match(
                        r"(.+?)\s*\(应修\s*(\d+\.?\d*)\s*/\s*已修\s*(\d+\.?\d*)\)",
                        first_cell_text,
                    )

                    if module_match:
                        module_name = module_match.group(1)
                        required_credits = float(module_match.group(2))
                        completed_credits = float(module_match.group(3))

                        current_module = {
                            "module_name": module_name,
                            "required_credits": required_credits,
                            "completed_credits": completed_credits,
                            "courses": [],
                            "subtotal": None,
                        }
                        modules.append(current_module)

            if len(cells) >= 12 and current_module is not None:
                if cells[0].get_text().strip() == "小计":

                    def clean_text(text: str) -> str:
                        return re.sub(r"&nbsp;|\s+", " ", text).strip()

                    subtotal_info = {
                        "total_credits": clean_text(cells[1].get_text()),
                        "hours": {
                            "lecture": clean_text(cells[2].get_text()),
                            "practice": clean_text(cells[3].get_text()),
                            "seminar": clean_text(cells[4].get_text()),
                            "experiment": clean_text(cells[5].get_text()),
                            "design": clean_text(cells[6].get_text()),
                            "computer": clean_text(cells[7].get_text()),
                            "discussion": clean_text(cells[8].get_text()),
                            "extracurricular": clean_text(cells[9].get_text()),
                            "online": clean_text(cells[10].get_text()),
                            "total": clean_text(cells[11].get_text()),
                        },
                    }

                    current_module["subtotal"] = subtotal_info
                    continue

            if len(cells) >= 12 and current_module is not None:
                first_text = cells[0].get_text().strip() if len(cells) > 0 else ""
                has_module_cell = cells[0].get("rowspan") is not None and (  # type: ignore
                    "应修" in first_text or "已修" in first_text
                )

                base_index = 2 if has_module_cell else 1

                course_code = (
                    re.sub(r"&nbsp;", "", cells[base_index].get_text().strip())
                    if len(cells) > base_index
                    else ""
                )
                course_name = (
                    re.sub(r"&nbsp;", "", cells[base_index + 1].get_text().strip())
                    if len(cells) > base_index + 1
                    else ""
                )

                if (
                    course_code
                    and course_name
                    and course_name != "小计"
                    and cells[0].get_text().strip() != "小计"
                    and len(course_code) >= 3
                    and re.match(r"^[A-Za-z0-9]", course_code)
                ):
                    completion_status = (
                        cells[base_index + 2].get_text().strip()
                        if len(cells) > base_index + 2
                        else ""
                    )
                    course_nature = (
                        cells[base_index + 3].get_text().strip()
                        if len(cells) > base_index + 3
                        else ""
                    )
                    course_attribute = (
                        cells[base_index + 4].get_text().strip()
                        if len(cells) > base_index + 4
                        else ""
                    )
                    credits = (
                        cells[base_index + 5].get_text().strip()
                        if len(cells) > base_index + 5
                        else ""
                    )

                    lecture_hours = (
                        cells[base_index + 6].get_text().strip()
                        if len(cells) > base_index + 6
                        else "0"
                    )
                    practice_hours = (
                        cells[base_index + 7].get_text().strip()
                        if len(cells) > base_index + 7
                        else "0"
                    )
                    seminar_hours = (
                        cells[base_index + 8].get_text().strip()
                        if len(cells) > base_index + 8
                        else "0"
                    )
                    experiment_hours = (
                        cells[base_index + 9].get_text().strip()
                        if len(cells) > base_index + 9
                        else "0"
                    )
                    design_hours = (
                        cells[base_index + 10].get_text().strip()
                        if len(cells) > base_index + 10
                        else "0"
                    )
                    computer_hours = (
                        cells[base_index + 11].get_text().strip()
                        if len(cells) > base_index + 11
                        else "0"
                    )
                    discussion_hours = (
                        cells[base_index + 12].get_text().strip()
                        if len(cells) > base_index + 12
                        else "0"
                    )
                    extracurricular_hours = (
                        cells[base_index + 13].get_text().strip()
                        if len(cells) > base_index + 13
                        else "0"
                    )
                    online_hours = (
                        cells[base_index + 14].get_text().strip()
                        if len(cells) > base_index + 14
                        else "0"
                    )
                    total_hours = (
                        cells[base_index + 15].get_text().strip()
                        if len(cells) > base_index + 15
                        else "0"
                    )
                    semester = (
                        cells[base_index + 16].get_text().strip()
                        if len(cells) > base_index + 16
                        else ""
                    )

                    def clean_text(text: str) -> str:
                        return re.sub(r"&nbsp;|\s+", " ", text).strip()

                    course = {
                        "course_code": clean_text(course_code),
                        "course_name": clean_text(course_name),
                        "completion_status": (
                            clean_text(completion_status)
                            if completion_status
                            else "未修"
                        ),
                        "course_nature": clean_text(course_nature),
                        "course_attribute": clean_text(course_attribute),
                        "credits": clean_text(credits),
                        "hours": {
                            "lecture": clean_text(lecture_hours),
                            "practice": clean_text(practice_hours),
                            "seminar": clean_text(seminar_hours),
                            "experiment": clean_text(experiment_hours),
                            "design": clean_text(design_hours),
                            "computer": clean_text(computer_hours),
                            "discussion": clean_text(discussion_hours),
                            "extracurricular": clean_text(extracurricular_hours),
                            "online": clean_text(online_hours),
                            "total": clean_text(total_hours),
                        },
                        "semester": clean_text(semester),
                    }

                    current_module["courses"].append(course)

        # 计算未完成模块
        incomplete_modules = []
        for module in modules:
            required = float(module.get("required_credits", 0))
            completed = float(module.get("completed_credits", 0))
            shortage = round(required - completed, 2)
            if shortage > 0:
                incomplete_modules.append(
                    {
                        "module_name": module.get("module_name", ""),
                        "required_credits": required,
                        "completed_credits": completed,
                        "shortage_credits": shortage,
                    }
                )

        # 计算模块课程数量
        module_course_counts = [
            {
                "module_name": module.get("module_name", ""),
                "course_count": len(module.get("courses", [])),
            }
            for module in modules
        ]

        logger.debug(f"解析完成，共{len(modules)}个模块")

        result = {
            "modules": modules,
            "incomplete_modules": incomplete_modules,
            "module_course_counts": module_course_counts,
        }
        return result
