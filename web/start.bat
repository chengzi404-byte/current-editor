@echo off
chcp 65001 >nul

echo === 火凤编辑器启动脚本 ===

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 18或更高版本
    pause
    exit /b 1
)

REM 检查npm是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装npm
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
npm install

REM 安装客户端依赖
echo 安装客户端依赖...
cd client
npm install
cd ..

REM 构建客户端
echo 构建客户端...
cd client
npm run build
cd ..

REM 启动服务器
echo 启动服务器...
echo 前端地址: http://localhost:3000
echo 后端API: http://localhost:5000
echo 健康检查: http://localhost:5000/health
echo.

npm start
pause