import React from 'react'
import { useTranslation } from 'react-i18next'
import { Circle, FileText, GitBranch } from 'lucide-react'

const StatusBar = ({ currentFile, isConnected }) => {
  const { t } = useTranslation()

  return (
    <div className="status-bar">
      <div className="flex items-center space-x-4">
        {/* 连接状态 */}
        <div className="flex items-center space-x-1">
          <Circle 
            className={`w-2 h-2 ${isConnected ? 'text-green-500' : 'text-red-500'}`} 
            fill="currentColor"
          />
          <span className="text-xs">
            {isConnected ? t('status.connected') : t('status.disconnected')}
          </span>
        </div>

        {/* 当前文件信息 */}
        {currentFile && (
          <div className="flex items-center space-x-1">
            <FileText className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-400">{currentFile.path}</span>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {/* 行号/列号信息 */}
        {currentFile && (
          <span className="text-xs text-gray-400">Ln 1, Col 1</span>
        )}

        {/* 编码格式 */}
        <span className="text-xs text-gray-400">UTF-8</span>

        {/* 语言信息 */}
        {currentFile && (
          <span className="text-xs text-gray-400">
            {currentFile.name.split('.').pop()?.toUpperCase() || 'TEXT'}
          </span>
        )}

        {/* Git分支信息 */}
        <div className="flex items-center space-x-1">
          <GitBranch className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-400">main</span>
        </div>
      </div>
    </div>
  )
}

export default StatusBar