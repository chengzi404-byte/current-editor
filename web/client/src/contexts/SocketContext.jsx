import React, { createContext, useContext, useEffect, useState } from 'react'
import io from 'socket.io-client'

const SocketContext = createContext()

export const useSocket = () => {
  const context = useContext(SocketContext)
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  useEffect(() => {
    // 创建Socket连接
    const newSocket = io('http://localhost:5000', {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    })

    newSocket.on('connect', () => {
      console.log('Socket connected')
      setIsConnected(true)
      setConnectionError(null)
    })

    newSocket.on('disconnect', () => {
      console.log('Socket disconnected')
      setIsConnected(false)
    })

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error)
      setConnectionError(error.message)
      setIsConnected(false)
    })

    newSocket.on('file_change', (data) => {
      console.log('File changed:', data)
      // 处理文件变更事件
    })

    newSocket.on('collaboration', (data) => {
      console.log('Collaboration event:', data)
      // 处理协作事件
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [])

  const joinRoom = (roomId) => {
    if (socket && isConnected) {
      socket.emit('join_room', roomId)
    }
  }

  const leaveRoom = (roomId) => {
    if (socket && isConnected) {
      socket.emit('leave_room', roomId)
    }
  }

  const sendFileChange = (filePath, content, cursorPosition) => {
    if (socket && isConnected) {
      socket.emit('file_change', {
        filePath,
        content,
        cursorPosition,
        timestamp: Date.now()
      })
    }
  }

  const value = {
    socket,
    isConnected,
    connectionError,
    joinRoom,
    leaveRoom,
    sendFileChange
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}