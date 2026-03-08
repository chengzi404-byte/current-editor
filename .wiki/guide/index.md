# 上手指南

## 欢迎使用 Current Editor

Current Editor 是一个轻量级、现代化的代码编辑器，专为简洁高效的编程体验而设计。它支持多种编程语言的语法高亮，并具备丰富的代码编辑功能。

## 1. 环境要求

### 1.1 操作系统兼容性

| 操作系统 | 版本要求 | 支持状态 |
|---------|---------|---------|
| Windows | Windows 7/8/10/11 | ✅ 完全支持 |
| macOS | macOS 10.15+ | ❌ 不支持（开发中） |
| Linux | Ubuntu 20.04+ | ❌ 不支持（开发中） |

### 1.2 依赖软件版本要求

| 依赖软件 | 版本要求 | 说明 |
|---------|---------|------|
| Python | 3.8+ | 核心运行环境 |
| Tkinter | 8.6+ | GUI框架（Python标准库） |
| requests | 2.0+ | HTTP请求库（用于AI功能） |
| json | 标准库 | 配置文件处理 |
| pathlib | 标准库 | 文件路径处理 |

## 2. 下载指南

### 2.1 源码获取方式

#### 使用 Git 克隆

```bash
git clone https://gitee.com/chengzi404-byte/phoenix-editor.git
cd phoenix-editor
```

#### 直接下载 ZIP 文件

1. 访问 [项目仓库](https://gitee.com/chengzi404-byte/phoenix-editor)
2. 点击 "下载 ZIP" 按钮
3. 解压到本地目录

### 2.2 可用版本信息

| 版本号 | 发布日期 | 主要功能 |
|-------|---------|---------|
| v0.1.1 | 2023-01-14 | 优化语法高亮逻辑，改进用户界面 |
| v0.1.0 | 2023-01-10 | 初始版本，包含基本编辑和运行功能 |

### 2.3 分支说明

| 分支名称 | 说明 |
|---------|------|
| main | 稳定版，适合大多数用户 |
| develop | 开发版，包含最新功能但可能不稳定 |
| feature/* | 功能分支，正在开发中的新功能 |
| bugfix/* | 修复分支，正在修复的bug |

## 3. 安装步骤

### 3.1 安装依赖

Current Editor 主要依赖 Python 标准库，只需确保安装了 Python 3.8+ 即可。

```bash
# 检查 Python 版本
python --version

# 如果需要安装 Python，推荐使用官方安装包或 pyenv
# 下载地址：https://www.python.org/downloads/
```

### 3.2 配置文件设置

编辑器首次运行时会自动创建默认配置文件 `asset/settings.json`。如果需要手动配置，可以编辑该文件：

```json
{
    "editor.file-encoding": "utf-8",
    "editor.lang": "Chinese",
    "editor.font": "Consolas",
    "editor.fontsize": 12,
    "highlighter.syntax-highlighting": {
        "theme": "github-dark",
        "enable-type-hints": true,
        "enable-docstrings": true,
        "code": "python"
    }
}
```

### 3.3 初始化流程

1. 进入项目根目录：
   ```bash
   cd phoenix-editor
   ```

2. 首次启动编辑器：
   ```bash
   python app.py
   ```

3. 编辑器会自动执行初始化操作，包括：
   - 检查 Python 环境
   - 配置文件初始化
   - 主题加载

## 4. 验证安装成功

### 4.1 测试方法

1. **启动测试**：运行 `python app.py`，如果成功启动编辑器窗口，则安装基本成功。

2. **功能测试**：
   - 新建一个 Python 文件
   - 输入代码 `print("Hello World")`
   - 点击 "运行" 按钮或按 F5
   - 在终端窗口查看输出结果

### 4.2 常见问题排查

#### 问题 1：启动时显示 "当前系统不支持，仅在Windows上运行"

**解决方案**：
- 确保在 Windows 系统上运行编辑器
- 如果需要在其他系统上运行，请等待后续版本支持

#### 问题 2：启动时显示 "当前环境为conda环境，可能会导致一些问题"

**解决方案**：
- 建议在普通 Python 环境中运行
- 如果仍要在 conda 环境中运行，可以注释掉 `app.py` 中的检查部分

#### 问题 3：语法高亮不工作

**解决方案**：
- 检查当前文件的扩展名是否正确
- 在设置中检查语法高亮是否已启用
- 尝试切换主题

#### 问题 4：代码运行无输出

**解决方案**：
- 检查代码是否有语法错误
- 确保终端窗口已打开
- 检查运行命令是否正确

## 5. 快速入门

### 5.1 创建第一个文件

1. 点击菜单栏 "文件" > "新建文件"
2. 输入代码：
   ```python
   def hello(name):
       return f"Hello, {name}!"
   
   print(hello("World"))
   ```
3. 点击 "保存" 按钮，选择保存位置和文件名

### 5.2 运行代码

1. 确保代码已保存
2. 点击菜单栏 "运行" > "运行" 或按 F5
3. 在终端窗口查看输出结果：`Hello, World!`

### 5.3 基本编辑操作

- **复制/粘贴**：使用快捷键 Ctrl+C/Ctrl+V
- **撤销/重做**：使用快捷键 Ctrl+Z/Ctrl+Y
- **查找/替换**：使用快捷键 Ctrl+F

## 6. 进一步学习

- [功能介绍](./features.md)
- [键盘快捷键](./shortcuts.md)
- [主题配置](./themes.md)
- [插件开发](./plugins.md)

## 7. 联系与支持

- **项目主页**：[Gitee 项目主页](https://gitee.com/chengzi404-byte/phoenix-editor)
- **问题反馈**：[Issue 跟踪](https://gitee.com/chengzi404-byte/phoenix-editor/issues)
- **贡献代码**：欢迎提交 Pull Request

## 8. 版本更新

### 8.1 检查更新

编辑器会定期检查更新，也可以手动检查：

1. 点击菜单栏 "帮助" > "检查更新"
2. 按照提示安装最新版本

### 8.2 更新日志

- **v0.1.1**：优化语法高亮逻辑，改进用户界面
- **v0.1.0**：初始版本，包含基本编辑和运行功能

## 9. 资源链接

- [API文档](../api/index.md)
- [GitHub 仓库](https://github.com/your-repo/current-editor)
- [Gitee 仓库](https://gitee.com/chengzi404-byte/phoenix-editor)
- [发布页面](https://gitee.com/chengzi404-byte/phoenix-editor/releases)

---

祝您使用愉快！
