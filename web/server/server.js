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


app.use(cors())
app.use(express.json({ limit: '50mb' }))


const staticPath = path.join(__dirname, '../client/dist')
console.log('静态文件路径:', staticPath)
app.use(express.static(staticPath))


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

    if (!filePath.startsWith(process.cwd())) {
      return res.status(403).json({ success: false, error: 'Access denied' })
    }


    await fs.mkdir(path.dirname(filePath), { recursive: true })
    
    await fs.writeFile(filePath, content, 'utf-8')

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

    if (!filePath.startsWith(process.cwd())) {
      return res.status(403).json({ success: false, error: 'Access denied' })
    }

    await fs.unlink(filePath)

    io.emit('file_deleted', {
      filePath: req.params.filePath,
      timestamp: Date.now()
    })

    res.json({ success: true })
  } catch (error) {
    res.status(500).json({ success: false, error: error.message })
  }
})

async function getFileTree(dirPath, basePath = process.cwd()) {
  const items = await fs.readdir(dirPath)
  const result = []

  for (const item of items) {
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

    socket.to(data.roomId).emit('file_change', {
      ...data,
      userId: socket.id
    })
  })

  socket.on('cursor_move', (data) => {

    socket.to(data.roomId).emit('cursor_move', {
      ...data,
      userId: socket.id
    })
  })

  socket.on('disconnect', () => {
    console.log('用户断开连接:', socket.id)
  })
})

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  })
})


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