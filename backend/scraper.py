# scraper.py
import requests
import base64
import ddddocr

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
