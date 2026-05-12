#!/usr/bin/env bash
# Skill 3.3 — 路径/404 类问题服务器侧自检（无硬编码部署路径，依赖环境变量）
set -euo pipefail

# 必填：仓库或部署根，用于相对定位配置模板（按实际约定设置）
: "${SMARTREC_PROJECT_ROOT:=}"

# Nginx：主配置目录或站点目录（任选其一存在即可）
: "${NGINX_CONF_DIR:=}"
: "${NGINX_SITES_DIR:=}"

# 可选：用于 curl 探测的后端直连地址（如 http://127.0.0.1:8080/health）
: "${UPSTREAM_CHECK_URL:=}"

# 服务名以系统为准
: "${NGINX_SERVICE_NAME:=nginx}"

echo "[Skill_3.3_Path_Healer] 开始路径/代理自检"

if [[ -n "${SMARTREC_PROJECT_ROOT}" && -d "${SMARTREC_PROJECT_ROOT}" ]]; then
  echo "  PROJECT_ROOT=${SMARTREC_PROJECT_ROOT}"
else
  echo "  警告: 未设置 SMARTREC_PROJECT_ROOT，跳过仓库内文件探查"
fi

if [[ -n "${NGINX_CONF_DIR}" && -d "${NGINX_CONF_DIR}" ]]; then
  echo "  检索 location / proxy_pass（示例）:"
  grep -R "location \|proxy_pass" "${NGINX_CONF_DIR}" 2>/dev/null | head -n 40 || true
fi
if [[ -n "${NGINX_SITES_DIR}" && -d "${NGINX_SITES_DIR}" ]]; then
  grep -R "location \|proxy_pass" "${NGINX_SITES_DIR}" 2>/dev/null | head -n 40 || true
fi

if [[ -n "${UPSTREAM_CHECK_URL}" ]]; then
  echo "  探测 UPSTREAM_CHECK_URL=${UPSTREAM_CHECK_URL}"
  curl -sS -o /dev/null -w "HTTP %{http_code}\n" "${UPSTREAM_CHECK_URL}" || echo "  curl 失败，请检查 URL 与防火墙"
fi

if command -v nginx >/dev/null 2>&1; then
  sudo nginx -t && echo "  nginx -t 通过" || { echo "  nginx -t 失败，请先修正配置"; exit 1; }
else
  echo "  未找到 nginx 命令，跳过 -t"
fi

echo "[Skill_3.3_Path_Healer] 若配置已修正，可执行: sudo systemctl reload \"${NGINX_SERVICE_NAME}\""
echo "完成。"
