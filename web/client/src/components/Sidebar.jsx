import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Folder, File, ChevronRight, ChevronDown } from 'lucide-react'

const Sidebar = ({ currentFile, onFileSelect, onFileContentChange }) => {
  const { t } = useTranslation()
  const [fileTree, setFileTree] = useState([])
  const [expandedFolders, setExpandedFolders] = useState(new Set())

  // 模拟文件树数据
  useEffect(() => {
    const mockFileTree = [
      {
        name: 'src',
        type: 'folder',
        children: [
          { name: 'main.js', type: 'file', path: '/src/main.js' },
          { name: 'App.jsx', type: 'file', path: '/src/App.jsx' },
          {
            name: 'components',
            type: 'folder',
            children: [
              { name: 'Header.jsx', type: 'file', path: '/src/components/Header.jsx' },
              { name: 'Sidebar.jsx', type: 'file', path: '/src/components/Sidebar.jsx' },
              { name: 'Editor.jsx', type: 'file', path: '/src/components/Editor.jsx' }
            ]
          }
        ]
      },
      {
        name: 'public',
        type: 'folder',
        children: [
          { name: 'index.html', type: 'file', path: '/public/index.html' },
          { name: 'favicon.ico', type: 'file', path: '/public/favicon.ico' }
        ]
      },
      { name: 'package.json', type: 'file', path: '/package.json' },
      { name: 'README.md', type: 'file', path: '/README.md' }
    ]
    setFileTree(mockFileTree)
  }, [])

  const toggleFolder = (folderName) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(folderName)) {
      newExpanded.delete(folderName)
    } else {
      newExpanded.add(folderName)
    }
    setExpandedFolders(newExpanded)
  }

  const handleFileClick = (file) => {
    onFileSelect(file)
    // 模拟加载文件内容
    const mockContent = `// ${file.name}
// 这是 ${file.name} 的示例内容
// 文件路径: ${file.path}

function example() {
  console.log("Hello from ${file.name}")
}

// 更多代码...`
    onFileContentChange(mockContent)
  }

  const renderFileTree = (items, level = 0) => {
    return items.map((item, index) => (
      <div key={index} style={{ paddingLeft: level * 16 }}>
        {item.type === 'folder' ? (
          <div>
            <div 
              className="file-item flex items-center space-x-1"
              onClick={() => toggleFolder(item.name)}
            >
              {expandedFolders.has(item.name) ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
              <Folder className="w-4 h-4 text-blue-400" />
              <span>{item.name}</span>
            </div>
            {expandedFolders.has(item.name) && item.children && (
              <div className="ml-4">
                {renderFileTree(item.children, level + 1)}
              </div>
            )}
          </div>
        ) : (
          <div 
            className={`file-item flex items-center space-x-1 ${
              currentFile?.path === item.path ? 'active' : ''
            }`}
            onClick={() => handleFileClick(item)}
          >
            <File className="w-4 h-4 text-gray-400" />
            <span>{item.name}</span>
          </div>
        )}
      </div>
    ))
  }

  return (
    <div className="sidebar">
      <div className="p-3 border-b border-gray-700">
        <h3 className="font-medium text-white">{t('editor.fileExplorer')}</h3>
      </div>
      <div className="file-tree">
        {renderFileTree(fileTree)}
      </div>
    </div>
  )
}

export default Sidebar