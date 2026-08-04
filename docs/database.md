# 数据库演进

## 当前策略

应用仍保留原有 `create_all()` 和 `ensure_schema_upgrades()` 启动行为，避免本轮改变使用方式。新增 Alembic 是兼容迁移通道；验证稳定后再单独评审是否移除启动时 DDL。

```powershell
python -m pip install -r backend/requirements-dev.txt
.\scripts\migrate.ps1
```

迁移 `0001` 对空库创建当前模型，对已有库不重复建表；`0002` 添加查询索引。迁移不会新增可能因历史重复数据而失败的唯一约束。

## 约束审计

当前模型已声明用户手机号、学号、人脸档案、阳光跑班级规则、教师学员关系和用户奖牌等唯一约束。以下候选约束需要先审计生产数据，再单独上线：

- `classes(major_id, name)`
- `teacher_subjects(teacher_id, subject_name)`
- `run_group_members(group_id, user_id)`
- `run_group_activity_applications(activity_id, user_id)`
- `enrollments(student_id, course_id)`
- `course_progress(student_id, content_id)`
- `activity_metrics(activity_id)`
- `activity_review(activity_id)`

这些约束会拒绝现有功能曾允许的重复写入，因此本轮只记录，不直接施加。
