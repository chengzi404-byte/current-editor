# 火凤编辑器 - 在线版本 (Phoenix Editor Web)

基于Web的远程代码编辑器，支持中英文界面，提供完整的代码编辑和文件管理功能。

## 🌟 特性

- **多语言支持**: 完整的中英文界面，UI保持一致
- **前后端分离**: 现代化的React前端 + Node.js后端架构
- **实时协作**: WebSocket支持多人实时编辑
- **Monaco编辑器**: 基于VS Code的编辑器核心
- **文件管理**: 完整的文件浏览器和操作功能
- **主题支持**: 多种编辑器主题可选
- **响应式设计**: 适配不同屏幕尺寸
- **Docker部署**: 支持容器化部署

## 🚀 快速开始

### 环境要求

- Node.js 18+
- npm 9+

### 开发模式启动

1. 安装依赖:
```bash
cd web
npm run install-all
```

2. 启动开发服务器:
```bash
npm run dev
```

这将同时启动:
- 前端开发服务器: http://localhost:3000
- 后端API服务器: http://localhost:5000

### 生产模式启动

1. 构建并启动:
```bash
cd web
./start.sh  # Linux/Mac
start.bat   # Windows
```

2. 访问: http://localhost:5000

## 📁 项目结构

```
web/
├── client/                 # 前端React应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── contexts/       # React Context
│   │   ├── locales/        # 国际化文件
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── server/                 # 后端Node.js服务
│   └── server.js          # 主服务器文件
├── package.json           # 后端依赖
├── Dockerfile             # Docker构建配置
├── docker-compose.yml     # Docker编排配置
└── README.md
```

## 🔧 技术栈

### 前端
- **React 18** - 用户界面框架
- **Monaco Editor** - 代码编辑器核心
- **Tailwind CSS** - 样式框架
- **Socket.io Client** - WebSocket客户端
- **React i18next** - 国际化支持
- **Vite** - 构建工具

### 后端
- **Express.js** - Web框架
- **Socket.io** - WebSocket服务器
- **CORS** - 跨域支持
- **文件系统API** - 文件操作

## 🌐 API接口

### 文件操作
- `GET /api/files` - 获取文件树
- `GET /api/file/:path` - 读取文件内容
- `POST /api/file/:path` - 保存文件
- `DELETE /api/file/:path` - 删除文件

### WebSocket事件
- `file_change` - 文件内容变更
- `cursor_move` - 光标移动
- `join_room` - 加入协作房间
- `leave_room` - 离开协作房间

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t phoenix-editor .
```

### 使用Docker Compose
```bash
docker-compose up -d
```

### 环境变量
- `NODE_ENV` - 运行环境 (development/production)
- `PORT` - 服务端口 (默认: 5000)

## 🔒 安全特性

- 文件路径安全检查
- 文件大小限制 (5MB)
- CORS配置
- 输入验证
- 错误处理

## 🌍 国际化

项目支持中英文界面，语言文件位于:
- `client/src/locales/zh.json` - 中文
- `client/src/locales/en.json` - 英文

语言切换通过界面右上角的下拉菜单实现。

## 🎨 界面预览

编辑器界面包含:
- **顶部工具栏**: 文件操作、语言切换、连接状态
- **左侧边栏**: 文件浏览器
- **中央编辑器**: Monaco代码编辑器
- **底部状态栏**: 文件信息、连接状态

## 📞 开发支持

### 常见问题

1. **端口冲突**: 修改`server.js`和`vite.config.js`中的端口配置
2. **依赖安装失败**: 尝试清除缓存 `npm cache clean --force`
3. **构建错误**: 检查Node.js版本是否符合要求

### 调试模式

设置环境变量启用详细日志:
```bash
export DEBUG=phoenix-editor:*
npm run dev
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。