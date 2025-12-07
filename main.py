debug = True # Debug

from library.highlighter_factory import HighlighterFactory
from library.logger import setup_logger
from library.api import Settings
from library.editor_operations import EditorOperations
from tkinter import messagebox
from tkinter.font import Font
from tkinter import (
    Tk, Menu, Text, BOTH, VERTICAL, HORIZONTAL, Button
)
from tkinter.ttk import PanedWindow, Entry, Notebook, Frame
from pathlib import Path
from library import directory
import os
import json
import easygui

# -------------------- Global Variables --------------------
global settings, highlighter_factory, file_path, logger
global codehighlighter2, codehighlighter, APIKEY
logger = setup_logger()
highlighter_factory = HighlighterFactory()
file_path = "temp_script.txt"

with open(f"{Path.cwd() / 'asset' / 'settings.json'}", "r", encoding="utf-8") as fp:
    settings = json.load(fp)

# Load language settings
with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
    lang_dict = json.load(fp)

if not debug:
    try:
        APIKEY = Settings.AI.get_api_key()
    except KeyError:
        APIKEY = easygui.enterbox("API KEY: ", "API KEY:")

if not directory.test():
    directory.initlaze()

with open(f"{Path.cwd() / 'asset' / 'packages' / 'themes.dark.json'}", "r", encoding="utf-8") as fp:
    dark_themes = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'dark.json'}", "r", encoding="utf-8") as fp:
    dark_terminal_theme = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'light.json'}", "r", encoding="utf-8") as fp:
    light_terminal_theme = json.load(fp)

# -------------------- Create the window and menus --------------------

# Create the main window
root = Tk()
root.title(lang_dict["title"])
root.geometry("1920x980+0+0")
root.configure(bg='black')
root.resizable(width=True, height=True)

# Create the main paned window
main_paned = PanedWindow(root, orient=HORIZONTAL)
main_paned.pack(fill=BOTH, expand=True)

# Create the code area paned window
code_paned = PanedWindow(main_paned, orient=VERTICAL)
main_paned.add(code_paned)

# Create the multi-file editor frame
editor_frame = Frame(code_paned)
code_paned.add(editor_frame, weight=2)

subpaned = PanedWindow(code_paned, orient=HORIZONTAL)
code_paned.add(subpaned)
inputarea = Text(subpaned, font=Font(root, family=Settings.Editor.font(), size=Settings.Editor.font_size()))
subpaned.add(inputarea)
printarea = Text(subpaned, font=Font(root, family=Settings.Editor.font(), size=Settings.Editor.font_size()))
subpaned.add(printarea)

commandpaned = PanedWindow(code_paned, orient=HORIZONTAL)
code_paned.add(commandpaned, weight=1)
commandarea = Entry(commandpaned, font=Font(root, family=Settings.Editor.font(), size=Settings.Editor.font_size()))
commandpaned.add(commandarea,weight=18)
executebutton = Button(text=lang_dict["menus"]["run"])
commandpaned.add(executebutton, weight=1)

# Initialize multi-file editor
from library.multi_file_editor import MultiFileEditor
multi_editor = MultiFileEditor(editor_frame, printarea, inputarea, commandarea)

# Get the current editor for backward compatibility
codearea = multi_editor.get_current_editor()

# Config commandpaned widgets background color
if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes:
    commandarea.config(background="#2F4F4F")
else:
    commandarea.config(background="#F8F8F8")

# Show last edited content
try:
    with open("temp_script.txt", "r", encoding="utf-8") as fp:
        if codearea:
            codearea.insert("1.0", fp.read())
except FileNotFoundError:
    # If temp file doesn't exist, create an empty one
    with open("temp_script.txt", "w", encoding="utf-8") as fp:
        fp.write("")

# 初始化编辑器操作类
editor_ops = EditorOperations(root, codearea, printarea, inputarea, commandarea, 
                               None, None, None, None, None, multi_editor)

# Binding
root.bind("<Control-x>", lambda event: editor_ops.delete())
root.bind("<Control-z>", lambda event: editor_ops.undo())
root.bind("<Control-y>", lambda event: editor_ops.redo())
root.bind("<F5>", lambda event: editor_ops.run())
root.bind("<Key>", lambda event: editor_ops.autosave())

# Create all the menus
menu = Menu()
root.config(menu=menu)

