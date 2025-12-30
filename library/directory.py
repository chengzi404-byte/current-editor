from os import mkdir
from pathlib import Path
import json

needed_files = [
    "asset",
    "asset/packages",
    "asset/theme",
    "library",
    "library/highlighter"
]

def initlaze():
    folder_fix()
    languange_files_fix()
    theme_fix()
    database_fix()

def folder_fix():
    mkdir('asset')
    mkdir('asset/packages') 
    mkdir('asset/packages/lang')
    mkdir('asset/theme')
    mkdir('asset/theme/terminalTheme')
    mkdir('asset/settings.json')

def languange_files_fix():
    with open('asset/packages/lang/Chinese.json', 'w', encoding='utf-8') as fp:
        json.dump(fp, 
                    {
                        "plugin": {
                            "download-success": [ "插件", "插件下载成功，请重启软件。" ],
                            "download-failture": [ "插件", "插件安装失败: {}" ]
                        }, 
                        "settings": {
                            "font": "字体",
                            "font-size": "字体大小",
                            "theme": "主题",
                            "languange": "语言",
                            "restart": "请重新启动软件来应用设置",
                            "close": "关闭",
                            "title": "设置",
                            "coding-languange": "编程语言",
                            "clear-cache": "清空缓存"
                        },
                        "menus": {
                            "configure": "设置",
                            "open-settings": "设置",
                            "file": "文件",
                            "new-file": "新建文件",
                            "new-window": "新建窗口",
                            "open-file": "打开文件",
                            "save-file": "保存文件",
                            "save-as-file": "另存为",
                            "show-file-dir": "显示文件路径",
                            "exit": "退出",
                            "edit": "编辑",
                            "undo": "撤销",
                            "redo": "重做",
                            "copy": "复制",
                            "paste": "粘贴",
                            "delete": "删除",
                            "plugin": "插件",
                            "run": "运行",
                            "clear-output": "清除输出",
                            "help": "帮助"
                        },
                        "file-types": [
                            "Python 文件",
                            "HTML 文件",
                            "CSS 文件",
                            "JavaScript 文件",
                            "JSON 文件",
                            "Ruby 文件",
                            "C/C++ 文件",
                            "Objective-C 文件",
                            "所有文件"
                        ],
                        "plugin-types": [
                            "插件文件",
                            "所有文件"
                        ],
                        "ai": {
                            "title": "AI 助手",
                            "send": "发送",
                            "show": "显示 AI 侧边栏",
                            "hide": "隐藏 AI 侧边栏"
                        },
                        "info-window-title": "提示",
                        "title": "火凤编辑器",
                        "help": "火凤编辑器\n版本：v0.4.2\n\n作者：chengzi404(gitee) remain(github)"
                    }

        )
    with open('asset/packages/lang/English.json', 'w', encoding='utf-8') as fp:
        json.dump(fp, 
                    {
                        "plugin": {
                            "download-success": ["Plugin", "Plugin downloaded successfully. Please restart the software."],
                            "download-failture": ["Plugin", "Plugin installation failed: {}"]
                        }, 
                        "settings": {
                            "font": "Font",
                            "font-size": "Font Size",
                            "theme": "Theme",
                            "languange": "Language",
                            "restart": "Please restart the software to apply settings",
                            "close": "Close",
                            "title": "Settings",
                            "coding-languange": "Coding Language",
                            "clear-cache": "Clear Cache"
                        },
                        "menus": {
                            "configure": "Settings",
                            "open-settings": "Settings",
                            "file": "File",
                            "new-file": "New File",
                            "new-window": "New Window",
                            "open-file": "Open File",
                            "save-file": "Save File",
                            "save-as-file": "Save As",
                            "show-file-dir": "Show File Path",
                            "exit": "Exit",
                            "edit": "Edit",
                            "undo": "Undo",
                            "redo": "Redo",
                            "copy": "Copy",
                            "paste": "Paste",
                            "delete": "Delete",
                            "plugin": "Plugin",
                            "run": "Run",
                            "clear-output": "Clear Output",
                            "help": "Help"
                        },
                        "file-types": [
                            "Python File",
                            "HTML File",
                            "CSS File",
                            "JavaScript File",
                            "JSON File",
                            "Ruby File",
                            "C/C++ File",
                            "Objective-C File",
                            "All Files"
                        ],
                        "plugin-types": [
                            "Plugin File",
                            "All Files"
                        ],
                        "ai": {
                            "title": "AI Assistant",
                            "send": "Send",
                            "show": "Show AI Sidebar",
                            "hide": "Hide AI Sidebar"
                        },
                        "info-window-title": "Info",
                        "title": "Phoenix Editor",
                        "help": "Phoenix Editor\nVersion: v0.4.2\n\nAuthor: chengzi404(gitee) remain(github)"
                    }

        )

    with open('asset/packages/lang/__Chinese.json', 'w', encoding='utf-8') as fp:
        json.dump(fp, 
            {
                "plugin": {
                    "download-success": ["插件", "插件下載成功，請重啟軟件。"],
                    "download-failture": ["插件", "插件安裝失敗: {}"]
                },
                "settings": {
                    "font": "字體",
                    "font-size": "字體大小",
                    "theme": "主題",
                    "language": "語言",
                    "restart": "請重新啟動軟件來應用設置",
                    "close": "關閉",
                    "title": "設置",
                    "coding-language": "編程語言",
                    "clear-cache": "清空緩存"
                },
                "menus": {
                    "configure": "設置",
                    "open-settings": "設置",
                    "file": "文件",
                    "new-file": "新建文件",
                    "new-window": "新建窗口",
                    "open-file": "打開文件",
                    "save-file": "保存文件",
                    "save-as-file": "另存為",
                    "show-file-dir": "顯示文件路徑",
                    "exit": "退出",
                    "edit": "編輯",
                    "undo": "撤銷",
                    "redo": "重做",
                    "copy": "複製",
                    "paste": "粘貼",
                    "delete": "刪除",
                    "plugin": "插件",
                    "run": "運行",
                    "clear-output": "清除輸出",
                    "help": "幫助"
                },
                "file-types": [
                    "Python 文件",
                    "HTML 文件",
                    "CSS 文件",
                    "JavsaScript 文件",
                    "JSON 文件",
                    "Ruby 文件",
                    "C/C++ 文件",
                    "Objective-C 文件",
                    "所有文件"
                ],
                "plugin-types": [
                    "插件文件",
                    "所有文件"
                ],
                "ai": {
                    "title": "AI 助手",
                    "send": "發送",
                    "show": "顯示 AI 側邊欄",
                    "hide": "隱藏 AI 側邊欄"
                },
                "info-window-title": "提示",
                "title": "火鳳編輯器",
                "help": "火鳳編輯器\n版本：v0.4.2\n\n作者：chengzi404(gitee) remain(github)"
            }
        )

