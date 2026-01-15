# Current Editor

Current Editor is a lightweight and modern code editor designed to provide a clean and efficient programming experience. It supports syntax highlighting for multiple programming languages and offers rich code editing features.

## 🌟 Features

- **Multi-language Syntax Highlighting**: Support for Python, C/C++, Java, JavaScript, HTML, CSS, Ruby, Rust, Go, Objective-C, Bash, and dozens of other programming languages.
- **Multi-file Editor**: Tab-based management system supporting simultaneous editing of multiple files with easy switching.
- **Auto-save Mechanism**: Automatically saves current editing content every 5 seconds, effectively preventing data loss.
- **Intelligent Syntax Analysis**: Advanced code highlighting based on AST syntax tree, accurately distinguishing between variables, function names, package names, and other data types.
- **Extensible Theme System**: Built-in multiple dark/light themes (such as VS Code, GitHub, Dracula, etc.), supporting custom theme configurations.
- **Multi-language Interface**: Support for Chinese, English, French, German, Japanese, Russian, and other language interfaces to meet global user needs.
- **Integrated AI Functionality**: Integration with Deepseek-R1 large language model, providing intelligent code suggestions, error fixes, and other auxiliary features.
- **Command Line Integration**: Built-in command line interface supporting direct code execution and system commands.
- **Complete Logging System**: Detailed logging functionality for debugging and issue troubleshooting.
- **First Start Optimization**: Automatically detects and downloads Python environment, intelligently selecting the optimal installation source.

## 🚀 Installation

### Prerequisites

- Python 3.x environment

### Installation Steps

1. Clone this repository to your local machine:

   ```bash
   git clone https://gitee.com/chengzi404-byte/phoenix-editor.git
   ```

2. Navigate to the project directory:

   ```bash
   cd phoenix-editor
   ```

3. Run the main program:

   ```bash
   python app.py
   ```

## 💡 Usage

### Basic Operations

- **New File/Window**: Click on the menu bar `File > New File / New Window`
- **Open File**: Click on the menu bar `File > Open File`
- **Save File**: Click on the menu bar `File > Save File`
- **Run Code**: Click on the menu bar `Run > Run` or use the shortcut key `F5`
- **View Help**: Click on the menu bar `Help` to view version information and usage guidelines

### Settings

Click on the menu bar `Settings > Open Settings Panel` to adjust the following parameters:

- Font and font size
- File encoding format
- Interface language
- Theme style
- Auto-save interval

## 📁 Project Structure

```
current-editor/
├── asset/              # Resource files directory
│   ├── icons/         # Icon resources
│   ├── packages/      # Package resources
│   ├── theme/         # Theme files
│   └── settings.json  # Configuration file
├── lang/              # Multi-language support
├── library/           # Core library modules
│   ├── highlighter/   # Syntax highlighting implementations
│   ├── api.py         # Core interfaces
│   ├── editor_operations.py  # Editor operations
│   ├── logger.py      # Logging system
│   ├── multi_file_editor.py  # Multi-file editor
│   ├── py_executable_check.py  # Python environment check
│   └── startup.py     # First start operations
├── ui/                # UI interface modules
│   ├── main_window.py # Main window
│   ├── menu.py        # Menu
│   ├── tabs.py        # Tab components
│   └── file_browser.py  # File browser
├── test/              # Test code
├── app.py             # Main program entry
└── README.md          # Project description
```

## 🛠️ Core Modules

- **library/highlighter/**: Syntax highlighting implementations for various programming languages, supporting precise code coloring.
- **library/multi_file_editor.py**: Multi-file editing functionality with tab management and file switching.
- **library/editor_operations.py**: Core editing operations including copy, paste, undo, redo, etc.
- **library/logger.py**: Complete logging system for debugging and issue tracking.
- **library/startup.py**: Automatic configuration and environment checking during first startup.
- **ui/main_window.py**: Application main window responsible for interface layout and component management.
- **ui/tabs.py**: Tab components including settings panel and help panel.

## 🧪 Testing

Test code is located in the `test/` directory, written using Python's standard unittest framework:

```bash
python -m unittest discover test
```

## 📝 Version History

- **v0.1.1**: Optimized syntax highlighting logic and improved user interface
- **v0.1.0**: Initial release with basic editing and running capabilities

## 🤝 Contributing

Contributions are welcome! Please submit Issues and Pull Requests to help improve the project.

### Contribution Process

1. Fork this repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License. Please refer to the [LICENSE](LICENSE) file for details.

## 📞 Contact Us

- Gitee Project Home: https://gitee.com/chengzi404-byte/phoenix-editor
- Issue Tracking: https://gitee.com/chengzi404-byte/phoenix-editor/issues

---

**Current Editor** - Making programming more efficient!