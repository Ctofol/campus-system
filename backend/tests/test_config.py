import pytest
from pydantic import ValidationError

from app.config import Settings, validate_runtime_config


def test_settings_keep_existing_development_defaults(monkeypatch):
    for name in (
        "APP_ENV",
        "SECRET_KEY",
        "CAPTCHA_SECRET",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "FACE_PROVIDER",
    ):
        monkeypatch.delenv(name, raising=False)

    candidate = Settings(_env_file=None)

    assert candidate.app_env == "development"
    assert candidate.access_token_expire_minutes == 60 * 24 * 60
    assert candidate.face_provider == "none"


def test_production_validation_rejects_default_secrets():
    candidate = Settings(app_env="production", _env_file=None)

    with pytest.raises(ValueError, match="SECRET_KEY"):
        validate_runtime_config(strict=True, candidate=candidate)


def test_face_provider_is_typed():
    with pytest.raises(ValidationError):
        Settings(face_provider="unsupported", _env_file=None)
