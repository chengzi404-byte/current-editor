const express = require('express')
const http = require('http')
const socketIo = require('socket.io')
const cors = require('cors')
const path = require('path')
const fs = require('fs').promises

const app = express()
const server = http.createServer(app)
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
})

// 中间件
app.use(cors())
app.use(express.json({ limit: '50mb' }))

// 提供前端静态文件
const staticPath = path.join(__dirname, '../client/dist')
console.log('静态文件路径:', staticPath)
app.use(express.static(staticPath))

// 文件操作API
app.get('/api/files', async (req, res) => {
  try {
    const basePath = process.cwd()
    const files = await getFileTree(basePath)
    res.json({ success: true, files })
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

app.get('/api/file/:filePath(*)', async (req, res) => {
  try {
    const filePath = path.join(process.cwd(), req.params.filePath)
    
    // 安全检查：确保文件在项目目录内
    if (!filePath.startsWith(process.cwd())) {
      return res.status(403).json({ success: false, error: 'Access denied' })
    }

    const stats = await fs.stat(filePath)
    if (stats.isDirectory()) {
      const files = await fs.readdir(filePath)
      const fileList = await Promise.all(
        files.map(async (file) => {
          const fullPath = path.join(filePath, file)
          const fileStats = await fs.stat(fullPath)
          return {
            name: file,
            path: fullPath.replace(process.cwd(), ''),
            type: fileStats.isDirectory() ? 'folder' : 'file',
            size: fileStats.size,
            modified: fileStats.mtime
          }
        })
      )
      res.json({ success: true, files: fileList })
    } else {
      // 检查文件大小（限制为5MB）
      if (stats.size > 5 * 1024 * 1024) {
        return res.status(413).json({ 
          success: false, 
          error: 'File too large (max 5MB)' 
        })
      }

      const content = await fs.readFile(filePath, 'utf-8')
      res.json({ 
        success: true, 
        content,
        stats: {
          size: stats.size,
          modified: stats.mtime,
          created: stats.ctime
        }
      })
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

app.post('/api/file/:filePath(*)', async (req, res) => {
  try {
    const filePath = path.join(process.cwd(), req.params.filePath)
    const { content } = req.body

    // 安全检查
    if (!filePath.startsWith(process.cwd())) {
      return res.status(403).json({ success: false, error: 'Access denied' })
    }

    // 创建目录（如果不存在）
    await fs.mkdir(path.dirname(filePath), { recursive: true })
    
    await fs.writeFile(filePath, content, 'utf-8')
    
    // 广播文件变更
    io.emit('file_saved', {
      filePath: req.params.filePath,
      timestamp: Date.now()
    })

    res.json({ success: true })
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

app.delete('/api/file/:filePath(*)', async (req, res) => {
  try {
    const filePath = path.join(process.cwd(), req.params.filePath)

    // 安全检查
    if (!filePath.startsWith(process.cwd())) {
      return res.status(403).json({ success: false, error: 'Access denied' })
    }

    await fs.unlink(filePath)
    
    // 广播文件删除
    io.emit('file_deleted', {
      filePath: req.params.filePath,
      timestamp: Date.now()
    })

    res.json({ success: true })
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

// 递归获取文件树
async function getFileTree(dirPath, basePath = process.cwd()) {
  const items = await fs.readdir(dirPath)
  const result = []

  for (const item of items) {
    // 忽略隐藏文件和node_modules
    if (item.startsWith('.') || item === 'node_modules') continue

    const fullPath = path.join(dirPath, item)
    const relativePath = fullPath.replace(basePath, '')
    const stats = await fs.stat(fullPath)

    const fileInfo = {
      name: item,
      path: relativePath,
      type: stats.isDirectory() ? 'folder' : 'file',
      size: stats.size,
      modified: stats.mtime
    }

    if (stats.isDirectory()) {
      fileInfo.children = await getFileTree(fullPath, basePath)
    }

    result.push(fileInfo)
  }

  return result
}

// Socket.IO 连接处理
io.on('connection', (socket) => {
  console.log('用户连接:', socket.id)

  socket.on('join_room', (roomId) => {
    socket.join(roomId)
    console.log(`用户 ${socket.id} 加入房间 ${roomId}`)
  })

  socket.on('leave_room', (roomId) => {
    socket.leave(roomId)
    console.log(`用户 ${socket.id} 离开房间 ${roomId}`)
  })

  socket.on('file_change', (data) => {
    // 广播文件变更到同一房间的用户
    socket.to(data.roomId).emit('file_change', {
      ...data,
      userId: socket.id
    })
  })

  socket.on('cursor_move', (data) => {
    // 广播光标移动
    socket.to(data.roomId).emit('cursor_move', {
      ...data,
      userId: socket.id
    })
  })

  socket.on('disconnect', () => {
    console.log('用户断开连接:', socket.id)
  })
})

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  })
})

// 提供前端静态文件
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/dist/index.html'))
})

const PORT = process.env.PORT || 5000

server.listen(PORT, () => {
  console.log(`火凤编辑器服务器运行在端口 ${PORT}`)
  console.log(`前端地址: http://localhost:3000`)
  console.log(`后端API: http://localhost:${PORT}/api`)
  console.log(`健康检查: http://localhost:${PORT}/health`)
})