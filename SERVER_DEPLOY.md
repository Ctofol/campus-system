# Run-Checkin 服务器部署指南

本指南将帮助你将项目部署到 Linux 服务器（如 Ubuntu/CentOS）。

## 1. 准备工作

在服务器上安装 Docker 环境：

```bash
# Ubuntu
curl -fsSL https://get.docker.com | bash
apt install docker-compose -y

# CentOS
curl -fsSL https://get.docker.com | bash
yum install docker-compose -y
systemctl start docker
systemctl enable docker
```

## 2. 文件上传

请使用 FTP 工具（如 FileZilla）或 SCP 命令将以下文件上传到服务器的 `/root/campus-system` 目录：

### 需要上传的文件/目录：
1. `backend/` 文件夹（包含后端代码）
2. `fronted/unpackage/dist/build/web/` 文件夹（**重要**：这是 H5 的编译结果）
   - 请先在 HBuilderX 中点击菜单：`发行` -> `网站-PC Web或手机H5` 生成此目录
   - 上传后，服务器上应有 `/root/campus-system/fronted/unpackage/dist/build/web/`
3. `fronted/nginx.conf`
4. `fronted/Dockerfile`
5. `docker-compose.yml` (位于项目根目录)

### 目录结构示例：
上传完成后，服务器上的目录结构应如下所示：

```text
/root/campus-system/
├── docker-compose.yml
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── ...
├── fronted/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── unpackage/
│       └── dist/
│           └── build/
│               └── web/
│                   ├── index.html
│                   └── ...
```

## 3. 修改配置 (重要)

### 3.1 App 连接配置
如果你要打包 App (APK) 并连接到这个服务器：
1. 打开本地代码的 `fronted/utils/request.js`。
2. 找到 `baseUrl` 配置，将其修改为你的**服务器公网 IP**：
   ```javascript
   baseUrl = 'http://<服务器公网IP>:8000';
   ```
3. 重新制作自定义调试基座或正式打包 App。

### 3.2 数据库密码 (可选)
编辑 `docker-compose.yml` 和 `backend/app/database.py` 中的数据库密码（默认为 `Chen20070509`），建议修改为更复杂的密码。

## 4. 启动服务

在服务器的 `/root/campus-system` 目录下执行：

```bash
# 启动所有服务
docker-compose up -d --build
```

## 5. 验证部署

- **后端接口**：访问 `http://<服务器IP>:8000/docs`
- **前端 H5**：访问 `http://<服务器IP>:8080`
- **数据库**：端口 `5432`

## 6. 常用维护命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码后重新部署
# 1. 上传新代码
# 2. 执行构建并重启
docker-compose up -d --build
```
