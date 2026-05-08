"""
智能反馈解析与自愈建议（翊晨运动 / SmartRec）。

路径与日志位置一律由环境变量或运行时目录解析，禁止写死服务器绝对路径。
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class FeedbackCategory(str, Enum):
    NETWORK = "Network"
    PATH = "Path"
    PERMISSION = "Permission"
    LOGIC = "Logic"


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


AI_DIAGNOSIS_SYSTEM_PROMPT = """你是翊晨运动(SmartRec)后台的反馈分类器。仅根据用户反馈原文输出**一行合法 JSON**，不要 Markdown，不要解释。

JSON 字段（必须齐全）：
- "category": 只能是 "Network" | "Path" | "Permission" | "Logic"
  - Network: 超时、连不上、DNS、TLS、CORS、connection refused、网关不可达等
  - Path: 404、路由错误、接口路径写错、静态资源找不到
  - Permission: 401/403、未登录、token 失效、角色无权
  - Logic: 业务规则、数据校验、状态机、非 HTTP 路径类逻辑问题
- "severity": "P0"|"P1"|"P2"|"P3"
  - P0 全线不可用或数据损坏风险
  - P1 核心功能大面积不可用
  - P2 局部功能或部分用户
  - P3 轻微体验或可绕过
- "diagnosis": 字符串，1～3 句中文技术推断
- "suggested_action": 字符串，可执行的排查/修复方向（勿编造具体内网 IP）

