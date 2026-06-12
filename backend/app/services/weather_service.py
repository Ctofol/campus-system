"""腾讯位置服务 · 实时天气（服务端代理，Key 不暴露给前端）。"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

from .. import config

_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _aqi_to_label(aqi: Any) -> str:
    try:
        n = int(aqi)
    except (TypeError, ValueError):
        return ""
    if n <= 0:
        return ""
    if n <= 50:
        return "空气优"
    if n <= 100:
        return "空气良"
    if n <= 150:
        return "轻度污染"
    if n <= 200:
        return "中度污染"
    if n <= 300:
        return "重度污染"
    return "严重污染"


def _cache_key(lat: float, lng: float) -> str:
    return f"{round(lat, 3)},{round(lng, 3)}"


def _parse_tencent_body(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not body or body.get("status") != 0:
        return None
    row = (body.get("result") or {}).get("realtime")
    if not row or not isinstance(row, list):
        return None
    first = row[0] if row else None
    infos = (first or {}).get("infos") or {}
    weather = infos.get("weather") or "—"
    try:
        temp = int(round(float(infos.get("temperature"))))
    except (TypeError, ValueError):
        temp = 0
    air = (first or {}).get("air") or {}
    humidity = infos.get("humidity")
    try:
        humidity = int(round(float(humidity))) if humidity is not None else None
    except (TypeError, ValueError):
        humidity = None
    return {
        "temp": temp,
        "condition": str(weather),
        "aqi_label": _aqi_to_label(air.get("aqi")),
        "humidity": humidity,
        "icon": "default",
    }


def get_realtime_weather(lat: float, lng: float) -> Dict[str, Any]:
    """
    按经纬度查询实时天气。
    返回 { ok, weather?, error?, message? }
    """
    if not config.TENCENT_MAP_KEY:
        return {"ok": False, "error": "no_key", "message": "未配置 TENCENT_MAP_KEY"}

    key = _cache_key(lat, lng)
    now = time.time()
    cached = _cache.get(key)
    if cached and now - cached[0] < config.WEATHER_CACHE_TTL_SEC:
        return {"ok": True, "weather": cached[1], "from_cache": True}

    params = urllib.parse.urlencode(
        {
            "key": config.TENCENT_MAP_KEY,
            "location": f"{lat},{lng}",
            "type": "now",
            "added_fields": "air",
            "output": "json",
        }
    )
    url = f"{config.TENCENT_MAP_API_BASE}/ws/weather/v1/?{params}"

    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
        body = json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": "upstream_http", "message": str(e.reason)}
    except urllib.error.URLError as e:
        return {"ok": False, "error": "upstream_network", "message": str(e.reason)}
    except (json.JSONDecodeError, TimeoutError, OSError) as e:
        return {"ok": False, "error": "upstream_parse", "message": str(e)}

    weather = _parse_tencent_body(body)
    if not weather:
        msg = body.get("message") if isinstance(body, dict) else "parse_failed"
        return {
            "ok": False,
            "error": "upstream_status",
            "message": msg,
            "status": body.get("status") if isinstance(body, dict) else None,
        }

    _cache[key] = (now, weather)
    return {"ok": True, "weather": weather, "from_cache": False}
