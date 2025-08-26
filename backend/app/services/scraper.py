# app/services/scraper.py
import requests
import base64
import ddddocr
from bs4 import BeautifulSoup
import re
from typing import Optional, List
from loguru import logger

# 伪造一个浏览器头，让请求看起来更像真实用户
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

# 假设这是你学校教务系统的登录URL
LOGIN_URL = "http://zhjw.qfnu.edu.cn/jsxsd/xk/LoginToXkLdap"
VERIFYCODE_URL = "http://zhjw.qfnu.edu.cn/jsxsd/verifycode.servlet"


def get_random_code(session):
    """使用指定的session获取验证码，确保cookie一致性"""
    try:
        logger.debug("正在获取验证码...")
        response = session.get(VERIFYCODE_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"获取验证码失败，状态码: {response.status_code}")
            return None

        if len(response.content) < 100:
            logger.warning("获取的验证码数据异常，可能不是有效的图片")
            return None

        logger.debug("正在识别验证码...")
        ocr = ddddocr.DdddOcr(show_ad=False)
        code = ocr.classification(response.content)

        if code and len(code) >= 3:
            logger.info(f"验证码识别成功: {code}")
            return code
        else:
            logger.warning(f"验证码格式异常: {code}")
            return None

    except Exception as e:
        logger.error(f"获取验证码时出错: {e}")
        return None


def login_to_university(student_id: str, password: str, max_retries: int = 3):
    """
    尝试登录到学校教务系统。
    成功返回 session 对象，失败返回 None。
    """
    logger.info(f"开始登录流程，学号: {student_id}")

    encoded_student_id = base64.b64encode(student_id.encode()).decode()
    encoded_password = base64.b64encode(password.encode()).decode()
    encoded = f"{encoded_student_id}%%%{encoded_password}"
    logger.debug("学号和密码编码完成")

    for attempt in range(max_retries):
        logger.info(f"第 {attempt + 1} 次登录尝试...")

        try:
            session = requests.Session()
            logger.debug("创建新的session对象")

            random_code = get_random_code(session)

            if random_code is None:
                logger.warning(f"第 {attempt + 1} 次尝试：获取验证码失败，准备重试...")
                session.close()
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("获取验证码失败次数已达上限")
                    return None

            form_data = {
                "RANDOMCODE": random_code,
                "encoded": encoded,
            }

            logger.debug(
                f"登录数据准备完成: RANDOMCODE={random_code}, encoded={encoded[:20]}..."
            )
            logger.info("正在发送登录请求...")
            response = session.post(
                LOGIN_URL, headers=HEADERS, data=form_data, timeout=10
            )
            logger.info(f"登录响应状态码: {response.status_code}")

            if "密码错误" in response.text or "用户名或密码错误" in response.text:
                logger.error("登录失败：用户名或密码错误")
                session.close()
                return None

            if "验证码错误" in response.text or "验证码不正确" in response.text:
                logger.warning(f"第 {attempt + 1} 次尝试：验证码错误，准备重试...")
                session.close()
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("验证码重试次数已用完")
                    return None

            logger.debug("正在验证登录状态...")
            main_page_url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp"
            main_page_resp = session.get(main_page_url, headers=HEADERS, timeout=10)

            if (
                "教学一体化服务平台" in main_page_resp.text
                or "学生个人中心" in main_page_resp.text
            ):
                logger.info("登录成功！")
                return session

            logger.warning(f"登录响应内容片段: {response.text[:200]}...")
            logger.warning("登录失败：可能是验证码识别错误或其他未知原因")
            session.close()
            if attempt < max_retries - 1:
                logger.info("准备重试...")
                continue

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求出错: {e}")
            if "session" in locals():
                session.close()
            if attempt < max_retries - 1:
                logger.info("网络错误，准备重试...")
                continue
            else:
                return None

    logger.error(f"登录失败：已尝试 {max_retries} 次")
    return None


