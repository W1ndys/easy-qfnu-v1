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
    获取当前登录用户的成绩。

    Args:
        session: 已登录的requests.Session对象
        semester: 学期参数，格式为 "2024-2025-2"，空字符串表示获取全部学期

    Returns:
        dict: 包含成绩信息的字典，格式为：
        {
            "success": bool,
            "message": str,
            "data": [
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
            ]
        }
    """
    print(f"正在获取学期 {semester if semester else '全部学期'} 的成绩...")

    try:
        # 构建请求URL - 使用POST方法
        grades_url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"

        # 设置请求头
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

        # 构建POST数据
        post_data = {
            "kksj": semester,  # 学期参数，空字符串表示全部学期
            "kcxz": "",  # 课程性质，空表示全部
            "kcmc": "",  # 课程名称，空表示全部
            "xsfs": "all",  # 显示方式，all表示显示全部
        }

        # 发送POST请求获取成绩页面
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

        # 获取表头
        headers_row = table.find("tr")  # type: ignore
        if not headers_row:
            return {"success": False, "message": "未找到表格头部", "data": []}

        # 提取列名
        headers = []
        for th in headers_row.find_all("th"):  # type: ignore
            header_text = th.get_text(strip=True)
            if header_text:  # 只添加非空的列名
                headers.append(header_text)

        print(f"表格列名: {headers}")

        # 获取所有数据行（跳过表头）
        data_rows = table.find_all("tr")[1:]  # type: ignore

        grades_data = []

        for row in data_rows:
            cells = row.find_all("td")  # type: ignore

            # 如果没有td元素，跳过该行
            if not cells:
                continue

            # 检查是否是"未查询到数据"的行
            if len(cells) == 1 and "未查询到数据" in cells[0].get_text(strip=True):
                print("未查询到成绩数据")
                break

            # 如果单元格数量少于预期，可能需要调整解析逻辑
            if len(cells) < len(headers):
                print(
                    f"警告：数据行单元格数量({len(cells)})少于表头数量({len(headers)})"
                )
                # 继续处理，用空字符串填充缺失的单元格

            # 提取每行数据
            row_data = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    cell_text = cells[i].get_text(strip=True)
                    row_data[header] = cell_text
                else:
                    row_data[header] = ""  # 填充空值

            # 只有当行数据包含有效信息时才添加（至少有序号或课程名称）
            if row_data.get("序号") or row_data.get("课程名称"):
                grades_data.append(row_data)

        print(f"成功获取 {len(grades_data)} 条成绩记录")

        # 调试信息：保存响应内容到文件以便分析
        if len(grades_data) == 0:
            print("调试：未获取到成绩数据，保存响应内容用于分析...")
            try:
                with open("debug_response.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("调试：响应内容已保存到 debug_response.html")
            except Exception as debug_e:
                print(f"调试：保存响应内容失败: {debug_e}")

        # 计算各种GPA数据
        gpa_results = {
            "basic_gpa": calculate_gpa_advanced(grades_data),
            "no_retakes_gpa": calculate_gpa_advanced(grades_data, remove_retakes=True),
        }

        return {
            "success": True,
            "message": f"成功获取{len(grades_data)}条成绩记录",
            "data": grades_data,
            "gpa_analysis": gpa_results,
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

        # 按学年分组计算
        yearly_gpa = _calculate_yearly_gpa(filtered_data)

        # 计算总体GPA
        total_gpa = _calculate_total_gpa(filtered_data)

        return {
            "success": True,
            "total_gpa": total_gpa,
            "yearly_gpa": yearly_gpa,
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
        course_name = grade_item.get("课程名称", "")
        course_code = grade_item.get("课程编号", "")
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
                    gpa = float(record.get("绩点", "0"))
                    if gpa > best_gpa:
                        best_gpa = gpa
                        best_record = record
                except ValueError:
                    continue

            processed_data.append(best_record)

    return processed_data


def _calculate_yearly_gpa(grades_data: list):
    """
    按学年计算加权GPA。

    Args:
        grades_data: 成绩数据列表

    Returns:
        dict: 按学年组织的GPA数据
    """
    yearly_data = {}

    for grade_item in grades_data:
        semester = grade_item.get("开课学期", "")
        if not semester:
            continue

        # 提取学年 (例如: "2022-2023-1" -> "2022-2023")
        try:
            year = "-".join(semester.split("-")[:2])
        except:
            continue

        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(grade_item)

    # 为每个学年计算GPA
    yearly_gpa = {}
    for year, year_grades in yearly_data.items():
        gpa_result = _calculate_total_gpa(year_grades)
        yearly_gpa[year] = gpa_result

    return yearly_gpa


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
        credit_str = grade_item.get("学分", "0")
        grade_point_str = grade_item.get("绩点", "0")

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
                        "course_name": grade_item.get("课程名称", ""),
                        "credit": credit,
                        "grade_point": grade_point,
                        "semester": grade_item.get("开课学期", ""),
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
