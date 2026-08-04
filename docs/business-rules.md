# 核心业务规则索引

本文只记录规则位置，不修改现有业务定义。

| 业务 | 当前主要实现 |
| --- | --- |
| 阳光跑距离、配速和阶梯计分 | `backend/app/config.py`、`backend/app/services/score_service.py` |
| 活动与跑步记录 | `backend/app/routers/activity.py`、`student.py`、`teacher.py` |
| 体测视频分析 | `backend/app/services/test_analysis_service.py`、`pose_analyzer/` |
| 人脸建档与核验 | `backend/app/services/face_profile_service.py`、`face_verify_service.py` |
| 课程 | `backend/app/routers/courses.py` |
| 跑团 | `backend/app/routers/run_groups.py` |

任何规则调整都应同时更新本文件、对应测试和 API 文档。涉及计分、达标或身份核验阈值的变更，需要记录变更日期、旧值、新值和适用范围。
