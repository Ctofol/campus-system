from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """仅集中解析环境配置；业务常量继续保留在模块级，保持现有兼容性。"""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    secret_key: SecretStr = SecretStr("mvp_secret_key_change_me")
    access_token_expire_minutes: int = 60 * 24 * 60
    captcha_secret: SecretStr = SecretStr("lingxi_sports_mvp_secret_salt_2026")
    initial_account_password: SecretStr = SecretStr("123456")

    face_provider: Literal["none", "tencent", "local"] = "none"
    face_insightface_model: str = "buffalo_l"
    face_insightface_providers: str = "CPUExecutionProvider"
    face_local_min_similarity: float = 0.55
    face_local_min_face_ratio: float = 0.035
    face_local_min_brightness: float = 45
    face_local_min_sharpness: float = 35
    tencent_secret_id: SecretStr = SecretStr("")
    tencent_secret_key: SecretStr = SecretStr("")
    tencent_region: str = "ap-guangzhou"

    tencent_map_key: SecretStr = SecretStr("")
    tencent_map_api_base: str = "https://apis.map.qq.com"
    weather_cache_ttl_sec: int = 1800
    face_match_threshold: float = 70
    face_verify_timeout_sec: int = 8
    face_block_on_fail: bool = True

    test_analysis_use_background: bool = True
    test_default_min_count: int = 10
    test_min_count_pull_up: int = 10
    test_min_count_sit_up: int = 10
    test_min_count_push_up: int = 10


settings = Settings()


def validate_runtime_config(
    *,
    strict: bool = False,
    candidate: Settings | None = None,
) -> list[str]:
    """返回配置风险；strict=True 时用于部署前阻止不安全配置。"""

    current = candidate or settings
    issues: list[str] = []
    if current.secret_key.get_secret_value() == "mvp_secret_key_change_me":
        issues.append("SECRET_KEY 仍为开发默认值")
    if current.captcha_secret.get_secret_value() == "lingxi_sports_mvp_secret_salt_2026":
        issues.append("CAPTCHA_SECRET 仍为开发默认值")
    if current.face_provider == "tencent" and not (
        current.tencent_secret_id.get_secret_value()
        and current.tencent_secret_key.get_secret_value()
    ):
        issues.append("FACE_PROVIDER=tencent 时必须设置腾讯云密钥")

    if strict and issues:
        raise ValueError("; ".join(issues))
    return issues

# 基础配置
APP_ENV = settings.app_env
SECRET_KEY = settings.secret_key.get_secret_value()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# 业务密钥
CAPTCHA_SECRET = settings.captcha_secret.get_secret_value()
INITIAL_ACCOUNT_PASSWORD = settings.initial_account_password.get_secret_value()

# 登录保护：连续失败达到阈值后短暂锁定，成功登录会立即清除记录。
LOGIN_MAX_FAILURES = 8
LOGIN_LOCK_SECONDS = 15 * 60

# 阳光跑打卡及计分配置
CHECKPOINT_RADIUS = 50  # 米
REQUIRED_CHECKPOINTS = 3

# 性别对应最低里程
MIN_DISTANCE_MALE = 2.0  # km
MIN_DISTANCE_FEMALE = 1.2  # km

# 配速区间 (分钟/公里)
MAX_PACE_MIN_KM = 10.0
MIN_PACE_MIN_KM = 3.0

# 阶梯计分阶梯
SCORE_TIER_1_MIN = 11
SCORE_TIER_2_MIN = 20
SCORE_TIER_3_MAX = 40
SCORE_TIER_1_START_VAL = 42
SCORE_TIER_2_START_VAL = 60
SCORE_MAX = 100

# 人脸核验：none=仅双照 | tencent=腾讯云 | local=InsightFace 本地比对
FACE_PROVIDER = settings.face_provider
FACE_INSIGHTFACE_MODEL = settings.face_insightface_model
FACE_INSIGHTFACE_PROVIDERS = settings.face_insightface_providers
# 本地 1:1 余弦相似度阈值（0~1），常见 0.38~0.55，可按内测调整
FACE_LOCAL_MIN_SIMILARITY = settings.face_local_min_similarity
FACE_LOCAL_MIN_FACE_RATIO = settings.face_local_min_face_ratio
FACE_LOCAL_MIN_BRIGHTNESS = settings.face_local_min_brightness
FACE_LOCAL_MIN_SHARPNESS = settings.face_local_min_sharpness
TENCENT_SECRET_ID = settings.tencent_secret_id.get_secret_value()
TENCENT_SECRET_KEY = settings.tencent_secret_key.get_secret_value()
TENCENT_REGION = settings.tencent_region

# 腾讯位置服务 WebService（天气等），Key 仅放服务端
TENCENT_MAP_KEY = settings.tencent_map_key.get_secret_value().strip()
TENCENT_MAP_API_BASE = settings.tencent_map_api_base.rstrip("/")
WEATHER_CACHE_TTL_SEC = settings.weather_cache_ttl_sec
FACE_MATCH_THRESHOLD = settings.face_match_threshold
FACE_VERIFY_TIMEOUT_SEC = settings.face_verify_timeout_sec
FACE_BLOCK_ON_FAIL = settings.face_block_on_fail

# 体测视频分析
TEST_ANALYSIS_USE_BACKGROUND = settings.test_analysis_use_background
TEST_DEFAULT_MIN_COUNT = settings.test_default_min_count
TEST_EXERCISE_MIN_COUNT = {
    "pull_up": settings.test_min_count_pull_up,
    "sit_up": settings.test_min_count_sit_up,
    "push_up": settings.test_min_count_push_up,
}
