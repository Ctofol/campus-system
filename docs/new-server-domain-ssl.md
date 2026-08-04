# 新服务器域名与 SSL 上线步骤

目标地址：

- 学生端：`https://campus.gzyichenai.com/`
- 管理端：`https://campus.gzyichenai.com/admin/`
- 健康检查：`https://campus.gzyichenai.com/system/health`

当前新服务器入口：学生端 `320`，管理端 `321`。根目录的 `remote_nginx.conf` 已按这两个入口生成。

## 1. 上传文件

不要将私钥上传到公开仓库。通过服务器控制台文件工具或 SCP 上传以下文件：

- `certs/campus.pem`
- `certs/campus.key`
- `remote_nginx.conf`

SCP 示例（将 `<SSH_PORT>` 替换为实际 SSH 端口）：

```bash
scp -P <SSH_PORT> certs/campus.pem root@111.231.55.178:/tmp/campus.pem
scp -P <SSH_PORT> certs/campus.key root@111.231.55.178:/tmp/campus.key
scp -P <SSH_PORT> remote_nginx.conf root@111.231.55.178:/tmp/campus.conf
```

## 2. 在服务器安装

```bash
install -d -m 700 /etc/nginx/ssl
install -m 644 /tmp/campus.pem /etc/nginx/ssl/campus.pem
install -m 600 /tmp/campus.key /etc/nginx/ssl/campus.key
install -m 644 /tmp/campus.conf /etc/nginx/sites-available/campus.conf
ln -sfn /etc/nginx/sites-available/campus.conf /etc/nginx/sites-enabled/campus.conf
```

若仍启用 Nginx 默认站点，应先确认其中没有其他网站，再取消默认站点：

```bash
rm /etc/nginx/sites-enabled/default
```

## 3. 校验并生效

```bash
nginx -t
systemctl reload nginx
```

只有 `nginx -t` 成功后才能执行 reload。若失败，保留原配置并根据错误信息处理，不要重启 Nginx。

## 4. 验收

```bash
curl -I http://campus.gzyichenai.com
curl -I https://campus.gzyichenai.com
curl https://campus.gzyichenai.com/system/health
curl -I https://campus.gzyichenai.com/admin/
```

预期：HTTP 跳转 HTTPS、HTTPS 证书有效、健康检查返回正常状态、管理端页面可访问。

## 5. 续期提醒

当前证书有效期至 2026-10-09。该证书不是本机 Certbot 自动签发，需在到期前从证书控制台续签并替换 `campus.pem` 与 `campus.key`，然后执行 `nginx -t && systemctl reload nginx`。
