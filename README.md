# Current Editor

Current Editor 是一个轻量级的代码编辑器，旨在提供简洁高效的编程体验。它支持多种编程语言的语法高亮，并具备基本的代码编辑功能。

## 特性

- **多语言语法高亮**：支持 Python、C/C++、Java、JavaScript、HTML、CSS、Ruby、Rust、Objective-C、Bash 等多种编程语言。
- **多文件编辑器**：支持多标签页管理，可同时编辑多个文件。
- **自动保存**：每 5 秒自动保存当前编辑内容，防止数据丢失。
- **智能语法分析**：基于 AST 语法树的高级代码高亮，支持变量、函数名、包名等不同数据类型的区分。
- **可扩展主题**：内置多种深色/浅色主题，支持自定义主题配置。
- **多语言界面**：支持中文、英文、法文、德文、日文、俄文等多语言界面。
- **集成 AI 功能**：接入 Deepseek-R1 大模型，提供智能代码辅助。
- **命令行集成**：内置命令行界面，可直接运行代码和系统命令。
- **日志系统**：完整的日志记录功能，便于调试和问题排查。
- **跨平台支持**：支持 Windows 和 Linux/Unix 操作系统。

## 安装

1. 确保你已经安装了 Python 3.x。
2. 克隆本仓库到本地：

   ```bash
   git clone https://gitee.com/chengzi404-byte/phoenix-editor.git
   ```

3. 进入项目目录并运行主程序：

   ```bash
   cd current-editor
   python main.py
   ```

## 使用方法

- **新建文件/窗口**：点击菜单栏 `File > New File / New Window`。
- **打开文件**：点击菜单栏 `File > Open`。
- **保存文件**：点击菜单栏 `File > Save`。
- **运行代码**：点击菜单栏 `Run > Run`。
- **设置**：点击菜单栏 `Settings > Open Settings Panel` 可调整字体、编码、语言等。

## 配置

所有配置信息存储在 `asset/settings.json` 文件中，你可以手动修改该文件来调整以下设置：

- 字体与字号
- 默认编码格式
- 默认语言
- 主题样式（支持深色/浅色模式）
- 自动保存间隔

## 主要模块

- `library/highlighter/`: 各种编程语言的语法高亮实现。
- `library/api.py`: 编辑器核心配置与初始化接口。
- `library/directory.py`: 目录管理功能。
- `library/editor_operations.py`: 编辑器操作实现。
- `library/highlighter_factory.py`: 高亮器工厂模式。
- `library/logger.py`: 日志记录模块。
- `library/multi_file_editor.py`: 多文件编辑器功能。
- `library/validator.py`: 验证器模块。
- `main.py`: 主程序入口及基础功能实现。
- `asset/settings.json`: 存储用户配置。
- `asset/theme/`: 主题样式文件。
- `asset/packages/lang/`: 多语言支持文件。

## 测试

测试代码存放在 `test/` 目录下：

- `test/test_highlighter_unit.py`: 测试语法高亮功能。
- `test/test_vbash_unit.py`: 测试 VBash 相关功能。

运行测试：

```bash
python -m unittest discover test
```

## 贡献

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 本仓库。
2. 创建新分支 (`git checkout -b feature/new-feature`)。
3. 提交更改 (`git commit -m 'Add new feature'`)。
4. 推送分支 (`git push origin feature/new-feature`)。
5. 创建 Pull Request。

## 许可证

本项目采用 Apache 2.0 License，请参阅 [LICENSE](LICENSE) 文件了解详细信息。

## 版本历史

- **v0.1.0** 最新版本

## 下载

你可以从 [Releases](https://gitee.com/chengzi404-byte/current-editor/releases) 页面下载最新版本的 Current Editor。

## 相关链接

- [Gitee 项目主页](https://gitee.com/chengzi404-byte/phoenix-editor)
- [Issue 跟踪](https://gitee.com/chengzi404-byte/phoenix-editor/issues)