def get_grades(session: requests.Session, semester: str = ""):
    """
    获取当前登录用户的成绩，并提供精简、准确的GPA分析。

    返回结构已重构，以满足以下需求：
    - basic_gpa: 包含所有课程计算的加权平均绩点。
    - effective_gpa: 去除重修/补考，只取课程最高绩点记录后计算的加权平均绩点。
    - yearly_gpa: 基于 effective_gpa 的规则，按学年统计的绩点。
    - semester_gpa: 基于 effective_gpa 的规则，按学期统计的绩点。
    - data: 原始的完整成绩列表。
    """
    logger.info(f"开始获取成绩数据，学期: {semester if semester else '全部学期'}")
    try:
        grades_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"
        post_data = {"kksj": semester, "kcxz": "", "kcmc": "", "xsfs": "all"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query",
            **HEADERS,
        }

        response = session.post(grades_url, headers=headers, data=post_data, timeout=10)
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"请求失败，状态码: {response.status_code}",
            }

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "dataList"})
        if not table:
            return {"success": False, "message": "未找到成绩表格，可能登录已过期"}

        header_map = {
            "序号": "index",
            "开课学期": "semester",
            "课程编号": "courseCode",
            "课程名称": "courseName",
            "分组名": "groupName",
            "成绩": "score",
            "成绩标识": "scoreTag",
            "学分": "credit",
            "总学时": "totalHours",
            "绩点": "gpa",
            "补重学期": "retakeSemester",
            "考核方式": "assessmentMethod",
            "考试性质": "examType",
            "课程属性": "courseAttribute",
            "课程性质": "courseNature",
            "课程类别": "courseCategory",
        }
        actual_headers = [
            th.get_text(strip=True) for th in table.find("tr").find_all("th")
        ]

        grades_data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < len(actual_headers):
                continue
            grade_item = {
                header_map.get(actual_headers[i]): cell.get_text(strip=True)
                for i, cell in enumerate(cells)
                if header_map.get(actual_headers[i])
            }
            if grade_item:
                grades_data.append(grade_item)

        logger.info(f"成功解析 {len(grades_data)} 条原始成绩记录")

        # --- GPA 计算逻辑重构 ---

        # 1. 计算基础GPA (所有课程)
        basic_gpa_result = _calculate_total_gpa(grades_data)
        basic_gpa_result.pop("courses", None)  # 移除课程详情

        # 2. 获取有效成绩列表 (处理重修/补考，取最高分)
        effective_grades_list = _process_retakes(grades_data)
        logger.info(f"处理重修/补考后，共 {len(effective_grades_list)} 条有效成绩记录")

        # 3. 计算有效GPA
        effective_gpa_result = _calculate_total_gpa(effective_grades_list)
        effective_gpa_result.pop("courses", None)

        # 4. 基于有效成绩，计算学年和学期GPA (核心BUG修复)
        detailed_gpa = _calculate_detailed_gpa(effective_grades_list)

        # 清理学年和学期GPA分析中的课程列表
        for year_gpa in detailed_gpa["yearly_gpa"].values():
            year_gpa.pop("courses", None)
        for sem_gpa in detailed_gpa["semester_gpa"].values():
            sem_gpa.pop("courses", None)

        logger.info("GPA分析完成，构建最终响应")
        return {
            "success": True,
            "message": f"成功获取{len(grades_data)}条原始成绩记录",
            "data": grades_data,
            "basic_gpa": basic_gpa_result,
            "effective_gpa": effective_gpa_result,
            "yearly_gpa": detailed_gpa["yearly_gpa"],
            "semester_gpa": detailed_gpa["semester_gpa"],
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求出错: {e}")
        return {"success": False, "message": f"网络请求出错: {e}"}
    except Exception as e:
        logger.error(f"解析成绩数据时出错: {e}")
        return {"success": False, "message": f"解析成绩数据时出错: {e}"}


def get_available_semesters(session: requests.Session):
    """
    获取可用的学期列表。
    """
    try:
        logger.info("开始获取可用学期列表...")
        query_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query"
        logger.debug(f"学期查询URL: {query_url}")

        headers = {
            **HEADERS,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        }

        response = session.get(query_url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"获取学期列表失败，状态码: {response.status_code}")
            return {
                "success": False,
                "message": f"获取学期列表失败，状态码: {response.status_code}",
                "data": [],
            }

        logger.debug("学期查询请求成功，开始解析HTML")
        soup = BeautifulSoup(response.text, "html.parser")
        semester_select = soup.find("select", {"id": "kksj"}) or soup.find(
            "select", {"name": "kksj"}
        )

        if not semester_select:
            logger.warning("未找到学期选择下拉框")
            return {"success": False, "message": "未找到学期选择下拉框", "data": []}

        semesters = [
            str(option.get("value")).strip()
            for option in semester_select.find_all("option")
            if option.get("value") and str(option.get("value")).strip()
        ]

        logger.info(f"成功获取 {len(semesters)} 个学期: {semesters}")
        return {
            "success": True,
            "message": f"成功获取{len(semesters)}个学期",
            "data": semesters,
        }

    except Exception as e:
        logger.error(f"获取学期列表时出错: {e}")
        return {"success": False, "message": f"获取学期列表时出错: {e}", "data": []}


def calculate_gpa_advanced(
    grades_data: list,
    include_indices: Optional[List[int]] = None,
    remove_retakes: bool = False,
):
    """
    高级GPA计算功能，支持多种计算模式。
    """
    try:
        logger.info(
            f"开始高级GPA计算，数据量: {len(grades_data)}, 选中课程: {include_indices}, 去重修: {remove_retakes}"
        )

        if include_indices is None:
            include_indices = []

        original_data = grades_data.copy()

        filtered_data = [
            item
            for item in grades_data
            if not include_indices
            or item.get("index", "") in [str(idx) for idx in include_indices]
        ]
        logger.debug(f"过滤后数据量: {len(filtered_data)}")

        if remove_retakes:
            logger.debug("启用去重修模式...")
            filtered_data = _process_retakes(filtered_data)
            logger.debug(f"去重修后数据量: {len(filtered_data)}")

        logger.debug("开始计算总体GPA...")
        total_gpa = _calculate_total_gpa(filtered_data, include_indices, original_data)

        logger.debug("开始计算详细GPA分析...")
        detailed_gpa = _calculate_detailed_gpa(
            filtered_data, remove_retakes=remove_retakes
        )

        logger.info("高级GPA计算完成")
        return {
            "success": True,
            "total_gpa": total_gpa,
            "yearly_gpa": detailed_gpa["yearly_gpa"],
            "semester_gpa": detailed_gpa["semester_gpa"],
            "message": "GPA计算完成",
        }

    except Exception as e:
        logger.error(f"计算GPA时出错: {e}")
        return {"success": False, "message": f"计算GPA时出错: {e}"}


def _process_retakes(grades_data: list):
    """
    处理重修/补考记录，对相同的课程，只保留绩点最高的一条。
    判断标准：课程代码 (courseCode) 和 课程名称 (courseName) 均相同。
    """
    logger.debug("开始处理重修/补考记录，保留最高绩点...")

    course_groups = {}
    for grade_item in grades_data:
        key = (grade_item.get("courseCode"), grade_item.get("courseName"))
        if key not in course_groups:
            course_groups[key] = []
        course_groups[key].append(grade_item)

    processed_list = []
    for key, records in course_groups.items():
        if len(records) == 1:
            processed_list.append(records[0])
        else:
            best_record = max(records, key=lambda x: float(x.get("gpa", "0.0")))
            processed_list.append(best_record)
            logger.debug(
                f"课程 '{key[1]}' 有 {len(records)} 条记录，已选择最高绩点: {best_record.get('gpa')}"
            )

    return processed_list


def _calculate_detailed_gpa(grades_data: list, remove_retakes: bool = False):
    """
    计算详细的GPA分析，包括按学年、学期分组。
    """
    logger.debug("开始计算详细GPA分析...")
    yearly_data, semester_data = {}, {}

    for item in grades_data:
        semester = item.get("semester", "")
        if not semester:
            continue
        try:
            year = "-".join(semester.split("-")[:2])
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(item)
            if semester not in semester_data:
                semester_data[semester] = []
            semester_data[semester].append(item)
        except:
            continue

    yearly_gpa = {
        year: _calculate_total_gpa(grades, remove_retakes=remove_retakes)
        for year, grades in yearly_data.items()
    }
    semester_gpa = {
        semester: _calculate_total_gpa(grades, remove_retakes=remove_retakes)
        for semester, grades in semester_data.items()
    }

    logger.debug("详细GPA分析计算完成")
    return {
        "yearly_gpa": yearly_gpa,
        "semester_gpa": semester_gpa,
    }


def _calculate_total_gpa(
    grades_data: list,
    include_indices: Optional[List[int]] = None,
    original_data: Optional[list] = None,
    remove_retakes: bool = False,
):
    """
    计算总体加权GPA。
    """
    logger.debug(f"开始计算总体GPA，数据量: {len(grades_data)}")
    total_credit, total_grade_point, course_count = 0.0, 0.0, 0
    valid_courses = []

    data_source = original_data if original_data is not None else grades_data
    selected_indices_str = [str(idx) for idx in (include_indices or [])]

    for grade_item in data_source:
        is_included = (
            not selected_indices_str
            or grade_item.get("index", "") in selected_indices_str
        )

        try:
            credit = float(grade_item.get("credit", "0") or "0")
            grade_point = float(grade_item.get("gpa", "0") or "0")

            course_info = {
                "index": grade_item.get("index", ""),
                "course_name": grade_item.get("courseName", ""),
                "credit": credit,
                "grade_point": grade_point,
                "score": grade_item.get("score", ""),
                "is_excluded": not is_included,
            }
            valid_courses.append(course_info)

            # 仅当课程在计算范围内（即在 filtered_data 中）时，才累加绩点
            if grade_item in grades_data and credit > 0 and grade_point >= 0:
                total_credit += credit
                total_grade_point += credit * grade_point
                course_count += 1
        except (ValueError, TypeError):
            logger.warning(f"跳过无效数据: {grade_item}")
            continue

    weighted_gpa = (total_grade_point / total_credit) if total_credit > 0 else 0.0
    return {
        "weighted_gpa": round(weighted_gpa, 3),
        "total_credit": round(total_credit, 1),
        "course_count": course_count,
        "courses": valid_courses,
    }


def calculate_gpa(grades_data: list):
    """
    简单GPA计算（保持向后兼容）。
    """
    logger.info("开始简单GPA计算...")
    result = calculate_gpa_advanced(grades_data)
    if result.get("success"):
        total_gpa = result.get("total_gpa", {})
        logger.info(f"简单GPA计算完成: GPA={total_gpa.get('weighted_gpa', 0.0)}")
        return {"success": True, "gpa": total_gpa.get("weighted_gpa", 0.0)}
    else:
        logger.error(f"简单GPA计算失败: {result.get('message')}")
        return {"success": False, "gpa": 0.0, "message": result.get("message")}
