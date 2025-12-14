import React from 'react'
import { useTranslation } from 'react-i18next'
import { Globe, Wifi, WifiOff, Save, FolderOpen, FileText } from 'lucide-react'

const Header = ({ currentFile, onLanguageChange, isConnected }) => {
  const { t, i18n } = useTranslation()

  const handleSave = () => {
    // 保存文件逻辑
    console.log('保存文件:', currentFile)
  }

  const handleNewFile = () => {
    // 新建文件逻辑
    console.log('新建文件')
  }

  const handleOpenFile = () => {
    // 打开文件逻辑
    console.log('打开文件')
  }

  return (
    <div className="editor-header">
      <div className="flex items-center space-x-4">
        <h1 className="text-lg font-bold text-white">{t('editor.title')}</h1>
        
        {/* 连接状态 */}
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <Wifi className="w-4 h-4 text-green-500" />
          ) : (
            <WifiOff className="w-4 h-4 text-red-500" />
          )}
          <span className="text-sm text-gray-300">
            {isConnected ? t('status.connected') : t('status.disconnected')}
          </span>
        </div>
      </div>

      <div className="flex-1"></div>

      <div className="flex items-center space-x-4">
        {/* 文件操作按钮 */}
        <button 
          onClick={handleNewFile}
          className="btn btn-secondary flex items-center space-x-1"
          title={t('editor.newFile')}
        >
          <FileText className="w-4 h-4" />
          <span>{t('editor.newFile')}</span>
        </button>

        <button 
          onClick={handleOpenFile}
          className="btn btn-secondary flex items-center space-x-1"
          title={t('editor.openFile')}
        >
          <FolderOpen className="w-4 h-4" />
          <span>{t('editor.openFile')}</span>
        </button>

        <button 
          onClick={handleSave}
          className="btn btn-primary flex items-center space-x-1"
          title={t('editor.saveFile')}
          disabled={!currentFile}
        >
          <Save className="w-4 h-4" />
          <span>{t('editor.saveFile')}</span>
        </button>

        {/* 语言切换 */}
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-gray-400" />
          <select 
            value={i18n.language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="bg-dark-800 border border-gray-600 rounded px-2 py-1 text-sm text-white"
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default Header