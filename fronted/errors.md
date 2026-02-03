# 常见报错与处理文档

## 1. H5 定位失败 / 需 HTTPS
- 现象：浏览器无法获取定位或长时间无位置更新。
- 触发条件：非 HTTPS 域名（localhost/127.0.0.1除外）或用户拒绝定位权限。
- 日志关键字：`Location failed`, `H5定位需HTTPS`。
- 参考代码：[run.vue:getLocation/doGetLocation](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L626-L653)
- 处理：
  - 使用 HTTPS 或 localhost/127.0.0.1。
  - 引导开启定位权限；失败时降级使用模拟位置并提示。

## 2. 地图轨迹始终为直线或不更新
- 现象：轨迹总指向固定方向或不刷新。
- 原因：轨迹与导航线状态未分层或更新未触发渲染。
- 参考代码：[updateMapPolyline](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L340-L357)、[startNormalRun](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L907-L919)
- 处理：
  - 轨迹与导航线分离管理；更新折线时深拷贝触发渲染。
  - 普通跑步开始时清空导航线。

## 3. 搜索不同地点却总定位同方向
- 现象：搜索或地图选择后，导航线始终指向固定方向。
- 原因：未使用后端真实打卡点或目标点未更新到导航折线。
- 参考代码：[searchCheckpoint/handleMapSelect](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L657-L783)
- 处理：
  - 使用后端打卡点数据进行模糊搜索；
  - 重新生成 points 并深拷贝更新导航线。

## 4. 计步/传感器监听异常
- 现象：步数增长异常或性能问题。
- 原因：重复监听或阈值、防抖不合理。
- 参考代码：[startStepCount](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L820-L869)
- 处理：
  - 开启前停止已有监听；
  - 使用阈值、最小间隔与强制复位超时优化。

## 5. 提交数据失败
- 现象：结束跑步后提示“提交失败”，或跳转结果页失败。
- 原因：网络或后端错误、token 失效。
- 参考代码：[stopRun](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L951-L1026)
- 处理：
  - 校验登录状态并引导重新登录；
  - 弹窗提供重试与强制结束选项；
  - 检查后端返回的 detail。

## 6. 校园打卡未触发成功
- 现象：到达目标点附近不提示“打卡成功”。
- 原因：围栏半径或 ID 未传入，导致仅本地提示。
- 参考代码：[updateLocationLogic](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L406-L425)
- 处理：
  - 确保 checkpoint.id 与 radius 正确传入；
  - 调用后端 checkIn 接口。

## 7. 配速达标判定不正确
- 现象：专项测试页面配速状态与教师任务要求不一致。
- 原因：pace/target 参数解析或单位换算错误。
- 参考代码：[onLoad](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L541-L557)
- 处理：
  - 在 onLoad 解析 pace 与 target（米），判定采用分钟/公里；
  - 任务列表将 min_distance(km)→米，min_duration(分钟)→pace(分钟/公里)。

## 8. NaN/Infinity 数据异常
- 现象：配速或距离显示/计算异常。
- 原因：距离为0时计算配速、定位抖动或异常点未过滤。
- 参考代码：[currentPace](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L526-L533)、[updateLocationLogic](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L385-L436)
- 处理：
  - 配速在 km=0 时返回0；
  - 过滤过小/过大的位移（如 d>2 且 d<100）；
  - 限制异常值上限。
