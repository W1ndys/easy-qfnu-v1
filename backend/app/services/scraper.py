# scraper.py
import requests
import base64
import ddddocr
from bs4 import BeautifulSoup
import re
from typing import Optional, List

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
        response = session.get(VERIFYCODE_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"获取验证码失败，状态码: {response.status_code}")
            return None

        # 检查是否获取到了图片数据
        if len(response.content) < 100:  # 验证码图片通常不会这么小
            print("获取的验证码数据异常，可能不是有效的图片")
            return None

        ocr = ddddocr.DdddOcr(show_ad=False)
        code = ocr.classification(response.content)

        # 简单的验证码格式验证（通常是4位数字或字母）
        if code and len(code) >= 3:
            print(f"识别的验证码: {code}")
            return code
        else:
            print(f"识别的验证码格式异常: {code}")
            return None

    except Exception as e:
        print(f"获取验证码时出错: {e}")
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
    print(f"正在尝试使用学号 {student_id} 登录...")

    # 分别对学号和密码进行base64编码后用%%%拼接（只需要编码一次）
    encoded_student_id = base64.b64encode(student_id.encode()).decode()
    encoded_password = base64.b64encode(password.encode()).decode()
    encoded = f"{encoded_student_id}%%%{encoded_password}"

    for attempt in range(max_retries):
        print(f"第 {attempt + 1} 次尝试...")

        try:
            # 创建一个新的session对象
            session = requests.Session()

            # 先获取验证码，确保在同一个session中
            print("正在获取验证码...")
            random_code = get_random_code(session)

            if random_code is None:
                print(f"第 {attempt + 1} 次尝试：获取验证码失败，准备重试...")
                session.close()  # 关闭失败的session
                if attempt < max_retries - 1:
                    continue
                else:
                    print("获取验证码失败次数已达上限。")
                    return None

            form_data = {
                "RANDOMCODE": random_code,
                "encoded": encoded,
            }

            print(f"登录数据: RANDOMCODE={random_code}, encoded={encoded[:20]}...")

            response = session.post(
                LOGIN_URL, headers=HEADERS, data=form_data, timeout=10
            )

            print(f"登录响应状态码: {response.status_code}")

            # 检查常见的失败提示
            if "密码错误" in response.text or "用户名或密码错误" in response.text:
                print("登录失败：用户名或密码错误。")
                session.close()  # 关闭失败的session
                return None

            if "验证码错误" in response.text or "验证码不正确" in response.text:
                print(f"第 {attempt + 1} 次尝试：验证码错误，准备重试...")
                session.close()  # 关闭失败的session
                if attempt < max_retries - 1:
                    continue
                else:
                    print("验证码重试次数已用完。")
                    return None

            # 登录后，访问主页判断是否登录成功
            main_page_url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp"
            main_page_resp = session.get(main_page_url, headers=HEADERS, timeout=10)

            if (
                "教学一体化服务平台" in main_page_resp.text
                or "学生个人中心" in main_page_resp.text
            ):
                print("登录成功！")
                return session  # 返回成功登录的session对象

            # 如果没有明确的错误信息，可能是其他问题
            print(f"登录响应内容片段: {response.text[:200]}...")
            print("登录失败：可能是验证码识别错误或其他未知原因。")

            session.close()  # 关闭失败的session
            if attempt < max_retries - 1:
                print("准备重试...")
                continue

        except requests.exceptions.RequestException as e:
            print(f"网络请求出错: {e}")
            if "session" in locals():
                session.close()  # 关闭session
            if attempt < max_retries - 1:
                print("网络错误，准备重试...")
                continue
            else:
                return None

    print(f"登录失败：已尝试 {max_retries} 次。")
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
    print(f"正在获取学期 {semester if semester else '全部学期'} 的成绩...")

    try:
        # 新版接口：POST请求获取成绩
        grades_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"

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

        response = session.post(grades_url, headers=headers, data=post_data, timeout=10)

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"请求失败，状态码: {response.status_code}",
                "data": [],
            }

        # 解析HTML响应
        soup = BeautifulSoup(response.text, "html.parser")

        # 查找成绩表格
        table = soup.find("table", {"id": "dataList"})
        if not table:
            return {"success": False, "message": "未找到成绩表格", "data": []}

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
            return {"success": False, "message": "未找到表格头部", "data": []}

        actual_headers = [th.get_text(strip=True) for th in headers_row.find_all("th")]  # type: ignore

        grades_data = []
        data_rows = table.find_all("tr")[1:]  # type: ignore

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

        print(f"成功获取 {len(grades_data)} 条成绩记录")

        # 1. 分别计算两种模式下的GPA
        basic_gpa_result = calculate_gpa_advanced(grades_data, remove_retakes=False)
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
        print(f"网络请求出错: {e}")
        return {"success": False, "message": f"网络请求出错: {e}", "data": []}
    except Exception as e:
        print(f"解析成绩数据时出错: {e}")
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
        # 访问成绩查询页面，获取可用学期
        query_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_query"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
        }

        response = session.get(query_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"获取学期列表失败，状态码: {response.status_code}",
                "data": [],
            }

        # 解析HTML以获取学期选项
        soup = BeautifulSoup(response.text, "html.parser")

        # 查找学期选择下拉框
        semester_select = soup.find("select", {"id": "kksj"}) or soup.find(
            "select", {"name": "kksj"}
        )

        if not semester_select:
            # 如果没有找到下拉框，返回默认学期
            current_year = "2025"
            return {
                "success": True,
                "message": "使用默认学期列表",
                "data": [
                    f"{current_year}-{int(current_year)+1}-1",  # 第一学期
                    f"{current_year}-{int(current_year)+1}-2",  # 第二学期
                ],
            }

        semesters = []
        for option in semester_select.find_all("option"):  # type: ignore
            value = option.get("value")  # type: ignore
            if value and str(value).strip():
                semesters.append(str(value).strip())

        return {
            "success": True,
            "message": f"成功获取{len(semesters)}个学期",
            "data": semesters,
        }

    except Exception as e:
        print(f"获取学期列表时出错: {e}")
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
        if exclude_indices is None:
            exclude_indices = []

        # 过滤数据
        filtered_data = []
        for grade_item in grades_data:
            # 排除指定序号的课程
            sequence = grade_item.get("序号", "")
            if sequence and str(sequence) in [str(idx) for idx in exclude_indices]:
                continue
            filtered_data.append(grade_item)

        # 处理重修补考（如果启用）
        if remove_retakes:
            filtered_data = _process_retakes(filtered_data)

        # 计算总体GPA
        total_gpa = _calculate_total_gpa(filtered_data)

        # 计算详细的GPA分析（按学年、学期）
        detailed_gpa = _calculate_detailed_gpa(filtered_data)

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
    # 按课程名称分组
    course_groups = {}
    for grade_item in grades_data:
        course_name = grade_item.get("courseName", "")
        course_code = grade_item.get("courseCode", "")
        key = f"{course_code}_{course_name}"

        if key not in course_groups:
            course_groups[key] = []
        course_groups[key].append(grade_item)

    # 对每个课程组，保留绩点最高的记录
    processed_data = []
    for course_list in course_groups.values():
        if len(course_list) == 1:
            processed_data.append(course_list[0])
        else:
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

            processed_data.append(best_record)

    return processed_data


