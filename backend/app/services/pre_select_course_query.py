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


def get_jx0502zbid(session: Session, select_semester: Optional[str]) -> Optional[str]:
    """
    获取教务系统中的选课轮次编号(jx0502zbid)
    """
    url = "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list"
    jx0502zbid_pattern = re.compile(r"jx0502zbid=([^&]+)")

    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.find_all("tr")

        if not select_semester:
            for row in rows[1:]:
                try:
                    link = row.find("a", href=True)
                    if link and "jx0502zbid" in link["href"]:
                        m = jx0502zbid_pattern.search(link["href"])
                        if m:
                            return m.group(1)
                except (AttributeError, IndexError) as e:
                    logging.warning(f"解析行数据时出错: {str(e)}")
                    continue
            return None

        first_valid_id = None
        for row in rows[1:]:
            try:
                cells = row.find_all("td")
                if not cells or len(cells) < 2:
                    continue
                link = row.find("a", href=True)
                if link and "jx0502zbid" in link["href"]:
                    m = jx0502zbid_pattern.search(link["href"])
                    if m:
                        if first_valid_id is None:
                            first_valid_id = m.group(1)
                        if select_semester in cells[1].text.strip():
                            return m.group(1)
            except (AttributeError, IndexError) as e:
                logging.warning(f"解析行数据时出错: {str(e)}")
                continue
        return first_valid_id
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
    course_id_or_name: str,
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
    cols: int, extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    payload = {
        "sEcho": "1",
        "iColumns": str(cols),
        "sColumns": "",
        "iDisplayStart": "0",
        "iDisplayLength": "15",
    }
    # 复用最常见的列表字段映射
    base = {
        12: {
            "mDataProp_0": "kch",
            "mDataProp_1": "kcmc",
            "mDataProp_2": "fzmc",
            "mDataProp_3": "xf",
            "mDataProp_4": "skls",
            "mDataProp_5": "sksj",
            "mDataProp_6": "skdd",
            "mDataProp_7": "xqmc",
            "mDataProp_8": "xkrs",
            "mDataProp_9": "syrs",
            "mDataProp_10": "ctsm",
            "mDataProp_11": "czOper",
        },
        13: {
            "mDataProp_0": "kch",
            "mDataProp_1": "kcmc",
            "mDataProp_2": "xf",
            "mDataProp_3": "skls",
            "mDataProp_4": "sksj",
            "mDataProp_5": "skdd",
            "mDataProp_6": "xqmc",
            "mDataProp_7": "xxrs",
            "mDataProp_8": "xkrs",
            "mDataProp_9": "syrs",
            "mDataProp_10": "ctsm",
            "mDataProp_11": "szkcflmc",
            "mDataProp_12": "czOper",
        },
    }
    payload.update(base.get(cols, {}))
    if extra:
        payload.update(extra)
    return payload


def _query_module(
    session: Session,
    module_key: str,
    course_id_or_name: str,
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
            "data": _build_common_table_payload(12),
        },
        "bxqjhxk": {
            "name": "本学期计划选课",
            "come_in": f"{base}/comeInBxqjhxk",
            "api": f"{base}/xsxkBxqjhxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(12),
        },
        "xxxk": {
            "name": "选修选课",
            "come_in": f"{base}/comeInXxxk",
            "api": f"{base}/xsxkXxxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(12),
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
            "data": _build_common_table_payload(13),
        },
        "fawxk": {
            "name": "计划外选课",
            "come_in": f"{base}/comeInFawxk",
            "api": f"{base}/xsxkFawxk",
            "params": _build_common_params(
                course_id_or_name, teacher_name, week_day, class_period
            ),
            "data": _build_common_table_payload(12),
        },
    }

    cfg = modules[module_key]
    # 先进入模块，刷新相关上下文
    _safe_get(session, cfg["come_in"])
    # 再发起数据请求
    data = _post_json(session, cfg["api"], cfg["params"], cfg["data"])
    if not data or not data.get("aaData"):
        logging.info(f"{cfg['name']} 未查询到数据")
        return None
    return {
        "module": module_key,
        "module_name": cfg["name"],
        "count": len(data.get("aaData", [])),
        "aaData": data.get("aaData", []),
    }


def pre_select_course_query(
    session: Session,  # 改为显式接收 session（从 API 的依赖注入传入）
    course_id_or_name: str,
    teacher_name: Optional[str] = None,
    week_day: Optional[str] = None,
    class_period: Optional[str] = None,
    select_semester: Optional[str] = None,
) -> Dict[str, Any]:
    """
    预选课查询：按模块依次查询，返回各模块结果

    Args:
        session: 已登录的教务系统Session（由依赖注入提供）
        course_id_or_name: 课程名称或课程ID(必填)
        teacher_name: 教师姓名(可选)
        week_day: 上课星期(可选)
        class_period: 上课节次(可选)
        select_semester: 选课学期(可选)

    Returns:
        dict: {
            "jx0502zbid": str,
            "modules": [ { "module": str, "module_name": str, "count": int, "aaData": list } ],
            "errors": [ { "module": str, "status": int, "message": str } ]
        }
    """
    # 1) 获取选课轮次编号
    jx0502zbid = get_jx0502zbid(session, select_semester)
    if not jx0502zbid:
        raise RuntimeError("未获取到有效的选课轮次编号(jx0502zbid)")

    # 2) 刷新选课上下文session
    _safe_get(
        session,
        f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={jx0502zbid}",
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
        "jx0502zbid": jx0502zbid,
        "modules": results,
        "errors": errors,
    }
