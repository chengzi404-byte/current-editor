import React, { createContext, useContext, useState } from 'react'

const FileContext = createContext()

export const useFile = () => {
  const context = useContext(FileContext)
  if (!context) {
    throw new Error('useFile must be used within a FileProvider')
  }
  return context
}

export const FileProvider = ({ children }) => {
  const [files, setFiles] = useState([])
  const [currentFile, setCurrentFile] = useState(null)
  const [fileContent, setFileContent] = useState('')
  const [isModified, setIsModified] = useState(false)

  const addFile = (file) => {
    setFiles(prev => [...prev, file])
  }

  const removeFile = (filePath) => {
    setFiles(prev => prev.filter(file => file.path !== filePath))
    if (currentFile?.path === filePath) {
      setCurrentFile(null)
      setFileContent('')
    }
  }

  const updateFileContent = (content) => {
    setFileContent(content)
    setIsModified(true)
  }

  const saveFile = async (filePath, content) => {
    try {
      // 这里将调用后端API保存文件
      console.log('保存文件:', filePath, content)
      setIsModified(false)
      return true
    } catch (error) {
      console.error('保存文件失败:', error)
      return false
    }
  }

  const value = {
    files,
    currentFile,
    fileContent,
    isModified,
    setCurrentFile,
    setFileContent: updateFileContent,
    addFile,
    removeFile,
    saveFile,
    setIsModified
  }

  return (
    <FileContext.Provider value={value}>
      {children}
    </FileContext.Provider>
  )
}