def database_fix():
    with open('asset/settings.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "editor.file-encoding": "utf-8",
                "editor.lang": "Chinese",
                "editor.font": "Consolas",
                "editor.fontsize": 12,
                "editor.file-path": "./temp_script.txt",
                "highlighter.syntax-highlighting": {
                    "theme": "github-dark",
                    "enable-type-hints": True,
                    "enable-docstrings": True,
                    "code": "python"
                },
                "run.timeout": 1000,
                "run.racemode": False
            }
        )

    with open('asset/packages/code_support.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            [
                "bash",
                "c",
                "cpp",
                "css",
                "html",
                "java",
                "javascript",
                "json",
                "objc",
                "python",
                "ruby",
                "rust"
            ]
        )

def theme_fix():
    with open('asset/theme/vscode-dark.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "keyword": "#569CD6",
                "control": "#C586C0",
                "operator": "#D4D4D4",
                "punctuation": "#D4D4D4",
                
                "class": "#4EC9B0",
                "function": "#DCDCAA",
                "method": "#DCDCAA",
                "variable": "#9CDCFE",
                "parameter": "#9CDCFE",
                "property": "#9CDCFE",
                
                "string": "#CE9178",
                "number": "#B5CEA8",
                "boolean": "#569CD6",
                "null": "#569CD6",
                "constant": "#4FC1FF",
                
                "comment": "#6A9955",
                "docstring": "#6A9955",
                "todo": "#FF8C00",
                
                "decorator": "#C586C0",
                "builtin": "#4EC9B0",
                "self": "#569CD6",
                "namespace": "#4EC9B0",
                
                "type": "#4EC9B0",
                "type_annotation": "#4EC9B0",
                "interface": "#4EC9B0",
                
                "error": "#F44747",
                "warning": "#DDB100",
                
                "regex": "#D16969",
                "markup": "#CE9178",
                "link": "#3794FF",
                
                "modified": "#1B81A8",
                "deprecated": "#848484",

                "base": {
                    "background": "#1E1E1E",
                    "foreground": "#D4D4D4",
                    "insertbackground": "#D4D4D4",
                    "selectbackground": "#264F78",
                    "selectforeground": "#D4D4D4"
                }
            }
        )

    with open('asset/theme/github-light.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "base": {
                    "background": "#FFFFFF",
                    "foreground": "#24292E",
                    "insertbackground": "#24292E",
                    "selectbackground": "#C8C8FA",
                    "selectforeground": "#24292E"
                },
                "keyword": "#D73A49",
                "control": "#D73A49",
                "operator": "#24292E",
                "punctuation": "#24292E",
                
                "class": "#6F42C1",
                "function": "#6F42C1",
                "method": "#6F42C1",
                "variable": "#24292E",
                "parameter": "#24292E",
                "property": "#24292E",
                
                "string": "#032F62",
                "number": "#005CC5",
                "boolean": "#005CC5",
                "null": "#005CC5",
                "constant": "#005CC5",
                
                "comment": "#6A737D",
                "docstring": "#6A737D",
                "todo": "#FF8C00",
                
                "decorator": "#6F42C1",
                "builtin": "#005CC5",
                "self": "#24292E",
                "namespace": "#6F42C1",
                
                "type": "#6F42C1",
                "type_annotation": "#6F42C1",
                "interface": "#6F42C1"
            } 

        )

    with open('asset/theme/dracula.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "base": {
                    "background": "#282A36",
                    "foreground": "#F8F8F2",
                    "insertbackground": "#F8F8F2",
                    "selectbackground": "#44475A",
                    "selectforeground": "#F8F8F2"
                },
                "keyword": "#FF79C6",
                "control": "#FF79C6",
                "operator": "#FF79C6",
                "punctuation": "#F8F8F2",
                
                "class": "#50FA7B",
                "function": "#50FA7B",
                "method": "#50FA7B",
                "variable": "#F8F8F2",
                "parameter": "#F8F8F2",
                "property": "#F8F8F2",
                
                "string": "#F1FA8C",
                "number": "#BD93F9",
                "boolean": "#BD93F9",
                "null": "#BD93F9",
                "constant": "#BD93F9",
                
                "comment": "#6272A4",
                "docstring": "#6272A4",
                "todo": "#FFB86C",
                
                "decorator": "#50FA7B",
                "builtin": "#8BE9FD",
                "self": "#FF79C6",
                "namespace": "#50FA7B",
                
                "type": "#8BE9FD",
                "type_annotation": "#8BE9FD",
                "interface": "#8BE9FD"
            }
        )

    with open('asset/theme/github-dark.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            {
                "base": {
                    "background": "#0D1117",
                    "foreground": "#C9D1D9",
                    "insertbackground": "#C9D1D9",
                    "selectbackground": "#363D4A",
                    "selectforeground": "#C9D1D9"
                },
                "keyword": "#FF7B72",
                "control": "#FF7B72",
                "operator": "#C9D1D9",
                "punctuation": "#C9D1D9",
                
                "class": "#D2A8FF",
                "function": "#D2A8FF",
                "method": "#D2A8FF",
                "variable": "#C9D1D9",
                "parameter": "#C9D1D9",
                "property": "#C9D1D9",
                
                "string": "#A5D6FF",
                "number": "#79C0FF",
                "boolean": "#79C0FF",
                "null": "#79C0FF",
                "constant": "#79C0FF",
                
                "comment": "#8B949E",
                "docstring": "#8B949E",
                "todo": "#FFA657",
                
                "decorator": "#D2A8FF",
                "builtin": "#79C0FF",
                "self": "#C9D1D9",
                "namespace": "#D2A8FF",
                
                "type": "#D2A8FF",
                "type_annotation": "#D2A8FF",
                "interface": "#D2A8FF"
            }    
        )
    
    with open('asset/theme/material.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            {
                "base": {
                    "background": "#263238",
                    "foreground": "#EEFFFF",
                    "insertbackground": "#EEFFFF",
                    "selectbackground": "#37474F",
                    "selectforeground": "#EEFFFF"
                },
                "keyword": "#C792EA",
                "control": "#C792EA",
                "operator": "#89DDFF",
                "punctuation": "#EEFFFF",
                
                "class": "#FFCB6B",
                "function": "#82AAFF",
                "method": "#82AAFF",
                "variable": "#EEFFFF",
                "parameter": "#EEFFFF",
                "property": "#EEFFFF",
                
                "string": "#C3E88D",
                "number": "#F78C6C",
                "boolean": "#F78C6C",
                "null": "#F78C6C",
                "constant": "#F78C6C",
                
                "comment": "#546E7A",
                "docstring": "#546E7A",
                "todo": "#FF8C00",
                
                "decorator": "#82AAFF",
                "builtin": "#89DDFF",
                "self": "#C792EA",
                "namespace": "#FFCB6B",
                
                "type": "#FFCB6B",
                "type_annotation": "#FFCB6B",
                "interface": "#FFCB6B"
            }
        )
    
    with open('asset/theme/nord.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            {
                "base": {
                    "background": "#2E3440",
                    "foreground": "#D8DEE9",
                    "insertbackground": "#D8DEE9",
                    "selectbackground": "#3B4252",
                    "selectforeground": "#D8DEE9"
                },
                "keyword": "#81A1C1",
                "control": "#81A1C1",
                "operator": "#D8DEE9",
                "punctuation": "#D8DEE9",
                
                "class": "#8FBCBB",
                "function": "#88C0D0",
                "method": "#88C0D0",
                "variable": "#D8DEE9",
                "parameter": "#D8DEE9",
                "property": "#D8DEE9",
                
                "string": "#A3BE8C",
                "number": "#B48EAD",
                "boolean": "#B48EAD",
                "null": "#B48EAD",
                "constant": "#B48EAD",
                
                "comment": "#4C566A",
                "docstring": "#4C566A",
                "todo": "#EBCB8B",
                
                "decorator": "#88C0D0",
                "builtin": "#81A1C1",
                "self": "#81A1C1",
                "namespace": "#8FBCBB",
                
                "type": "#8FBCBB",
                "type_annotation": "#8FBCBB",
                "interface": "#8FBCBB"
            }
        )

    with open('asset/theme/one-dark-pro.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "base": {
                    "background": "#282C34",
                    "foreground": "#ABB2BF",
                    "insertbackground": "#ABB2BF",
                    "selectbackground": "#3E4451",
                    "selectforeground": "#ABB2BF"
                },
                "keyword": "#C678DD",
                "control": "#C678DD",
                "operator": "#56B6C2",
                "punctuation": "#ABB2BF",
                
                "class": "#E5C07B",
                "function": "#61AFEF",
                "method": "#61AFEF",
                "variable": "#E06C75",
                "parameter": "#ABB2BF",
                "property": "#E06C75",
                
                "string": "#98C379",
                "number": "#D19A66",
                "boolean": "#D19A66",
                "null": "#D19A66",
                "constant": "#D19A66",
                
                "comment": "#7F848E",
                "docstring": "#7F848E",
                "todo": "#FF8C00",
                
                "decorator": "#61AFEF",
                "builtin": "#56B6C2",
                "self": "#E06C75",
                "namespace": "#E5C07B",
                
                "type": "#E5C07B",
                "type_annotation": "#E5C07B",
                "interface": "#E5C07B"
            } 
        )

    with open('asset/theme/solarized-dark.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "base": {
                    "background": "#002B36",
                    "foreground": "#839496",
                    "insertbackground": "#839496",
                    "selectbackground": "#073642",
                    "selectforeground": "#839496"
                },
                "keyword": "#859900",
                "control": "#859900",
                "operator": "#859900",
                "punctuation": "#839496",
                
                "class": "#CB4B16",
                "function": "#268BD2",
                "method": "#268BD2",
                "variable": "#839496",
                "parameter": "#839496",
                "property": "#839496",
                
                "string": "#2AA198",
                "number": "#D33682",
                "boolean": "#D33682",
                "null": "#D33682",
                "constant": "#D33682",
                
                "comment": "#586E75",
                "docstring": "#586E75",
                "todo": "#FF8C00",
                
                "decorator": "#268BD2",
                "builtin": "#B58900",
                "self": "#B58900",
                "namespace": "#CB4B16",
                
                "type": "#B58900",
                "type_annotation": "#B58900",
                "interface": "#B58900"
            } 
        )

    with open('asset/theme/sloarized-light.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            {
                "base": {
                    "background": "#FDF6E3",
                    "foreground": "#657B83",
                    "insertbackground": "#657B83",
                    "selectbackground": "#EEE8D5",
                    "selectforeground": "#657B83"
                },
                "keyword": "#859900",
                "control": "#859900",
                "operator": "#859900",
                "punctuation": "#657B83",
                
                "class": "#CB4B16",
                "function": "#268BD2",
                "method": "#268BD2",
                "variable": "#657B83",
                "parameter": "#657B83",
                "property": "#657B83",
                
                "string": "#2AA198",
                "number": "#D33682",
                "boolean": "#D33682",
                "null": "#D33682",
                "constant": "#D33682",
                
                "comment": "#93A1A1",
                "docstring": "#93A1A1",
                "todo": "#FF8C00",
                
                "decorator": "#268BD2",
                "builtin": "#B58900",
                "self": "#B58900",
                "namespace": "#CB4B16",
                
                "type": "#B58900",
                "type_annotation": "#B58900",
                "interface": "#B58900"
            }
        )

    with open('asset/theme/terminalTheme/dark.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp, 
            {
                "keyword": "#569CD6",
                "control": "#C586C0",
                "operator": "#D4D4D4",
                "punctuation": "#D4D4D4",
                
                "class": "#4EC9B0",
                "function": "#DCDCAA",
                "method": "#DCDCAA",
                "variable": "#9CDCFE",
                "parameter": "#9CDCFE",
                "property": "#9CDCFE",
                
                "string": "#CE9178",
                "number": "#B5CEA8",
                "boolean": "#569CD6",
                "null": "#569CD6",
                "constant": "#4FC1FF",
                
                "comment": "#6A9955",
                "docstring": "#6A9955",
                "todo": "#FF8C00",
                
                "decorator": "#C586C0",
                "builtin": "#4EC9B0",
                "self": "#569CD6",
                "namespace": "#4EC9B0",
                
                "type": "#4EC9B0",
                "type_annotation": "#4EC9B0",
                "interface": "#4EC9B0",
                
                "error": "#F44747",
                "warning": "#DDB100",
                
                "regex": "#D16969",
                "markup": "#CE9178",
                "link": "#3794FF",
                
                "modified": "#1B81A8",
                "deprecated": "#848484",

                "base": {
                    "background": "#1E1E1E",
                    "foreground": "#D4D4D4",
                    "insertbackground": "#D4D4D4",
                    "selectbackground": "#264F78",
                    "selectforeground": "#D4D4D4"
                }
            }
        )
    
    with open('asset/theme/terminalTheme/light.json', 'w', encoding='utf-8') as fp:
        json.dump(
            fp,
            {
                "keyword": "#0000FF",
                "control": "#800080",
                "operator": "#000000",
                "punctuation": "#000000",
                
                "class": "#2B91AF",
                "function": "#795E26",
                "method": "#795E26",
                "variable": "#001080",
                "parameter": "#001080",
                "property": "#001080",
                
                "string": "#A31515",
                "number": "#098658",
                "boolean": "#0000FF",
                "null": "#0000FF",
                "constant": "#007ACC",
                
                "comment": "#008000",
                "docstring": "#008000",
                "todo": "#FF8C00",
                
                "decorator": "#800080",
                "builtin": "#2B91AF",
                "self": "#0000FF",
                "namespace": "#2B91AF",
                
                "type": "#2B91AF",
                "type_annotation": "#2B91AF",
                "interface": "#2B91AF",
                
                "error": "#FF0000",
                "warning": "#FFA500",
                
                "regex": "#C00000",
                "markup": "#A31515",
                "link": "#0000FF",
                
                "modified": "#007ACC",
                "deprecated": "#808080",

                "base": {
                    "background": "#FFFFFF",
                    "foreground": "#000000",
                    "insertbackground": "#000000",
                    "selectbackground": "#ADD8E6",
                    "selectforeground": "#000000"
                }
            }
        )

def test() -> bool:
    flag = True
    for need_file in needed_files:
        if not Path(need_file).exists(): flag = False
    return flag