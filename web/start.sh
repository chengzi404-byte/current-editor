#!/bin/bash

# 火凤编辑器启动脚本

echo "=== 火凤编辑器启动脚本 ==="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 18或更高版本"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装npm"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
npm install

# 安装客户端依赖
echo "安装客户端依赖..."
cd client
npm install
cd ..

# 构建客户端
echo "构建客户端..."
cd client
npm run build
cd ..

# 启动服务器
echo "启动服务器..."
echo "前端地址: http://localhost:3000"
echo "后端API: http://localhost:5000"
echo "健康检查: http://localhost:5000/health"

npm start