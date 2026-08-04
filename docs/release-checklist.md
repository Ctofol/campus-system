# 上线验收清单

## 发布前

- [ ] 在服务器执行 `python backend/scripts/preflight.py`。
- [ ] 执行数据库迁移 `python -m alembic -c backend/alembic.ini upgrade head`。
- [ ] 完成数据库和 `uploads/` 备份，并验证恢复流程。
- [ ] 确认 `APP_ENV=production`，且密钥不是默认值。
- [ ] 审核人脸、体测视频和位置数据的告知说明。
- [ ] 确认管理员、教师和学生的测试账号可用。
- [ ] 确认统一初始密码已通过 `INITIAL_ACCOUNT_PASSWORD` 配置，并完成一次“建号 → 首次设置 → 重新登录”验收。

## 发布后

- [ ] 访问 `/system/health`，数据库与存储状态正常。
- [ ] 用真实 Android/iOS 设备验证登录、定位、上传和人脸认证。
- [ ] 管理端检查操作记录是否写入。
- [ ] 确认公开注册返回禁止提示，新增与重置账号均显示“待首次完善”。
- [ ] 运行 `python backend/scripts/report_upload_usage.py`，记录首次文件占用。
- [ ] 观察登录、上传、AI 分析失败情况。

## 回滚原则

- 先停止新版本流量，再恢复对应日期的数据库与上传文件。
- 代码回滚和数据库回滚必须一起评估，不能只回退代码。
- 记录回滚时间、原因、影响用户和后续修复计划。
