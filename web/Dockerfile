# 多阶段构建：前端构建阶段
FROM node:18-alpine AS frontend-build

WORKDIR /app/client
COPY client/package*.json ./
RUN npm ci --only=production

COPY client/ ./
RUN npm run build

# 后端运行阶段
FROM node:18-alpine

WORKDIR /app

# 安装后端依赖
COPY package*.json ./
RUN npm ci --only=production

# 复制后端代码
COPY server/ ./server/

# 复制前端构建结果
COPY --from=frontend-build /app/client/dist ./client/dist

# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S phoenix -u 1001

# 更改文件所有权
RUN chown -R phoenix:nodejs /app
USER phoenix

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node server/health-check.js

# 启动命令
CMD ["node", "server/server.js"]