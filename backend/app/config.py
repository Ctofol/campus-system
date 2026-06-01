import os

# 基础配置
SECRET_KEY = os.getenv("SECRET_KEY", "mvp_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 60  # 2个月

# 业务密钥
CAPTCHA_SECRET = os.getenv("CAPTCHA_SECRET", "lingxi_sports_mvp_secret_salt_2026")

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
FACE_PROVIDER = os.getenv("FACE_PROVIDER", "none")  # none | tencent | local
FACE_INSIGHTFACE_MODEL = os.getenv("FACE_INSIGHTFACE_MODEL", "buffalo_l")
FACE_INSIGHTFACE_PROVIDERS = os.getenv("FACE_INSIGHTFACE_PROVIDERS", "CPUExecutionProvider")
# 本地 1:1 余弦相似度阈值（0~1），常见 0.38~0.55，可按内测调整
FACE_LOCAL_MIN_SIMILARITY = float(os.getenv("FACE_LOCAL_MIN_SIMILARITY", "0.42"))
TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID", "")
TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY", "")
TENCENT_REGION = os.getenv("TENCENT_REGION", "ap-guangzhou")
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "70"))
FACE_VERIFY_TIMEOUT_SEC = int(os.getenv("FACE_VERIFY_TIMEOUT_SEC", "8"))
FACE_BLOCK_ON_FAIL = os.getenv("FACE_BLOCK_ON_FAIL", "true").lower() in ("1", "true", "yes")

# 体测视频分析
TEST_ANALYSIS_USE_BACKGROUND = os.getenv("TEST_ANALYSIS_USE_BACKGROUND", "true").lower() in (
    "1",
    "true",
    "yes",
)
TEST_DEFAULT_MIN_COUNT = int(os.getenv("TEST_DEFAULT_MIN_COUNT", "10"))
TEST_EXERCISE_MIN_COUNT = {
    "pull_up": int(os.getenv("TEST_MIN_COUNT_PULL_UP", "10")),
    "sit_up": int(os.getenv("TEST_MIN_COUNT_SIT_UP", "10")),
    "push_up": int(os.getenv("TEST_MIN_COUNT_PUSH_UP", "10")),
}
