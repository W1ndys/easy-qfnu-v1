# app/services/profile.py
import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger
from typing import Optional
from app.schemas.profile import StudentProfile


class ProfileService:
    """个人信息服务类"""

    @staticmethod
    def get_student_profile(session: requests.Session) -> dict:
        """
        获取学生个人信息

        Args:
            session: 已登录的requests.Session对象

        Returns:
            dict: 包含个人信息的字典
        """
        logger.info("开始获取学生个人信息...")

        try:
            # 访问个人信息页面
            profile_url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain_new.jsp"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp",
            }

            logger.debug(f"请求个人信息页面: {profile_url}")
            response = session.get(profile_url, headers=headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"获取个人信息失败，状态码: {response.status_code}")
                return {
                    "success": False,
                    "message": f"获取个人信息失败，状态码: {response.status_code}",
                    "data": None,
                }

            logger.debug("个人信息页面请求成功，开始解析HTML")
            soup = BeautifulSoup(response.text, "html.parser")

            # 检查是否成功登录（查找特定的页面标识）
            if "学生姓名" not in response.text:
                logger.warning("可能未登录或session已失效")
                return {
                    "success": False,
                    "message": "Session已失效，请重新登录",
                    "data": None,
                }

            # 解析个人信息
            profile_data = ProfileService._parse_profile_info(soup)

            if profile_data:
                logger.info(
                    f"成功获取个人信息: {profile_data.student_name} ({profile_data.student_id})"
                )
                return {
                    "success": True,
                    "message": "个人信息获取成功",
                    "data": profile_data,
                }
            else:
                logger.warning("解析个人信息失败")
                return {
                    "success": False,
                    "message": "解析个人信息失败",
                    "data": None,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求出错: {e}")
            return {
                "success": False,
                "message": f"网络请求出错: {e}",
                "data": None,
            }
        except Exception as e:
            logger.error(f"获取个人信息时出错: {e}")
            return {
                "success": False,
                "message": f"获取个人信息时出错: {e}",
                "data": None,
            }

    @staticmethod
    def _parse_profile_info(soup: BeautifulSoup) -> Optional[StudentProfile]:
        """
        解析个人信息HTML

        Args:
            soup: BeautifulSoup对象

        Returns:
            StudentProfile: 解析后的个人信息对象，解析失败时返回None
        """
        try:
            logger.debug("开始解析个人信息HTML...")

            # 查找包含个人信息的容器
            info_container = soup.find("div", class_="middletopttxlr")
            if not info_container or not isinstance(info_container, Tag):
                logger.error("未找到个人信息容器")
                return None

            # 初始化信息字典
            profile_info = {
                "student_name": "",
                "student_id": "",
                "college": "",
                "major": "",
                "class_name": "",
                "photo_url": None,
            }

            # 解析个人信息项
            info_divs = info_container.find_all("div")
            logger.debug(f"找到 {len(info_divs)} 个信息项")

            for div in info_divs:
                if isinstance(div, Tag):
                    text = div.get_text(strip=True)
                    logger.debug(f"处理信息项: {text}")

                    # 解析各个字段
                    if "学生姓名：" in text:
                        profile_info["student_name"] = text.replace(
                            "学生姓名：", ""
                        ).strip()
                    elif "学生编号：" in text:
                        profile_info["student_id"] = text.replace(
                            "学生编号：", ""
                        ).strip()
                    elif "所属院系：" in text:
                        profile_info["college"] = text.replace("所属院系：", "").strip()
                    elif "专业名称：" in text:
                        profile_info["major"] = text.replace("专业名称：", "").strip()
                    elif "班级名称：" in text:
                        profile_info["class_name"] = text.replace(
                            "班级名称：", ""
                        ).strip()

            # 尝试获取头像URL
            try:
                photo_div = soup.find("div", class_="circle-80531 zp")
                if photo_div and isinstance(photo_div, Tag):
                    style = photo_div.get("style")
                    if (
                        style
                        and isinstance(style, str)
                        and "background-image:url(" in style
                    ):
                        # 提取URL
                        url_start = style.find("url(") + 4
                        url_end = style.find(")", url_start)
                        if url_end > url_start:
                            photo_url = style[url_start:url_end]
                            # 如果是相对路径，补充完整域名
                            if photo_url.startswith("/"):
                                photo_url = "http://zhjw.qfnu.edu.cn" + photo_url
                            profile_info["photo_url"] = photo_url
                            logger.debug(f"解析到头像URL: {photo_url}")
            except Exception as e:
                logger.warning(f"解析头像URL失败: {e}")

            # 验证必要信息是否都已获取
            required_fields = [
                "student_name",
                "student_id",
                "college",
                "major",
                "class_name",
            ]
            missing_fields = [
                field for field in required_fields if not profile_info[field]
            ]

            if missing_fields:
                logger.warning(f"缺少必要信息字段: {missing_fields}")
                # 即使缺少某些字段，也尝试返回已获取的信息

            logger.info(f"个人信息解析完成: {profile_info}")

            # 确保photo_url是正确的类型
            photo_url = profile_info["photo_url"]
            if not isinstance(photo_url, str):
                photo_url = None

            # 创建并返回StudentProfile对象
            return StudentProfile(
                student_name=profile_info["student_name"],
                student_id=profile_info["student_id"],
                college=profile_info["college"],
                major=profile_info["major"],
                class_name=profile_info["class_name"],
                photo_url=photo_url,
            )

        except Exception as e:
            logger.error(f"解析个人信息时出错: {e}")
            return None
