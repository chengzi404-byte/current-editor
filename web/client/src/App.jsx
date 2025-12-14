import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Editor from './components/Editor'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import StatusBar from './components/StatusBar'
import { FileProvider } from './contexts/FileContext'
import { SocketProvider } from './contexts/SocketContext'
import './App.css'

function App() {
  const { t, i18n } = useTranslation()
  const [currentFile, setCurrentFile] = useState(null)
  const [fileContent, setFileContent] = useState('')
  const [isConnected, setIsConnected] = useState(false)

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng)
    localStorage.setItem('editor-language', lng)
  }

  useEffect(() => {
    const savedLanguage = localStorage.getItem('editor-language')
    if (savedLanguage) {
      i18n.changeLanguage(savedLanguage)
    }
  }, [i18n])

  return (
    <SocketProvider>
      <FileProvider>
        <div className="editor-container">
          <Header 
            currentFile={currentFile}
            onLanguageChange={changeLanguage}
            isConnected={isConnected}
          />
          <div className="editor-content">
            <Sidebar 
              currentFile={currentFile}
              onFileSelect={setCurrentFile}
              onFileContentChange={setFileContent}
            />
            <Editor 
              currentFile={currentFile}
              fileContent={fileContent}
              onContentChange={setFileContent}
            />
          </div>
          <StatusBar 
            currentFile={currentFile}
            isConnected={isConnected}
          />
        </div>
      </FileProvider>
    </SocketProvider>
  )
}

export default App