若信息不足，category 偏保守选 Logic，severity 不超过 P2，diagnosis 中说明需补充日志/接口名。"""


def _audit_log_path() -> str:
    explicit = os.environ.get("FEEDBACK_AUDIT_LOG")
    if explicit:
        return explicit
    base = os.environ.get("FEEDBACK_LOG_DIR", os.getcwd())
    return os.path.join(base, "feedback_audit.log")


def _path_healer_hint() -> str:
    """自愈脚本路径仅通过环境变量告知调用方，默认文案不绑定机器路径。"""
    script = os.environ.get("PATH_HEALER_SCRIPT", "")
    if script:
        return f'bash "{script}"'
    return (
        'export PATH_HEALER_SCRIPT="<仓库内 Skill_3.3_Path_Healer.sh 的绝对路径>"; '
        'bash "$PATH_HEALER_SCRIPT"'
    )


def _heal_mapper(category: FeedbackCategory, diagnosis: str) -> str:
    """自愈联动：根据分类追加标准化操作建议（仍无硬编码主机路径）。"""
    d = diagnosis.lower()
    if category == FeedbackCategory.PATH or "404" in d or "not found" in d:
        return (
            f"路径/404 类：建议在服务器上执行 Path 自愈脚本（需先设置 PATH_HEALER_SCRIPT）：{_path_healer_hint()}。"
            " 脚本内将使用 NGINX_CONF、UPSTREAM_CHECK_URL 等环境变量（见脚本头部说明）。"
        )
    if category == FeedbackCategory.NETWORK:
        return (
            "网络类：检查应用监听与防火墙；"
            "ss -lntp（或等价命令）核对端口；"
            "核对 Nginx upstream 与后端地址是否由环境变量注入；"
            "必要时 systemctl restart \"${NGINX_SERVICE_NAME:-nginx}\"（服务名以实际为准）。"
        )
    if category == FeedbackCategory.PERMISSION:
        return (
            "权限类：核对 Authorization 头、token 过期策略与角色；"
            "查看网关与 FastAPI 依赖注入的鉴权顺序；勿在日志中打印完整 token。"
        )
    return "逻辑类：在后端对应路由与服务层加结构化日志与请求 ID，复现后缩小到单测或最小复现请求。"


def _heuristic_classify(feedback: str) -> dict[str, Any]:
    t = feedback.strip()
    low = t.lower()

    if any(
        k in low
        for k in (
            "404",
            "not found",
            "路径",
            "路由",
            "接口不存在",
            "no route",
            "wrong url",
        )
    ):
        cat = FeedbackCategory.PATH
        sev = Severity.P2
    elif any(
        k in low
        for k in (
            "network",
            "网络",
            "timeout",
            "超时",
            "connection refused",
            "econnrefused",
            "cors",
            "failed to fetch",
            "网关",
        )
    ):
        cat = FeedbackCategory.NETWORK
        sev = Severity.P2
    elif any(
        k in low
        for k in (
            "401",
            "403",
            "权限",
            "无权限",
            "未登录",
            "token",
            "forbidden",
            "unauthorized",
        )
    ):
        cat = FeedbackCategory.PERMISSION
        sev = Severity.P2
    else:
        cat = FeedbackCategory.LOGIC
        sev = Severity.P3

    if any(x in low for x in ("500", "internal server", "全线", "全部不能用", "宕机")):
        sev = Severity.P1
    if any(x in low for x in ("数据丢失", "删库", "p0", "紧急")):
        sev = Severity.P0

    diagnosis = {
        FeedbackCategory.PATH: "疑似前端请求路径、反向代理 location 或 OpenAPI 路由不一致。",
        FeedbackCategory.NETWORK: "疑似链路、端口、TLS 或浏览器侧网络策略导致请求未到达业务代码。",
        FeedbackCategory.PERMISSION: "疑似鉴权失败或角色策略与资源不匹配。",
        FeedbackCategory.LOGIC: "疑似业务规则、校验或数据状态导致与预期不符。",
    }[cat]

    base_action = "收集：请求方法、完整路径、响应码、服务端对应时间点日志（脱敏）。"
    heal = _heal_mapper(cat, t)
    return {
        "original_feedback": t,
        "category": cat.value,
        "severity": sev.value,
        "diagnosis": diagnosis,
        "suggested_action": f"{base_action} {heal}",
    }


def _parse_llm_json(content: str) -> Optional[dict[str, Any]]:
    content = content.strip()
    m = re.search(r"\{[\s\S]*\}", content)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return None


def _llm_diagnose(feedback: str) -> Optional[dict[str, Any]]:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("FEEDBACK_LLM_API_KEY")
    if not api_key:
        return None
    base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("FEEDBACK_LLM_MODEL", "gpt-4o-mini")
    url = f"{base}/chat/completions"
    body = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": AI_DIAGNOSIS_SYSTEM_PROMPT},
            {"role": "user", "content": feedback},
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        text = raw["choices"][0]["message"]["content"]
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return None

    parsed = _parse_llm_json(text)
    if not parsed:
        return None
    for key in ("category", "severity", "diagnosis", "suggested_action"):
        if key not in parsed:
            return None
    cat = parsed["category"]
    if cat not in {c.value for c in FeedbackCategory}:
        return None
    if parsed["severity"] not in {s.value for s in Severity}:
        return None
    parsed["original_feedback"] = feedback.strip()
    heal_extra = _heal_mapper(FeedbackCategory(cat), str(parsed.get("diagnosis", "")))
    parsed["suggested_action"] = f"{parsed['suggested_action']} | Heal-Map: {heal_extra}"
    return parsed


def append_feedback_audit(record: dict[str, Any]) -> str:
    """追加一行 JSON 到审计日志，返回实际写入路径。"""
    path = _audit_log_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    line = {
        **record,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return path


def diagnose_feedback(feedback: str, prefer_llm: bool = True) -> dict[str, Any]:
    """
    返回标准字段：original_feedback, category, severity, diagnosis, suggested_action。
    优先 LLM（若配置了密钥），否则启发式；LLM 失败时回退启发式。
    """
    feedback = (feedback or "").strip()
    if not feedback:
        out = {
            "original_feedback": "",
            "category": FeedbackCategory.LOGIC.value,
            "severity": Severity.P3.value,
            "diagnosis": "空反馈，无法分类。",
            "suggested_action": "请用户提供具体操作步骤、接口与报错原文。",
        }
        append_feedback_audit(out)
        return out

    out: Optional[dict[str, Any]] = None
    if prefer_llm:
        out = _llm_diagnose(feedback)
    if out is None:
        out = _heuristic_classify(feedback)
    else:
        # 确保 Heal-Map 与分类一致（LLM 已拼过 Heal-Map，此处仅保证字段完整）
        pass

    append_feedback_audit(out)
    return out
