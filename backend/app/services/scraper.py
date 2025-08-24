# scraper.py
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

        # 检查是否获取到了图片数据
        if len(response.content) < 100:  # 验证码图片通常不会这么小
            logger.warning("获取的验证码数据异常，可能不是有效的图片")
            return None

        logger.debug("正在识别验证码...")
        ocr = ddddocr.DdddOcr(show_ad=False)
        code = ocr.classification(response.content)

        # 简单的验证码格式验证（通常是4位数字或字母）
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
    请求体只有两个，一个是RANDOMCODE，一个是encoded，是学号和密码分别base64编码之后用%%%拼接
    学号和密码base64编码之后用%%%拼接

    Args:
        student_id: 学号
        password: 密码
        max_retries: 最大重试次数（主要用于验证码识别错误的重试）

    Returns:
        requests.Session: 登录成功时返回已登录的session对象
        None: 登录失败时返回None
    """
    logger.info(f"开始登录流程，学号: {student_id}")

    # 分别对学号和密码进行base64编码后用%%%拼接（只需要编码一次）
    encoded_student_id = base64.b64encode(student_id.encode()).decode()
    encoded_password = base64.b64encode(password.encode()).decode()
    encoded = f"{encoded_student_id}%%%{encoded_password}"
    logger.debug("学号和密码编码完成")

    for attempt in range(max_retries):
        logger.info(f"第 {attempt + 1} 次登录尝试...")

        try:
            # 创建一个新的session对象
            session = requests.Session()
            logger.debug("创建新的session对象")

            # 先获取验证码，确保在同一个session中
            logger.debug("正在获取验证码...")
            random_code = get_random_code(session)

            if random_code is None:
                logger.warning(f"第 {attempt + 1} 次尝试：获取验证码失败，准备重试...")
                session.close()  # 关闭失败的session
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

            # 检查常见的失败提示
            if "密码错误" in response.text or "用户名或密码错误" in response.text:
                logger.error("登录失败：用户名或密码错误")
                session.close()  # 关闭失败的session
                return None

            if "验证码错误" in response.text or "验证码不正确" in response.text:
                logger.warning(f"第 {attempt + 1} 次尝试：验证码错误，准备重试...")
                session.close()  # 关闭失败的session
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("验证码重试次数已用完")
                    return None

            # 登录后，访问主页判断是否登录成功
            logger.debug("正在验证登录状态...")
            main_page_url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp"
            main_page_resp = session.get(main_page_url, headers=HEADERS, timeout=10)

            if (
                "教学一体化服务平台" in main_page_resp.text
                or "学生个人中心" in main_page_resp.text
            ):
                logger.info("登录成功！")
                return session  # 返回成功登录的session对象

            # 如果没有明确的错误信息，可能是其他问题
            logger.warning(f"登录响应内容片段: {response.text[:200]}...")
            logger.warning("登录失败：可能是验证码识别错误或其他未知原因")

            session.close()  # 关闭失败的session
            if attempt < max_retries - 1:
                logger.info("准备重试...")
                continue

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求出错: {e}")
            if "session" in locals():
                session.close()  # 关闭session
            if attempt < max_retries - 1:
                logger.info("网络错误，准备重试...")
                continue
            else:
                return None

    logger.error(f"登录失败：已尝试 {max_retries} 次")
    return None


def get_grades(session: requests.Session, semester: str = ""):
    """
    获取当前登录用户的成绩及GPA分析（新版接口说明）。

    参数:
        session: 已登录的requests.Session对象
        semester: 学期参数，格式如 "2024-2025-2"，空字符串表示获取全部学期

    返回:
        dict: 返回结构如下，包含成绩列表和GPA分析（新版接口结构）：
        {
            "success": bool,           # 是否成功
            "message": str,            # 提示信息
            "data": [                  # 成绩数据列表，每项为一门课程
                {
                    "序号": str,
                    "开课学期": str,
                    "课程编号": str,
                    "课程名称": str,
                    "分组名": str,
                    "成绩": str,
                    "成绩标识": str,
                    "学分": str,
                    "总学时": str,
                    "绩点": str,
                    "补重学期": str,
                    "考核方式": str,
                    "考试性质": str,
                    "课程属性": str,
                    "课程性质": str,
                    "课程类别": str
                }
            ],
            "gpa_analysis": {          # GPA分析结果（新版接口要求嵌套结构）
                "basic_gpa": {...},        # 基础GPA分析
                "no_retakes_gpa": {...}    # 去重修/补考后GPA分析
            },
            "total_courses": int       # 总课程数量
        }
    """
    logger.info(f"开始获取成绩数据，学期: {semester if semester else '全部学期'}")

    try:
        # 新版接口：POST请求获取成绩
        grades_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"
        logger.debug(f"成绩查询URL: {grades_url}")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "max-age=0",
            "Origin": "http://zhjw.qfnu.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
        }

        post_data = {
            "kksj": semester,  # 学期参数，空字符串表示全部学期
            "kcxz": "",  # 课程性质，空表示全部
            "kcmc": "",  # 课程名称，空表示全部
            "xsfs": "all",  # 显示方式，all表示显示全部
        }

        logger.debug(f"发送成绩查询请求，参数: {post_data}")
        response = session.post(grades_url, headers=headers, data=post_data, timeout=10)

        if response.status_code != 200:
            logger.error(f"成绩查询请求失败，状态码: {response.status_code}")
            return {
                "success": False,
                "message": f"请求失败，状态码: {response.status_code}",
                "data": [],
            }

        logger.debug("成绩查询请求成功，开始解析HTML响应")
        # 解析HTML响应
        soup = BeautifulSoup(response.text, "html.parser")

        # 查找成绩表格
        table = soup.find("table", {"id": "dataList"})
        if not table:
            logger.warning("未找到成绩表格")
            return {
                "success": False,
                "message": "未找到成绩表格，可能是登录过期，请手动退出登录重新登录",
                "data": [],
            }

        logger.debug("找到成绩表格，开始解析数据")
        # 我们定义一个中文到英文的映射关系
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

        # 从表头获取实际的列名顺序
        headers_row = table.find("tr")  # type: ignore
        if not headers_row:
            logger.error("未找到表格头部")
            return {"success": False, "message": "未找到表格头部", "data": []}

        actual_headers = [th.get_text(strip=True) for th in headers_row.find_all("th")]  # type: ignore
        logger.debug(f"表格列头: {actual_headers}")

        grades_data = []
        data_rows = table.find_all("tr")[1:]  # type: ignore
        logger.debug(f"找到 {len(data_rows)} 行成绩数据")

        for row in data_rows:
            cells = row.find_all("td")  # type: ignore
            if len(cells) < len(actual_headers):
                continue

            grade_item = {}
            for i, cell in enumerate(cells):
                # 使用英文键名来存储数据
                header_text = actual_headers[i]
                english_key = header_map.get(header_text)
                if english_key:  # 只添加我们定义过的键
                    grade_item[english_key] = cell.get_text(strip=True)

            if grade_item:
                grades_data.append(grade_item)

        logger.info(f"成功解析 {len(grades_data)} 条成绩记录")

        # 1. 分别计算两种模式下的GPA
        logger.debug("开始计算基础GPA...")
        basic_gpa_result = calculate_gpa_advanced(grades_data, remove_retakes=False)
        logger.debug("开始计算去重修GPA...")
        no_retakes_gpa_result = calculate_gpa_advanced(grades_data, remove_retakes=True)

        # 2. 提取 total_gpa 数据，构建符合 Schema 的结构
        basic_gpa_data = basic_gpa_result.get("total_gpa", {})
        no_retakes_gpa_data = no_retakes_gpa_result.get("total_gpa", {})

        # 3. 提取学期和学年GPA数据
        semester_gpa_data = basic_gpa_result.get("semester_gpa", {})
        yearly_gpa_data = basic_gpa_result.get("yearly_gpa", {})

        # 4. 总的有效加权绩点（去除重修补考的结果）
        effective_gpa_data = no_retakes_gpa_data

        # 5. 按照新版API要求的嵌套结构，组装 gpa_analysis 字典
        gpa_analysis_results = {
            "basic_gpa": basic_gpa_data,
            "no_retakes_gpa": no_retakes_gpa_data,
        }

        logger.info("GPA计算完成，准备返回结果")
        # 6. 返回新版接口要求的完整结构
        return {
            "success": True,
            "message": f"成功获取{len(grades_data)}条成绩记录",
            "data": grades_data,
            "gpa_analysis": gpa_analysis_results,
            "semester_gpa": semester_gpa_data,
            "yearly_gpa": yearly_gpa_data,
            "effective_gpa": effective_gpa_data,
            "total_courses": len(grades_data),
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求出错: {e}")
        return {"success": False, "message": f"网络请求出错: {e}", "data": []}
    except Exception as e:
        logger.error(f"解析成绩数据时出错: {e}")
        return {"success": False, "message": f"解析成绩数据时出错: {e}", "data": []}


def get_available_semesters(session: requests.Session):
    """
    获取可用的学期列表。

    Args:
        session: 已登录的requests.Session对象

    Returns:
        dict: 包含可用学期信息的字典
    """
    try:
        logger.info("开始获取可用学期列表...")
        # 访问成绩查询页面，获取可用学期
        query_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query"
        logger.debug(f"学期查询URL: {query_url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
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
        # 解析HTML以获取学期选项
        soup = BeautifulSoup(response.text, "html.parser")

        # 查找学期选择下拉框
        semester_select = soup.find("select", {"id": "kksj"}) or soup.find(
            "select", {"name": "kksj"}
        )

        if not semester_select:
            logger.warning("未找到学期选择下拉框，使用默认学期列表")
            # 如果没有找到下拉框，返回默认学期
            current_year = "2025"
            default_semesters = [
                f"{current_year}-{int(current_year)+1}-1",  # 第一学期
                f"{current_year}-{int(current_year)+1}-2",  # 第二学期
            ]
            logger.info(f"使用默认学期列表: {default_semesters}")
            return {
                "success": True,
                "message": "使用默认学期列表",
                "data": default_semesters,
            }

        semesters = []
        for option in semester_select.find_all("option"):  # type: ignore
            value = option.get("value")  # type: ignore
            if value and str(value).strip():
                semesters.append(str(value).strip())

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
    exclude_indices: Optional[List[int]] = None,
    remove_retakes: bool = False,
):
    """
    高级GPA计算功能，支持多种计算模式。

    Args:
        grades_data: 成绩数据列表
        exclude_indices: 要排除的课程序号列表
        remove_retakes: 是否去除重修补考，取最高绩点

    Returns:
        dict: 包含详细GPA计算结果的字典
    """
    try:
        logger.info(
            f"开始高级GPA计算，数据量: {len(grades_data)}, 排除课程: {exclude_indices}, 去重修: {remove_retakes}"
        )

        if exclude_indices is None:
            exclude_indices = []

        # 保存原始数据用于生成完整课程列表
        original_data = grades_data.copy()

        # 过滤数据
        filtered_data = []
        for grade_item in grades_data:
            # 排除指定序号的课程
            sequence = grade_item.get("index", "")
            if sequence and str(sequence) in [str(idx) for idx in exclude_indices]:
                logger.debug(
                    f"排除课程: {grade_item.get('courseName', 'Unknown')} (序号: {sequence})"
                )
                continue
            filtered_data.append(grade_item)

        logger.debug(f"过滤后数据量: {len(filtered_data)}")

        # 处理重修补考（如果启用）
        if remove_retakes:
            logger.debug("启用去重修模式，开始处理重修补考记录...")
            filtered_data = _process_retakes(filtered_data)
            logger.debug(f"去重修后数据量: {len(filtered_data)}")

        # 计算总体GPA，传入原始数据以生成完整课程列表
        logger.debug("开始计算总体GPA...")
        total_gpa = _calculate_total_gpa(filtered_data, exclude_indices, original_data)

        # 计算详细的GPA分析（按学年、学期）
        logger.debug("开始计算详细GPA分析...")
        detailed_gpa = _calculate_detailed_gpa(filtered_data)

        logger.info("高级GPA计算完成")
        return {
            "success": True,
            "total_gpa": total_gpa,
            "yearly_gpa": detailed_gpa["yearly_gpa"],
            "semester_gpa": detailed_gpa["semester_gpa"],
            "available_years": detailed_gpa["available_years"],
            "available_semesters": detailed_gpa["available_semesters"],
            "excluded_count": len(exclude_indices),
            "retakes_processed": remove_retakes,
            "message": "GPA计算完成",
        }

    except Exception as e:
        logger.error(f"计算GPA时出错: {e}")
        return {
            "success": False,
            "total_gpa": {},
            "yearly_gpa": {},
            "excluded_count": 0,
            "retakes_processed": False,
            "message": f"计算GPA时出错: {e}",
        }


def _process_retakes(grades_data: list):
    """
    处理重修补考，保留最高绩点的成绩。

    Args:
        grades_data: 成绩数据列表

    Returns:
        list: 处理后的成绩数据列表
    """
    logger.debug("开始处理重修补考记录...")
    # 按课程名称分组
    course_groups = {}
    for grade_item in grades_data:
        course_name = grade_item.get("courseName", "")
        course_code = grade_item.get("courseCode", "")
        key = f"{course_code}_{course_name}"

        if key not in course_groups:
            course_groups[key] = []
        course_groups[key].append(grade_item)

    logger.debug(f"找到 {len(course_groups)} 个课程组")

    # 对每个课程组，保留绩点最高的记录
    processed_data = []
    for course_key, course_list in course_groups.items():
        if len(course_list) == 1:
            processed_data.append(course_list[0])
        else:
            logger.debug(
                f"课程 {course_key} 有 {len(course_list)} 条记录，选择最高绩点"
            )
            # 找出绩点最高的记录
            best_record = course_list[0]
            best_gpa = 0.0

            for record in course_list:
                try:
                    gpa = float(record.get("gpa", "0"))
                    if gpa > best_gpa:
                        best_gpa = gpa
                        best_record = record
                except ValueError:
                    continue

            # 为被去除的重修记录添加标记
            for record in course_list:
                if record != best_record:
                    record["exclude_reason"] = "重修/补考记录（已取最高分）"

            processed_data.append(best_record)
            logger.debug(
                f"选择记录: {best_record.get('courseName')} - 绩点: {best_gpa}"
            )

    logger.debug(f"重修补考处理完成，处理后数据量: {len(processed_data)}")
    return processed_data


def _calculate_detailed_gpa(grades_data: list):
    """
    计算详细的GPA分析，包括按学年、学期分组。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: 详细的GPA分析数据
    """
    logger.debug("开始计算详细GPA分析...")
    yearly_data = {}
    semester_data = {}

    for grade_item in grades_data:
        semester = grade_item.get("semester", "")  # 使用英文字段名
        if not semester:
            continue

        # 提取学年 (例如: "2022-2023-1" -> "2022-2023")
        try:
            parts = semester.split("-")
            year = "-".join(parts[:2])
            full_semester = semester  # 完整学期，如 "2022-2023-1"
        except:
            continue

        # 按学年分组
        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(grade_item)

        # 按具体学期分组
        if full_semester not in semester_data:
            semester_data[full_semester] = []
        semester_data[full_semester].append(grade_item)

    logger.debug(f"学年分组: {list(yearly_data.keys())}")
    logger.debug(f"学期分组: {list(semester_data.keys())}")

    # 计算各维度GPA
    yearly_gpa = {}
    for year, year_grades in yearly_data.items():
        logger.debug(f"计算学年 {year} 的GPA，课程数: {len(year_grades)}")
        gpa_result = _calculate_total_gpa(year_grades)
        yearly_gpa[year] = gpa_result

    semester_gpa = {}
    for semester, semester_grades in semester_data.items():
        logger.debug(f"计算学期 {semester} 的GPA，课程数: {len(semester_grades)}")
        gpa_result = _calculate_total_gpa(semester_grades)
        semester_gpa[semester] = gpa_result

    logger.debug("详细GPA分析计算完成")
    return {
        "yearly_gpa": yearly_gpa,
        "semester_gpa": semester_gpa,
        "available_years": sorted(yearly_data.keys()),
        "available_semesters": sorted(semester_data.keys()),
    }


def _calculate_total_gpa(
    grades_data: list,
    exclude_indices: Optional[List[int]] = None,
    original_data: Optional[list] = None,
):
    """
    计算总体加权GPA。

    Args:
        grades_data: 成绩数据列表（已过滤）
        exclude_indices: 排除的课程序号列表
        original_data: 原始成绩数据列表（用于标记排除状态）

    Returns:
        dict: GPA计算结果
    """
    logger.debug(f"开始计算总体GPA，数据量: {len(grades_data)}")

    if exclude_indices is None:
        exclude_indices = []

    total_credit = 0.0
    total_grade_point = 0.0
    course_count = 0
    valid_courses = []

    # 如果有原始数据，生成包含排除状态的完整课程列表
    if original_data:
        excluded_indices_str = [str(idx) for idx in exclude_indices]
        for grade_item in original_data:
            credit_str = grade_item.get("credit", "0")
            grade_point_str = grade_item.get("gpa", "0")
            index_str = grade_item.get("index", "")

            try:
                credit = float(credit_str) if credit_str and credit_str != "" else 0.0
                grade_point = (
                    float(grade_point_str)
                    if grade_point_str and grade_point_str != ""
                    else 0.0
                )

                # 判断是否被排除
                is_excluded = index_str in excluded_indices_str

                course_info = {
                    "index": index_str,
                    "course_name": grade_item.get("courseName", ""),
                    "course_code": grade_item.get("courseCode", ""),
                    "credit": credit,
                    "grade_point": grade_point,
                    "score": grade_item.get("score", ""),
                    "semester": grade_item.get("semester", ""),
                    "is_excluded": is_excluded,
                    "exclude_reason": "用户排除" if is_excluded else None,
                }

                # 如果没有被排除且有效，计入GPA计算
                if not is_excluded and credit > 0 and grade_point >= 0:
                    total_credit += credit
                    total_grade_point += credit * grade_point
                    course_count += 1

                valid_courses.append(course_info)

            except ValueError:
                logger.warning(
                    f"跳过无效数据: credit={credit_str}, gpa={grade_point_str}"
                )
                continue
    else:
        # 原有逻辑，兼容性处理
        for grade_item in grades_data:
            credit_str = grade_item.get("credit", "0")
            grade_point_str = grade_item.get("gpa", "0")

            try:
                credit = float(credit_str) if credit_str and credit_str != "" else 0.0
                grade_point = (
                    float(grade_point_str)
                    if grade_point_str and grade_point_str != ""
                    else 0.0
                )

                if credit > 0 and grade_point >= 0:
                    total_credit += credit
                    total_grade_point += credit * grade_point
                    course_count += 1
                    valid_courses.append(
                        {
                            "index": grade_item.get("index", ""),
                            "course_name": grade_item.get("courseName", ""),
                            "course_code": grade_item.get("courseCode", ""),
                            "credit": credit,
                            "grade_point": grade_point,
                            "score": grade_item.get("score", ""),
                            "semester": grade_item.get("semester", ""),
                            "is_excluded": False,
                            "exclude_reason": None,
                        }
                    )

            except ValueError:
                logger.warning(
                    f"跳过无效数据: credit={credit_str}, gpa={grade_point_str}"
                )
                continue

    if total_credit > 0:
        weighted_gpa = total_grade_point / total_credit
        result = {
            "weighted_gpa": round(weighted_gpa, 3),
            "total_credit": round(total_credit, 1),
            "course_count": course_count,
            "courses": valid_courses,
        }
        logger.debug(
            f"GPA计算完成: 加权GPA={result['weighted_gpa']}, 总学分={result['total_credit']}, 课程数={result['course_count']}"
        )
        return result
    else:
        logger.warning("没有有效的学分数据，返回默认值")
        return {
            "weighted_gpa": 0.0,
            "total_credit": 0.0,
            "course_count": 0,
            "courses": valid_courses if original_data else [],
        }


def calculate_gpa(grades_data: list):
    """
    简单GPA计算（保持向后兼容）。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: 包含GPA计算结果的字典
    """
    logger.info("开始简单GPA计算...")
    result = calculate_gpa_advanced(grades_data)
    if result["success"]:
        total_gpa = result["total_gpa"]
        logger.info(f"简单GPA计算完成: GPA={total_gpa.get('weighted_gpa', 0.0)}")
        return {
            "success": True,
            "gpa": total_gpa.get("weighted_gpa", 0.0),
            "total_credit": total_gpa.get("total_credit", 0.0),
            "course_count": total_gpa.get("course_count", 0),
            "message": f"计算完成：总学分{total_gpa.get('total_credit', 0)}，课程数{total_gpa.get('course_count', 0)}",
        }
    else:
        logger.error(f"简单GPA计算失败: {result['message']}")
        return {
            "success": False,
            "gpa": 0.0,
            "total_credit": 0.0,
            "course_count": 0,
            "message": result["message"],
        }
