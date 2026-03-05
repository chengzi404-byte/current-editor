import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QTabWidget,
    QTextEdit, QMenuBar, QMenu, QToolBar, QStatusBar,
    QMessageBox, QApplication, QInputDialog, QFontDialog, QLabel
)
from PyQt6.QtCore import Qt, QTimer, QDir, QMimeData, QUrl
from PyQt6.QtGui import QAction, QKeySequence, QFont, QColor, QPalette, QIcon, QFileSystemModel

from library.api import Settings
from library.logger import get_logger
from library.i18n import get_i18n, t
from ui.highlighter import SyntaxHighlighter
from ui.lsp_client import LSPClient
from ui.terminal import TerminalWidget

logger = get_logger()
i18n = get_i18n()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_file_path = None
        self.file_dir = "."
        self.syntax_highlighter = None
        self.lsp_client = None
        self.document_version = 1
        
        self._init_lsp()
        self._init_ui()
        self._init_highlighter()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_theme()
        
        logger.info("主窗口初始化完成")
    
    def _init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.file_tree = self._create_file_tree()
        splitter.addWidget(self.file_tree)
        
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        self.editor = self._create_editor()
        self.tab_widget.addTab(self.editor, t("untitled"))
        
        right_splitter.addWidget(self.tab_widget)
        
        self.terminal = self._create_terminal()
        right_splitter.addWidget(self.terminal)
        
        right_splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        
        splitter.addWidget(right_splitter)
        splitter.setSizes([280, int(self.width() - 280)])
        
        main_layout.addWidget(splitter)
    
    def _init_lsp(self):
        self.lsp_client = LSPClient(self._on_lsp_diagnostic)
        self.lsp_client.start_server()
    
    def _on_lsp_diagnostic(self, uri, diagnostics):
        if not diagnostics:
            return
        
        error_lines = []
        for diag in diagnostics:
            range_info = diag.get("range", {})
            start = range_info.get("start", {})
            line = start.get("line", 0) + 1
            message = diag.get("message", "")
            severity = diag.get("severity", 3)
            
            if severity == 1:
                error_lines.append(f"Error (line {line}): {message}")
            elif severity == 2:
                error_lines.append(f"Warning (line {line}): {message}")
        
        if error_lines:
            self.terminal_widget.append("\n".join(error_lines))
    
    def _init_highlighter(self):
        theme_file = Path("./asset/theme") / f"{Settings.Highlighter.theme()}.json"
        self.syntax_highlighter = SyntaxHighlighter(self.editor_widget, theme_file)
        self.syntax_highlighter.set_file_path(None)
    
    def _create_file_tree(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.sidebar_header = QLabel(t("explorer"))
        self.sidebar_header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.sidebar_header)
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.tree_view.setHeaderHidden(False)
        self.tree_view.clicked.connect(self.on_file_clicked)
        
        layout.addWidget(self.tree_view)
        
        return container
    
    def _create_editor(self):
        self.editor_widget = QTextEdit()
        self.editor_widget.setFont(QFont(Settings.Editor.font(), Settings.Editor.font_size()))
        self.editor_widget.setAcceptRichText(False)
        self.editor_widget.textChanged.connect(self.on_text_changed)
        return self.editor_widget
    
    def _create_terminal(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.terminal_header = QLabel(t("terminal"))
        self.terminal_header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.terminal_header)
        
        self.terminal_widget = TerminalWidget()
        
        layout.addWidget(self.terminal_widget)
        
        return container
    
    def _create_actions(self):
        self.new_file_action = QAction(t("new_file"), self)
        self.new_file_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_file_action.triggered.connect(self.new_file)
        
        self.open_file_action = QAction(t("open_file"), self)
        self.open_file_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_file_action.triggered.connect(self.open_file)
        
        self.open_folder_action = QAction(t("open_folder"), self)
        self.open_folder_action.triggered.connect(self.open_folder)
        
        self.save_action = QAction(t("save"), self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction(t("save_as"), self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.save_as_file)
        
        self.exit_action = QAction(t("exit"), self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)
        
        self.undo_action = QAction(t("undo"), self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.editor_widget.undo)
        
        self.redo_action = QAction(t("redo"), self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.editor_widget.redo)
        
        self.cut_action = QAction(t("cut"), self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(self.editor_widget.cut)
        
        self.copy_action = QAction(t("copy"), self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.editor_widget.copy)
        
        self.paste_action = QAction(t("paste"), self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.editor_widget.paste)
        
        self.run_action = QAction(t("run"), self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.triggered.connect(self.run_code)
        
        self.clear_terminal_action = QAction(t("clear_output"), self)
        self.clear_terminal_action.triggered.connect(self.clear_terminal)
        
        self.font_action = QAction(t("font"), self)
        self.font_action.triggered.connect(self.change_font)
        
        self.theme_action = QAction(t("theme"), self)
        self.theme_action.triggered.connect(self.change_theme)
        
        self.about_action = QAction(t("about"), self)
        self.about_action.triggered.connect(self.show_about)
    
    def _create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu(t("file"))
        file_menu.addAction(self.new_file_action)
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.open_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        edit_menu = menubar.addMenu(t("edit"))
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        
        run_menu = menubar.addMenu(t("run"))
        run_menu.addAction(self.run_action)
        run_menu.addAction(self.clear_terminal_action)
        
        settings_menu = menubar.addMenu(t("settings"))
        settings_menu.addAction(self.font_action)
        settings_menu.addAction(self.theme_action)
        
        help_menu = menubar.addMenu(t("help"))
        help_menu.addAction(self.about_action)
    
    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_file_action)
        toolbar.addAction(self.open_file_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_action)
    
    def _create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(t("ready"))
        
        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.statusbar.addPermanentWidget(self.cursor_pos_label)
    
    def _apply_theme(self):
        theme_name = Settings.Highlighter.theme()
        theme_file = Path("./asset/theme") / f"{theme_name}.json"
        
        if theme_file.exists():
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)
            
            base = theme_data.get("base", {})
            bg_color = base.get("background", "#ffffff")
            fg_color = base.get("foreground", "#000000")
            
            from PyQt6.QtGui import QPalette, QColor
            from PyQt6.QtWidgets import QApplication
            
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Base, QColor(bg_color))
            palette.setColor(QPalette.ColorRole.Text, QColor(fg_color))
            palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
            
            self.editor_widget.setPalette(palette)
            self.terminal_widget.setPalette(palette)
            
            self.editor_widget.setStyleSheet("")
            self.terminal_widget.setStyleSheet("")
            
            if self.syntax_highlighter and self.syntax_highlighter.highlighter:
                self.syntax_highlighter.highlighter._load_theme(theme_file)
                self.syntax_highlighter.highlighter.rehighlight()
    
    def on_file_clicked(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file_from_path(file_path)
    
    def open_file_from_path(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.editor_widget.setPlainText(content)
            self.current_file_path = file_path
            
            if self.syntax_highlighter:
                self.syntax_highlighter.set_file_path(file_path)
            
            if self.lsp_client and self.lsp_client.is_ready():
                uri = f"file:///{file_path.replace(os.sep, '/')}"
                self.lsp_client.open_document(uri, content, "python")
                self.document_version = 1
            
            tab_text = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_text)
            
            self.statusbar.showMessage(f"{t('opened')}: {file_path}")
            logger.info(f"Opened file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"Failed to open file: {str(e)}")
            logger.error(f"Failed to open file: {str(e)}")
    
    def __init__(self):
        super().__init__()
        # ... 其他初始化代码
        self._last_lsp_update = 0
        self._lsp_update_timer = QTimer()
        self._lsp_update_timer.setSingleShot(True)
        self._lsp_update_timer.timeout.connect(self._delayed_lsp_update)

    def on_text_changed(self):
        if not self.tab_widget.tabText(self.tab_widget.currentIndex()).endswith("*"):
            self.tab_widget.setTabText(
                self.tab_widget.currentIndex(),
                self.tab_widget.tabText(self.tab_widget.currentIndex()) + "*"
            )
        
        # 延迟500ms发送LSP更新，避免频繁触发
        self._lsp_update_timer.start(500)

    def _delayed_lsp_update(self):
        if self.lsp_client and self.lsp_client.is_ready() and self.current_file_path:
            content = self.editor_widget.toPlainText()
            uri = f"file:///{self.current_file_path.replace(os.sep, '/')}"
            self.lsp_client.change_document(uri, content, self.document_version)
            self.document_version += 1
    
    def new_file(self):
        self.editor_widget.clear()
        self.current_file_path = None
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), t("untitled"))
        self.statusbar.showMessage(t("new_file_created"))
        logger.info("Created new file")
    
    def open_file(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, t("open_file"), "",
            t("file_filter")
        )
        if file_path:
            self.open_file_from_path(file_path)
    
    def open_folder(self):
        from PyQt6.QtWidgets import QFileDialog
        folder_path = QFileDialog.getExistingDirectory(self, t("open_folder"))
        if folder_path:
            self.file_tree_view = self.tree_view
            self.tree_view.setRootIndex(self.file_model.index(folder_path))
            self.file_dir = folder_path
            self.statusbar.showMessage(f"{t('folder_opened')}: {folder_path}")
            logger.info(f"Opened folder: {folder_path}")
    
    def save_file(self):
        if self.current_file_path:
            try:
                content = self.editor_widget.toPlainText()
                with open(self.current_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                tab_text = os.path.basename(self.current_file_path)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_text)
                
                self.statusbar.showMessage(f"{t('saved')}: {self.current_file_path}")
                logger.info(f"Saved file: {self.current_file_path}")
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"Failed to save file: {str(e)}")
                logger.error(f"Failed to save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("save_as"), "",
            t("file_filter")
        )
        if file_path:
            self.current_file_path = file_path
            self.save_file()
    
    def run_code(self):
        self.terminal_widget.clear()
        
        if self.current_file_path:
            import subprocess
            import sys
            
            try:
                self.statusbar.showMessage(t("running"))
                result = subprocess.run(
                    [sys.executable, self.current_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = result.stdout
                if result.stderr:
                    output += "\n[Error]\n" + result.stderr
                
                self.terminal_widget.setPlainText(output)
                self.statusbar.showMessage(t("execution_finished"))
                logger.info("Code executed successfully")
            except subprocess.TimeoutExpired:
                self.terminal_widget.setPlainText(t("execution_timeout"))
                logger.warning("Code execution timed out")
            except Exception as e:
                self.terminal_widget.setPlainText(f"Error: {str(e)}")
                logger.error(f"Execution error: {str(e)}")
        else:
            temp_file = "./temp_script.py"
            try:
                content = self.editor_widget.toPlainText()
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                import subprocess
                import sys
                
                self.statusbar.showMessage(t("running"))
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = result.stdout
                if result.stderr:
                    output += "\n[Error]\n" + result.stderr
                
                self.terminal_widget.setPlainText(output)
                self.statusbar.showMessage(t("execution_finished"))
                logger.info("Code executed successfully")
            except Exception as e:
                self.terminal_widget.setPlainText(f"Error: {str(e)}")
                logger.error(f"Execution error: {str(e)}")
    
    def clear_terminal(self):
        self.terminal_widget.clear()
    
    def change_font(self):
        font, ok = QFontDialog.getFont(self.editor_widget.font(), self)
        if ok:
            self.editor_widget.setFont(font)
            Settings.Editor.change("font", font.family())
            Settings.Editor.change("fontsize", font.pointSize())
    
    def change_theme(self):
        themes = ["github", "github-light", "vscode-light", "one-light", "solarized-light"]
        
        theme, ok = QInputDialog.getItem(self, t("select_theme"), "Theme:", themes, 0, False)
        if ok:
            Settings.Highlighter.change("theme", theme)
            self._apply_theme()
            
            if self.syntax_highlighter:
                theme_file = Path("./asset/theme") / f"{theme}.json"
                self.syntax_highlighter.set_theme(theme_file)
            
            logger.info(f"Theme changed to: {theme}")
    
    def show_about(self):
        QMessageBox.about(
            self,
            t("about"),
            t("about_text")
        )
    
    def close_tab(self, index):
        if index > 0:
            self.tab_widget.removeTab(index)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, t("exit"),
            t("confirm_exit"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.lsp_client:
                self.lsp_client.shutdown()
            event.accept()
            logger.info("Application closed")
        else:
            event.ignore()