def _calculate_detailed_gpa(grades_data: list):
    """
    计算详细的GPA分析，包括按学年、学期分组。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: 详细的GPA分析数据
    """
    yearly_data = {}
    semester_data = {}

    for grade_item in grades_data:
        semester = grade_item.get("semester", "")
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

    # 计算各维度GPA
    yearly_gpa = {}
    for year, year_grades in yearly_data.items():
        gpa_result = _calculate_total_gpa(year_grades)
        yearly_gpa[year] = gpa_result

    semester_gpa = {}
    for semester, semester_grades in semester_data.items():
        gpa_result = _calculate_total_gpa(semester_grades)
        semester_gpa[semester] = gpa_result

    return {
        "yearly_gpa": yearly_gpa,
        "semester_gpa": semester_gpa,
        "available_years": sorted(yearly_data.keys()),
        "available_semesters": sorted(semester_data.keys()),
    }


def _calculate_total_gpa(grades_data: list):
    """
    计算总体加权GPA。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: GPA计算结果
    """
    total_credit = 0.0
    total_grade_point = 0.0
    course_count = 0
    valid_courses = []

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

            if credit > 0 and grade_point >= 0:  # 绩点可以为0
                total_credit += credit
                total_grade_point += credit * grade_point
                course_count += 1
                valid_courses.append(
                    {
                        "course_name": grade_item.get("courseName", ""),
                        "credit": credit,
                        "grade_point": grade_point,
                        "semester": grade_item.get("semester", ""),
                    }
                )

        except ValueError:
            continue

    if total_credit > 0:
        weighted_gpa = total_grade_point / total_credit
        return {
            "weighted_gpa": round(weighted_gpa, 3),
            "total_credit": round(total_credit, 1),
            "course_count": course_count,
            "courses": valid_courses,
        }
    else:
        return {
            "weighted_gpa": 0.0,
            "total_credit": 0.0,
            "course_count": 0,
            "courses": [],
        }


def calculate_gpa(grades_data: list):
    """
    简单GPA计算（保持向后兼容）。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: 包含GPA计算结果的字典
    """
    result = calculate_gpa_advanced(grades_data)
    if result["success"]:
        total_gpa = result["total_gpa"]
        return {
            "success": True,
            "gpa": total_gpa.get("weighted_gpa", 0.0),
            "total_credit": total_gpa.get("total_credit", 0.0),
            "course_count": total_gpa.get("course_count", 0),
            "message": f"计算完成：总学分{total_gpa.get('total_credit', 0)}，课程数{total_gpa.get('course_count', 0)}",
        }
    else:
        return {
            "success": False,
            "gpa": 0.0,
            "total_credit": 0.0,
            "course_count": 0,
            "message": result["message"],
        }
