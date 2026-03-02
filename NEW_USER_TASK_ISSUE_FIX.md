# 新注册用户显示任务问题修复

## 问题描述
新注册的学生账号登录后，会看到一些任务（如"体能测试"、"Teacher Detail Test Task"等），但这些任务不应该显示给新用户。

## 问题原因

### 1. 数据库中存在全局任务
数据库中有5个 `class_id=NULL` 的全局任务：
- Task 2: 两公里跑步
- Task 4: Teacher Detail Test Task
- Task 5: 666
- Task 6: 666
- Task 7: 本周日常3公里跑步

### 2. 原有逻辑问题
原来的学生任务查询逻辑：
```python
if current_user.class_id:
    # 有班级的学生：显示本班任务或全局任务
    query = query.filter(or_(Task.class_id == current_user.class_id, Task.class_id == None))
    if teacher_id:
        query = query.filter(Task.created_by == teacher_id)  # ❌ 这会过滤掉全局任务
else:
    # 没有班级的学生：显示全局任务
    query = query.filter(Task.class_id == None)  # ❌ 新学生会看到所有全局任务
```

问题：
1. 新注册的学生没有班级（`class_id=NULL`）
2. 查询逻辑会返回所有全局任务给没有班级的学生
3. 所以新学生会看到这些测试任务

## 解决方案

### 已实施的修复

修改了 `backend/app/main.py` 中的学生任务查询逻辑：

```python
if current_user.class_id:
    # 有班级的学生
    cls = db.query(Class).filter(Class.id == current_user.class_id).first()
    teacher_id = cls.teacher_id if cls else None
    
    # 显示本班任务或全局任务
    query = query.filter(or_(Task.class_id == current_user.class_id, Task.class_id == None))
    
    # 如果有班主任，只显示班主任创建的本班任务，但保留所有全局任务
    if teacher_id:
        query = query.filter(
            or_(
                Task.created_by == teacher_id,  # 本班老师创建的任务
                Task.class_id == None  # 或全局任务
            )
        )
else:
    # ✅ 没有班级的学生不显示任何任务
    query = query.filter(Task.id == -1)  # 返回空结果
```

### 修复效果
- ✅ 新注册的学生（没有班级）不会看到任何任务
- ✅ 有班级的学生可以看到本班老师创建的任务
- ✅ 有班级的学生也可以看到全局任务（如果需要）
- ✅ 修复了原有逻辑中全局任务被错误过滤的bug

## 可选：清理全局任务

如果不需要全局任务功能，可以运行清理脚本删除现有的全局任务：

```bash
cd backend
python clean_global_tasks.py
```

这个脚本会：
1. 列出所有全局任务（`class_id=NULL`）
2. 询问是否删除
3. 删除确认的任务

## 测试验证

### 测试步骤
1. 注册一个新的学生账号
2. 登录后查看"我的任务"页面
3. 应该看不到任何任务

### 预期结果
- 新学生：任务列表为空
- 有班级的学生：可以看到本班老师发布的任务

## 相关文件
- `backend/app/main.py` - 修改了学生任务查询逻辑（第1444-1475行）
- `backend/clean_global_tasks.py` - 清理全局任务的脚本（可选使用）

## 注意事项

如果将来需要创建全局任务（所有学生都能看到的任务），需要：
1. 修改逻辑，允许没有班级的学生也能看到全局任务
2. 或者确保所有学生都分配了班级

当前的设计理念是：
- 学生必须先被分配到班级，才能看到任务
- 任务由班主任创建和管理
- 新注册的学生需要管理员分配班级后才能使用完整功能
