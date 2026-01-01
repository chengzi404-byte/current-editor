# Current Editor

Current Editor (Based from current editor, this project is the next version of the current editor) is a lightweight code editor designed to provide a clean and efficient programming experience. It supports syntax highlighting for multiple programming languages and comes equipped with essential code editing capabilities.

## Features

- **Multi-language Syntax Highlighting**: Support for Python, C/C++, Java, JavaScript, HTML, CSS, Ruby, Rust, Objective-C, Bash, and many other programming languages
- **Multi-file Editor**: Support for multi-tab management, allowing simultaneous editing of multiple files
- **Auto-save**: Automatically saves current content every 5 seconds to prevent data loss
- **Intelligent Syntax Analysis**: Advanced code highlighting based on AST syntax tree, supporting differentiation of variables, function names, package names, and other data types
- **Extensible Themes**: Built-in multiple dark/light themes with support for custom theme configurations
- **Multi-language Interface**: Support for Chinese, English, French, German, Japanese, Russian, and other language interfaces
- **Integrated AI Functionality**: Integration with Deepseek-R1 large language model for intelligent code assistance
- **Command Line Integration**: Built-in command line interface for direct code execution and system commands
- **Logging System**: Complete logging functionality for debugging and issue tracking
- **Cross-platform Support**: Compatible with Windows and Linux/Unix operating systems

## Installation

1. Ensure Python 3.x is installed on your system.
2. Clone this repository to your local machine:

   ```bash
   git clone https://gitee.com/your-repo/current-editor.git
   git clone https://gitee.com/chengzi404-byte/phoenix-editor.git
   ```

3. Navigate to the project directory and run the main program:

   ```bash
   cd current-editor
   python main.py
   ```

## Usage

- **New File/Window**: Click `File > New File / New Window` in the menu bar.
- **Open File**: Click `File > Open`.
- **Save File**: Click `File > Save`.
- **Run Code**: Click `Run > Run`.
- **Settings**: Click `Settings > Open Settings Panel` to adjust font, encoding, language, etc.

## Configuration

All configuration information is stored in the `asset/settings.json` file. You can manually modify this file to adjust the following settings:

- Font and font size
- Default encoding format
- Default language
- Theme style (supports dark/light mode)
- Auto-save interval

## Main Modules

- `library/highlighter/`: Syntax highlighting implementations for various programming languages
- `library/api.py`: Editor core configuration and initialization interface
- `library/directory.py`: Directory management functionality
- `library/editor_operations.py`: Editor operations implementation
- `library/highlighter_factory.py`: Highlighter factory pattern
- `library/logger.py`: Logging module
- `library/multi_file_editor.py`: Multi-file editor functionality
- `library/validator.py`: Validator module
- `main.py`: Main program entry and basic functionality implementation
- `asset/settings.json`: Stores user configurations
- `asset/theme/`: Theme style files
- `asset/packages/lang/`: Multi-language support files

## Contribution

We welcome code contributions and suggestions! Please follow these steps:

1. Fork this repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the Apache 2.0 License. Please refer to the [LICENSE](LICENSE) file for details.

## Version History

- **v0.4.0**: Added AI chat functionality
- **v0.3.0**: New multi-language support and theme switching capabilities
- **v0.2.0**: Implemented multi-tab and auto-save features
- **v0.1.1**: Optimized syntax highlighting logic
- **v0.1.0**: Initial release with basic editing and running capabilities

## Download

You can download the latest version of current Editor from the [Releases](README.md#Download) page.

## Related Links

- [Gitee Project Home](https://gitee.com/creative-and-dream/current-editor)
- [Issue Tracking](https://gitee.com/creative-and-dream/current-editor/issues)
- [Pull Request Submission Guide](.gitee/PULL_REQUEST_TEMPLATE.zh-CN.md)
- [Gitee Project Home](https://gitee.com/chengzi404-byte/phoenix-editor)
- [Issue Tracking](https://gitee.com/chengzi404-byte/phoenix-editor/issues)

## Testing

Test code is located in the `test/` directory:

- `test/test_highlighter_unit.py`: Tests for syntax highlighting functionality.
- `test/test_vbash_unit.py`: Tests for VBash-related functionality.

Run tests:

```bash
python -m unittest discover test
```
