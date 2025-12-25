import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Editor from '@monaco-editor/react'

const CodeEditor = ({ currentFile, fileContent, onContentChange }) => {
  const { t } = useTranslation()
  const [language, setLanguage] = useState('javascript')
  const [theme, setTheme] = useState('vs-dark')
  const [fontSize, setFontSize] = useState(14)

  // 根据文件扩展名设置语言
  useEffect(() => {
    if (currentFile) {
      const ext = currentFile.name.split('.').pop()
      const languageMap = {
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'py': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'md': 'markdown',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'sh': 'shell',
        'bash': 'shell'
      }
      setLanguage(languageMap[ext] || 'plaintext')
    }
  }, [currentFile])

  const handleEditorChange = (value) => {
    onContentChange(value)
  }

  const handleEditorDidMount = (editor, monaco) => {
    // 编辑器挂载后的配置
    editor.focus()
    
    // 添加自定义快捷键
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      console.log('Ctrl+S pressed - Save file')
    })
  }

  if (!currentFile) {
    return (
      <div className="editor-main flex items-center justify-center bg-dark-900">
        <div className="text-center text-gray-500">
          <h3 className="text-xl mb-2">{t('editor.welcome')}</h3>
          <p>{t('editor.openFile')} {t('common.or')} {t('editor.newFile')} {t('common.to')} {t('common.start')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="editor-main">
      {/* 编辑器工具栏 */}
      <div className="editor-toolbar bg-dark-800 border-b border-gray-700 px-4 py-2 flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">{t('editor.language')}:</span>
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-dark-700 border border-gray-600 rounded px-2 py-1 text-sm text-white"
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="c">C</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
            <option value="json">JSON</option>
            <option value="markdown">Markdown</option>
            <option value="plaintext">Plain Text</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">{t('editor.theme')}:</span>
          <select 
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="bg-dark-700 border border-gray-600 rounded px-2 py-1 text-sm text-white"
          >
            <option value="vs-dark">VS Dark</option>
            <option value="vs">VS Light</option>
            <option value="hc-black">High Contrast Dark</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">{t('editor.fontSize')}:</span>
          <select 
            value={fontSize}
            onChange={(e) => setFontSize(parseInt(e.target.value))}
            className="bg-dark-700 border border-gray-600 rounded px-2 py-1 text-sm text-white"
          >
            <option value={12}>12px</option>
            <option value={14}>14px</option>
            <option value={16}>16px</option>
            <option value={18}>18px</option>
            <option value={20}>20px</option>
          </select>
        </div>
      </div>

      {/* Monaco Editor */}
      <Editor
        height="100%"
        language={language}
        theme={theme}
        value={fileContent}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          fontSize: fontSize,
          minimap: { enabled: true },
          wordWrap: 'on',
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          insertSpaces: true,
          detectIndentation: true,
          trimAutoWhitespace: true,
          formatOnPaste: true,
          formatOnType: true,
          suggestOnTriggerCharacters: true,
          quickSuggestions: true,
          parameterHints: { enabled: true },
          hover: { enabled: true },
          renderWhitespace: 'boundary',
          renderControlCharacters: true,
          folding: true,
          foldingHighlight: true,
          matchBrackets: 'always',
          autoClosingBrackets: 'always',
          autoClosingQuotes: 'always',
          autoIndent: 'full',
          bracketPairColorization: { enabled: true }
        }}
      />
    </div>
  )
}

export default CodeEditor