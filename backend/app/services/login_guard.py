"""轻量登录失败保护；多实例部署可后续替换为 Redis 实现。"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock

from .. import config


@dataclass
class _FailureState:
    count: int
    locked_until: datetime | None = None


_states: dict[str, _FailureState] = {}
_lock = Lock()


def _key(account: str, client_host: str) -> str:
    return f"{account.casefold()}|{client_host}"


def remaining_lock_seconds(account: str, client_host: str) -> int:
    with _lock:
        state = _states.get(_key(account, client_host))
        if not state or not state.locked_until:
            return 0
        seconds = int((state.locked_until - datetime.now(timezone.utc)).total_seconds())
        return max(seconds, 0)


def record_failure(account: str, client_host: str) -> None:
    with _lock:
        key = _key(account, client_host)
        state = _states.get(key, _FailureState(count=0))
        state.count += 1
        if state.count >= config.LOGIN_MAX_FAILURES:
            state.locked_until = datetime.now(timezone.utc) + timedelta(seconds=config.LOGIN_LOCK_SECONDS)
            state.count = 0
        _states[key] = state


def clear_failures(account: str, client_host: str) -> None:
    with _lock:
        _states.pop(_key(account, client_host), None)
