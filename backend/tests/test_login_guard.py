from app.services import login_guard


def test_login_guard_locks_after_repeated_failures(monkeypatch):
    login_guard._states.clear()
    monkeypatch.setattr(login_guard.config, "LOGIN_MAX_FAILURES", 2)
    login_guard.record_failure("13800138000", "127.0.0.1")
    assert login_guard.remaining_lock_seconds("13800138000", "127.0.0.1") == 0
    login_guard.record_failure("13800138000", "127.0.0.1")
    assert login_guard.remaining_lock_seconds("13800138000", "127.0.0.1") > 0
    login_guard.clear_failures("13800138000", "127.0.0.1")
    assert login_guard.remaining_lock_seconds("13800138000", "127.0.0.1") == 0
