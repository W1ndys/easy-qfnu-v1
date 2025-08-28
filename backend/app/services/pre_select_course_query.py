# app/services/pre_select_course_query.py

import json
import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from requests import Session
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError


class HttpStatusError(Exception):
    def __init__(self, status_code: int, message: str, url: str):
        super().__init__(f"{status_code} {message} [{url}]")
        self.status_code = status_code
        self.message = message
        self.url = url


def get_jx0502zbid_and_name(session: Session) -> Optional[Dict[str, str]]:
    """
    获取教务系统中的选课轮次编号(jx0502zbid)和选课轮次名称(jx0502zbmc)
    返回: {"jx0502zbid": "选课ID", "name": "选课名称"} 或 None
    """
    url = "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list"
    jx0502zbid_pattern = re.compile(r"jx0502zbid=([^&]+)")

    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 查找表格
        table = soup.find("table", {"id": "tbKxkc"})
        if not table:
            logging.warning("未找到选课列表表格")
            return None

        rows = table.find_all("tr")  # type: ignore

        # 收集所有符合条件的候选项
        candidates = []

        # 跳过表头，从第二行开始解析
        for row in rows[1:]:
            try:
                cells = row.find_all("td")  # type: ignore
                if len(cells) >= 4:  # 确保有足够的列
                    # 获取选课名称（第2列，索引1）
                    course_name = cells[1].get_text(strip=True)

                    # 获取操作列中的链接（第4列，索引3）
                    link = cells[3].find("a", href=True)  # type: ignore
                    if link and "jx0502zbid" in link["href"]:  # type: ignore
                        m = jx0502zbid_pattern.search(link["href"])  # type: ignore
                        if m:
                            candidates.append(
                                {"jx0502zbid": m.group(1), "name": course_name}
                            )
            except (AttributeError, IndexError) as e:
                logging.warning(f"解析行数据时出错: {str(e)}")
                continue

        # 如果没有找到任何候选项
        if not candidates:
            return None

        # 优先选择包含"补选"或"选课"的那一行
        for candidate in candidates:
            if "补选" in candidate["name"] or "选课" in candidate["name"]:
                return candidate

        # 如果没有包含"补选"或"选课"的行，返回第一个候选项
        return candidates[0]

    except HTTPError as e:
        status = e.response.status_code if e.response is not None else -1
        logging.error(f"请求选课页面失败: {status} {str(e)}")
        raise HttpStatusError(status, "获取选课轮次失败", url)
    except (Timeout, ConnectionError) as e:
        logging.error(f"请求选课页面超时/连接失败: {str(e)}")
        raise
    except RequestException as e:
        logging.error(f"请求选课页面失败: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"获取选课轮次时发生未知错误: {str(e)}")
        raise


def _safe_get(session: Session, url: str) -> None:
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else -1
        raise HttpStatusError(status, "GET请求失败", url)
    except (Timeout, ConnectionError) as e:
        raise RuntimeError(f"GET请求失败(网络/超时): {url} {str(e)}")


def _post_json(
    session: Session, url: str, params: Dict[str, Any], data: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        r = session.post(url, params=params, data=data, timeout=15)
        if r.status_code == 404:
            # 与用户场景相符：部分接口未开放时可能返回404
            raise HttpStatusError(404, "接口未开放/不存在", url)
        r.raise_for_status()
        try:
            return json.loads(r.text)
        except ValueError:
            raise RuntimeError(f"API返回的数据不是有效的JSON格式: {url}")
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else -1
        raise HttpStatusError(status, "POST请求失败", url)
    except (Timeout, ConnectionError) as e:
        raise RuntimeError(f"POST请求失败(网络/超时): {url} {str(e)}")


def _build_common_params(
    course_id_or_name: Optional[str],
    teacher_name: Optional[str],
    week_day: Optional[str],
    class_period: Optional[str],
) -> Dict[str, Any]:
    return {
        "kcxx": course_id_or_name or "",
        "skls": teacher_name or "",
        "skxq": week_day or "",
        "skjc": class_period or "",
        "sfym": "false",
        "sfct": "false",
        "sfxx": "false",
    }


def _build_common_table_payload(
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    # 固定起始位置与返回条数
    payload = {
        "iDisplayStart": "0",
        "iDisplayLength": "1000",
    }
    if extra:
        payload.update(extra)
    return payload


def _to_int(val: Any) -> Optional[int]:
    try:
        if val is None:
            return None
        if isinstance(val, int):
            return val
        s = str(val).strip()
        if s == "":
            return None
        return int(s)
    except Exception:
        return None


def _parse_course_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    将教务系统返回的一条课程记录解析为前端所需字段
    """
    time_raw = item.get("sksj")
    ctsm_raw = item.get("ctsm") or ""

    parsed: Dict[str, Any] = {
        # 课程编号/课程名/分组名/学分
        "course_id": item.get("kch"),
        "course_name": item.get("kcmc"),
        "group_name": item.get("fzmc") or item.get("ktmc"),
        "credits": _to_int(item.get("xf")),
        # 上课老师/上课时间/上课地点/上课校区
        "teacher_name": item.get("skls"),
        "time_text": time_raw.strip() if isinstance(time_raw, str) else time_raw,
        "location": item.get("skdd"),
        "campus_name": item.get("xqmc"),
        # 剩余量
        "remain_count": _to_int(item.get("syrs")),
        # 时间冲突（根据备注是否包含“冲突”判断）
        "time_conflict": (
            ctsm_raw if (isinstance(ctsm_raw, str) and "冲突" in ctsm_raw) else ""
        ),
    }

    # 其余字段暂不返回：
    # parsed["teacher_id"] = item.get("sklsid")
    # parsed["plan_capacity"] = _to_int(item.get("pkrs"))
    # parsed["selected_count"] = _to_int(item.get("xkrs"))
    # parsed["max_capacity"] = _to_int(item.get("xxrs"))
    # parsed["remark"] = item.get("ctsm")
    # parsed["term_id"] = item.get("xnxq01id")
    # parsed["jxb_id"] = item.get("jx0404id")
    # parsed["jx0504id"] = item.get("jx0504id")
    # parsed["teaching_unit_id"] = item.get("jx02id")
    # parsed["course_property_code"] = item.get("kcsx")
    # parsed["course_property_name"] = item.get("kcxzmc")
    # parsed["course_property_subcode"] = item.get("kcxzm")
    # parsed["operation_html"] = item.get("czOper")
    # parsed["course_intro"] = item.get("kcjj")
    # parsed["teaching_class_name"] = item.get("ktmc")

    # 留作扩展：周次与排课明细（zcxqjcList/kkapList）
    # ...（不解析，以减少返回体体积与处理时延）...

    return parsed


def _query_module(
    session: Session,
    module_key: str,
    course_id_or_name: Optional[str],
    teacher_name: Optional[str],
    week_day: Optional[str],
    class_period: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    针对单个模块发起 comeIn + 查询请求，返回JSON或None
    """
    base = "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc"
    # 各模块配置（URL 与 表格列配置）
    modules = {
        "knjxk": {
            "name": "专业内跨年级选课",
            "come_in": f"{base}/comeInKnjxk",
            "api": f"{base}/xsxkKnjxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(),
        },
        "bxqjhxk": {
            "name": "本学期计划选课",
            "come_in": f"{base}/comeInBxqjhxk",
            "api": f"{base}/xsxkBxqjhxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(),
        },
        "xxxk": {
            "name": "选修选课",
            "come_in": f"{base}/comeInXxxk",
            "api": f"{base}/xsxkXxxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(),
        },
        "ggxxkxk": {
            "name": "公选课选课",
            # 参考用户示例中使用 comeInXxxk 进入，再调用 xsxkGgxxkxk
            "come_in": f"{base}/comeInXxxk",
            "api": f"{base}/xsxkGgxxkxk",
            "params": {
                **_build_common_params(
                    course_id_or_name, teacher_name, week_day, class_period
                ),
                "szjylb": "",
                "sfym": "false",
                "sfct": "true",
                "sfxx": "true",
            },
            "data": _build_common_table_payload(),
        },
        "fawxk": {
            "name": "计划外选课",
            "come_in": f"{base}/comeInFawxk",
            "api": f"{base}/xsxkFawxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(),
        },
    }

    cfg = modules[module_key]
    _safe_get(session, cfg["come_in"])
    data = _post_json(session, cfg["api"], cfg["params"], cfg["data"])
    if not data or not data.get("aaData"):
        logging.info(f"{cfg['name']} 未查询到数据")
        return None

    courses = [
        _parse_course_item(x) for x in data.get("aaData", []) if isinstance(x, dict)
    ]

    return {
        "module": module_key,
        "module_name": cfg["name"],
        "count": len(courses),
        "courses": courses,
    }


def pre_select_course_query(
    session: Session,  # 改为显式接收 session（从 API 的依赖注入传入）
    course_id_or_name: Optional[str],
    teacher_name: Optional[str] = None,
    week_day: Optional[str] = None,
    class_period: Optional[str] = None,
) -> Dict[str, Any]:
    """
    预选课查询：按模块依次查询，返回各模块结果

    Args:
        session: 已登录的教务系统Session（由依赖注入提供）
        course_id_or_name: 课程名称或课程ID(可选)
        teacher_name: 教师姓名(可选)
        week_day: 上课星期(可选)
        class_period: 上课节次(可选)
    """
    # 1) 获取选课轮次编号和名称
    jx0502zbid_and_name = get_jx0502zbid_and_name(session)
    if not jx0502zbid_and_name:
        raise RuntimeError("未获取到有效的选课轮次编号，可能是当前未开放任何轮次的选课")

    # 2) 刷新选课上下文session
    _safe_get(
        session,
        f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={jx0502zbid_and_name['jx0502zbid']}",
    )

    # 3) 依次查询模块
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    ordered = ["knjxk", "bxqjhxk", "xxxk", "ggxxkxk", "fawxk"]
    for key in ordered:
        try:
            r = _query_module(
                session, key, course_id_or_name, teacher_name, week_day, class_period
            )
            if r:
                results.append(r)
        except HttpStatusError as he:
            logging.warning(f"模块[{key}]查询失败: {he.status_code} {he.message}")
            errors.append(
                {"module": key, "status": he.status_code, "message": he.message}
            )
            continue
        except Exception as e:
            logging.error(f"模块[{key}]查询异常: {str(e)}")
            errors.append({"module": key, "status": -1, "message": str(e)})
            continue

    return {
        "select_course_round_id": jx0502zbid_and_name["jx0502zbid"],
        "select_course_round_name": jx0502zbid_and_name["name"],
        "modules": results,
        "errors": errors,
    }
