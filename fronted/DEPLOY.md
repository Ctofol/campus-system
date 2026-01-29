            # Run-Checkin 服务器部署指南

## 1. 准备工作

确保服务器已安装以下环境：
- **Docker**: [安装文档](https://docs.docker.com/engine/install/)
- **Docker Compose** (可选): [安装文档](https://docs.docker.com/compose/install/)

## 2. 部署文件清单

请将以下文件上传至服务器的同一目录下（例如 `/opt/run-checkin`）：

1.  `Dockerfile` (镜像构建文件)
2.  `nginx.conf` (Web 服务器配置)
3.  `unpackage/` 目录 (HBuilderX 发行的静态资源)
    *   *注意：请确保包含 `unpackage/dist/build/web` 目录*
4.  `docker-compose.yml` (可选，容器编排文件)

## 3. 方式一：使用 Docker Compose (推荐)

在部署目录下执行以下命令：

```bash
# 1. 构建镜像并启动服务 (-d 表示后台运行)
docker-compose up -d --build

# 2. 查看容器状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f
```

## 4. 方式二：使用原生 Docker 指令

如果您不想使用 Docker Compose，可以直接使用以下命令：

```bash
# 1. 构建 Docker 镜像 (注意最后有个点)
docker build -t run-checkin-h5 .

# 2. 运行容器
# -d: 后台运行
# -p 8080:80: 将容器80端口映射到服务器8080端口
# --name: 指定容器名称
# -v: 挂载 nginx 配置文件 (可选，方便修改)
docker run -d \
  -p 8080:80 \
  --name run-checkin-app \
  -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf \
  --restart always \
  run-checkin-h5
```

启动成功后，访问 `http://服务器IP:8080` 即可。

## 5. 常用维护命令

```bash
# 停止服务 (Docker Compose)
docker-compose down

# 停止并删除容器 (Docker 原生)
docker rm -f run-checkin-app

# 修改 nginx.conf 后重载配置（无需重启容器）
# 适用于两种部署方式
docker exec -it run-checkin-app nginx -s reload
```

## 6. 故障排查

- **403 Forbidden**: 检查 `unpackage/dist/build/web` 目录是否存在且有读取权限。
- **地图跨域错误**: 确认 `nginx.conf` 中已包含 `Cross-Origin-Embedder-Policy: unsafe-none` 配置。
