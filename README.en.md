# Phoenix Editor

Phoenix Editor is a lightweight code editor designed to provide a clean and efficient programming experience. It supports syntax highlighting for multiple programming languages and comes equipped with essential code editing capabilities.

## Features

- Support for multi-language syntax highlighting (Python, C/C++, Java, JavaScript, HTML, CSS, etc.)
- Multi-tab management
- Auto-save functionality
- Basic code highlighting and syntax analysis
- Extensible themes and language packs
- File icon display support

## Installation

1. Ensure Python 3.x is installed on your system.
2. Clone this repository to your local machine:

   ```bash
   git clone https://gitee.com/your-repo/phoenix-editor.git
   ```

3. Navigate to the project directory and run the main program:

   ```bash
   cd phoenix-editor
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

- `library/highlighter/`: Syntax highlighting implementations for various languages
- `library/tab_manager.py`: Tab management logic
- `library/api.py`: Editor core configuration and initialization interface
- `main.py`: Main program entry and basic functionality implementation
- `asset/settings.json`: Stores user configurations
- `asset/theme/`: Theme style files
- `asset/packages/lang/`: Multi-language support files

## Q&A

**Q1: What programming language was used to develop this project?**

> This project was developed using Python and integrates the **Deepseek-r1** large language model, enabling it to quickly respond to all user requests.
> 
> It uses the AST syntax tree for highlighting, implementing code highlighting for programming languages and supporting different data types across all languages.

**Q2: What are the key features of this project?**

> ### ✨ Advantages
> 
> * Lightweight —— Occupies only about 10MB of disk space and requires just 50MB of memory to run.
>   
> * Cross-platform —— Supports operating systems such as Windows and Linux/Unix, adapting to various runtime environments.
>   
> * Open-source and free —— All source code for the project is available on [Gitee](https://gitee.com/creative-and-dream/phoenix-editor/), licensed under the MIT License. This means anyone can modify and redistribute the work, providing users with a high degree of customization.
>   
> 
> ### ⭕ Limitations
> 
> * No cloud storage functionality
>   
> * No mobile application

**Q3: What is the primary target audience for this project?**

> The education sector. Compared to most IDEs used in education, this IDE offers several advantages; see *Q2*.

**Q4: What are the advantages and disadvantages of this project compared to other education-sector IDEs on the market?**

> | Feature               | Turtle Editor | This IDE |
> |-----------------------|---------------|----------|
> | Auto-save             | √             | √        |
> | Basic code highlighting (keywords, numbers) | √             | √        |
> | Advanced code highlighting (variables, function names, package names) | X             | √        |
> | AI functionality      | X             | √        |
> | Multi-language code highlighting | X             | √        |
> | Run command           | O             | √        |
> | Cloud storage         | √             | X        |
> 
> *Using Turtle Editor as an example here*

## Contribution

We welcome code contributions and suggestions! Please follow these steps:

1. Fork this repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License. Please refer to the [LICENSE](LICENSE) file for details.

## Version History

- **v0.4.0**: Added AI chat functionality
- **v0.3.0**: New multi-language support and theme switching capabilities
- **v0.2.0**: Implemented multi-tab and auto-save features
- **v0.1.1**: Optimized syntax highlighting logic
- **v0.1.0**: Initial release with basic editing and running capabilities

## Download

You can download the latest version of Phoenix Editor from the [Releases](README.md#Download) page.

## Related Links

- [Gitee Project Home](https://gitee.com/creative-and-dream/phoenix-editor)
- [Issue Tracking](https://gitee.com/creative-and-dream/phoenix-editor/issues)
- [Pull Request Submission Guide](.gitee/PULL_REQUEST_TEMPLATE.zh-CN.md)