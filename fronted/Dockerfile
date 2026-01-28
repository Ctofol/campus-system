# 使用 Nginx 官方轻量级镜像

FROM nginx:alpine



# 设置时区为上海
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 复制自定义 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制 HBuilderX 发行生成的 H5 静态文件到 Nginx 目录
# ⚠️ 重要：构建镜像前，请先在 HBuilderX 中执行：
# 顶部菜单 -> 发行 -> 网站-PC Web或手机H5
# 确保 unpackage/dist/build/web 目录存在
COPY unpackage/dist/build/web /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]