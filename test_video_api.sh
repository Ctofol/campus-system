#!/bin/bash

# 测试视频播放相关API
# 使用方法: bash test_video_api.sh

SERVER="http://120.26.17.147:8000"

echo "========================================="
echo "测试视频播放API"
echo "========================================="
echo ""

# 1. 测试登录获取token
echo "1. 测试登录..."
LOGIN_RESPONSE=$(curl -s -X POST "${SERVER}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"123456"}')

echo "登录响应: $LOGIN_RESPONSE"
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败，无法获取token"
  exit 1
fi

echo "✅ 登录成功，Token: ${TOKEN:0:20}..."
echo ""

# 2. 测试获取课程列表
echo "2. 测试获取课程列表..."
COURSES_RESPONSE=$(curl -s -X GET "${SERVER}/courses/?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN")

echo "课程列表响应: $COURSES_RESPONSE"
echo ""

# 3. 获取第一个课程ID
COURSE_ID=$(echo $COURSES_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$COURSE_ID" ]; then
  echo "❌ 没有找到课程"
  exit 1
fi

echo "✅ 找到课程ID: $COURSE_ID"
echo ""

# 4. 测试获取课程详情
echo "3. 测试获取课程详情..."
COURSE_DETAIL=$(curl -s -X GET "${SERVER}/courses/${COURSE_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "课程详情响应: $COURSE_DETAIL"
echo ""

# 5. 获取第一个内容ID
CONTENT_ID=$(echo $COURSE_DETAIL | grep -o '"id":[0-9]*' | sed -n '2p' | cut -d':' -f2)

if [ -z "$CONTENT_ID" ]; then
  echo "⚠️  课程没有内容，跳过内容测试"
  exit 0
fi

echo "✅ 找到内容ID: $CONTENT_ID"
echo ""

# 6. 测试获取单个内容详情（新增的API）
echo "4. 测试获取单个内容详情..."
CONTENT_DETAIL=$(curl -s -X GET "${SERVER}/courses/content/${CONTENT_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "内容详情响应: $CONTENT_DETAIL"

if echo "$CONTENT_DETAIL" | grep -q "Not Found"; then
  echo "❌ API不存在或返回404"
else
  echo "✅ 内容详情API正常"
fi
echo ""

# 7. 测试获取播放进度（新增的API）
echo "5. 测试获取播放进度..."
PROGRESS_GET=$(curl -s -X GET "${SERVER}/courses/content/${CONTENT_ID}/progress" \
  -H "Authorization: Bearer $TOKEN")

echo "播放进度响应: $PROGRESS_GET"

if echo "$PROGRESS_GET" | grep -q "Not Found"; then
  echo "❌ API不存在或返回404"
else
  echo "✅ 获取进度API正常"
fi
echo ""

# 8. 测试保存播放进度（新增的API）
echo "6. 测试保存播放进度..."
PROGRESS_SAVE=$(curl -s -X POST "${SERVER}/courses/content/${CONTENT_ID}/progress?last_position=120&completed=false" \
  -H "Authorization: Bearer $TOKEN")

echo "保存进度响应: $PROGRESS_SAVE"

if echo "$PROGRESS_SAVE" | grep -q "Not Found"; then
  echo "❌ API不存在或返回404"
else
  echo "✅ 保存进度API正常"
fi
echo ""

echo "========================================="
echo "测试完成"
echo "========================================="
