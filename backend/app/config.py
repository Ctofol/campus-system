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
