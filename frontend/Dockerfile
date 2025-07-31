# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖 (使用npm ci for production builds)
RUN npm ci --only=production --frozen-lockfile

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 创建非root用户
RUN addgroup -g 1001 -S nginx \
    && adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# 安装必要的工具
RUN apk --no-cache add curl

# 复制构建产物到nginx
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 设置文件权限
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/run/nginx.pid

# 切换到非root用户
USER nginx

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]