# File menu
filemenu = Menu(tearoff=0)
menu.add_cascade(menu=filemenu, label=lang_dict["menus"]["file"])
filemenu.add_command(command=editor_ops.new_file, label=lang_dict["menus"]["new-file"])
filemenu.add_command(command=editor_ops.new_window, label=lang_dict["menus"]["new-window"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.open_file, label=lang_dict["menus"]["open-file"])
filemenu.add_command(command=editor_ops.save_file, label=lang_dict["menus"]["save-file"])
filemenu.add_command(command=editor_ops.save_as_file, label=lang_dict["menus"]["save-as-file"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.show_current_file_dir, label=lang_dict["menus"]["show-file-dir"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.exit_editor, label=lang_dict["menus"]["exit"])

# Edit menu
editmenu = Menu(tearoff=0)
menu.add_cascade(menu=editmenu, label=lang_dict["menus"]["edit"])
editmenu.add_command(command=editor_ops.undo, label=lang_dict["menus"]["undo"])
editmenu.add_command(command=editor_ops.redo, label=lang_dict["menus"]["redo"])
editmenu.add_separator()
editmenu.add_command(command=editor_ops.copy, label=lang_dict["menus"]["copy"])
editmenu.add_command(command=editor_ops.paste, label=lang_dict["menus"]["paste"])
editmenu.add_command(command=editor_ops.delete, label=lang_dict["menus"]["delete"])

# Run menu
runmenu = Menu(tearoff=0)
menu.add_cascade(menu=runmenu, label=lang_dict["menus"]["run"])
runmenu.add_command(command=editor_ops.run, label=lang_dict["menus"]["run"])
runmenu.add_command(command=editor_ops.clear_printarea, label=lang_dict["menus"]["clear-output"])

# Pop menu
popmenu = Menu(root, tearoff=0)
popmenu.add_command(label=lang_dict["menus"]["copy"], command=editor_ops.copy)
popmenu.add_command(label=lang_dict["menus"]["paste"], command=editor_ops.paste)
popmenu.add_command(label=lang_dict["menus"]["undo"], command=editor_ops.undo)
popmenu.add_command(label=lang_dict["menus"]["redo"], command=editor_ops.redo)

# Plugin menu (comming soon)
pluginmenu = Menu(tearoff=0)
menu.add_cascade(menu=pluginmenu, label=lang_dict["menus"]["plugin"])

# Help menu
menu.add_command(label="帮助", command=lambda: messagebox.showinfo(lang_dict["info-window-title"], lang_dict["help"]))

# 绑定事件
executebutton.config(command=editor_ops.execute_commands)

# -------------------- 初始化功能 --------------------

# Setup auto-save timer
def schedule_autosave():
    """自动保存定时器"""
    editor_ops.autosave()
    root.after(5000, schedule_autosave)  # Auto-save every 5 seconds

# Start auto-save
schedule_autosave()

# Configure menu
settingsmenu = Menu(tearoff=0)
menu.add_cascade(menu=settingsmenu, label=lang_dict["menus"]["configure"])
settingsmenu.add_command(command=lambda: editor_ops.open_settings_panel(codehighlighter, codehighlighter2), label=lang_dict["menus"]["open-settings"])

# Enable autosave
schedule_autosave()

# Bind popup event
def show_popup(event):
    """显示右键菜单"""
    popmenu.post(event.x_root, event.y_root)

codearea.bind("<Button-3>", show_popup)

# Initialization
try:
    codehighlighter = highlighter_factory.create_highlighter(codearea, multi_editor.get_current_file_path())
    
    # Check 
    theme_file = f"{Path.cwd() / "asset" / "theme" / Settings.Highlighter.syntax_highlighting()["theme"]}.json"
    if not os.path.exists(theme_file):
        logger.warning(f"Warning: Theme file {theme_file} not found, using default theme")
        print(f"Theme file {theme_file} not found, using default theme")
        # Use built-in default theme
        theme_data = {
            "base": {
                "background": "#1E1E1E",
                "foreground": "#D4D4D4",
                "insertbackground": "#D4D4D4",
                "selectbackground": "#264F78",
                "selectforeground": "#D4D4D4"
            }
        }
    else:
        # Load theme
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)
        except Exception as e:
            logger.warning(f"Warning: Failed to load theme file: {str(e)}, using default theme")
            theme_data = {
                "base": {
                    "background": "#1E1E1E",
                    "foreground": "#D4D4D4",
                    "insertbackground": "#D4D4D4",
                    "selectbackground": "#264F78",
                    "selectforeground": "#D4D4D4"
                }
            }
    
    codehighlighter.set_theme(theme_data)
    codehighlighter.highlight()

    # Use the same configure to the terminal
    codehighlighter2 = highlighter_factory.create_highlighter(printarea)
    if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes: codehighlighter2.set_theme(dark_terminal_theme)
    else: codehighlighter2.set_theme(light_terminal_theme)
    codehighlighter2.highlight()

    codehighlighter3 = highlighter_factory.create_highlighter(inputarea)
    if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes: codehighlighter3.set_theme(dark_terminal_theme)
    else: codehighlighter3.set_theme(light_terminal_theme)
    codehighlighter3.highlight()
    
    def on_key(event):
        # Process auto-save
        editor_ops.autosave()
        return None
    
    # Remove all the key binds
    for binding in root.bind_all():
        if binding.startswith('<Key'):
            root.unbind_all(binding)
    
    # Add new key bind
    root.bind("<Key>", on_key, add="+")
    
except Exception as e:
    logger.warning(f"Warning: Code highlighter initialization failed: {str(e)}")


root.mainloop()