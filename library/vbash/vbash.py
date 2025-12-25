"""
library.vbash

Provides a cross-platform shell that can run commands in PowerShell / CMD / Bash.
The shell type is automatically determined by the operating system.

Author: Phoenix Editor
Version: 1.1.0

License: MIT License
"""

import platform
import subprocess
import os
import sys
from typing import Tuple, Optional, List


class VBash:
    def __init__(self, current_dir: Optional[str] = None) -> None:
        """
        VBash - A cross-platform shell wrapper.
        
        :param current_dir: Current directory. Defaults to user's home directory.
        """
        if current_dir is None:
            self.current_dir = os.path.expanduser("~")
        else:
            self.current_dir = os.path.abspath(os.path.expanduser(current_dir))
        
        # Ensure directory exists
        if not os.path.exists(self.current_dir):
            os.makedirs(self.current_dir, exist_ok=True)
        
        self.system = platform.system()
        self.shell = self._get_shell()
        self.history: List[str] = []

    def _get_shell(self) -> str:
        """Determine the appropriate shell for the current system."""
        if self.system == "Windows":
            return "powershell"
        elif self.system in ["Linux", "Darwin"]:  # Darwin is macOS
            return "bash"
        else:
            raise NotImplementedError(f"System {self.system} is not supported")

    def run(self, command: str, capture_output: bool = True) -> Tuple[bytes, bytes, int]:
        """
        Run a command in the appropriate shell.

        :param command: Command to run
        :param capture_output: Whether to capture stdout/stderr
        :return: Tuple of (stdout, stderr, return_code)
        """
        # Add to history
        self.history.append(command)
        
        try:
            if self.system == "Windows":
                # Use PowerShell for Windows
                full_command = f'cd "{self.current_dir}"; {command}'
                result = subprocess.run(
                    ["powershell", "-Command", full_command],
                    capture_output=capture_output,
                    text=False,
                    cwd=self.current_dir
                )
            else:
                # Use bash for Unix-like systems
                full_command = f'cd "{self.current_dir}" && {command}'
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=capture_output,
                    text=False,
                    cwd=self.current_dir
                )
            
            return result.stdout, result.stderr, result.returncode
            
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            return b"", error_msg.encode(), 1

    def cd(self, directory: str) -> bool:
        """
        Change current directory.
        
        :param directory: Directory to change to
        :return: True if successful, False otherwise
        """
        try:
            # Handle home directory shortcut
            if directory == "~":
                new_dir = os.path.expanduser("~")
            else:
                # Expand user directory and handle relative paths
                expanded_dir = os.path.expanduser(directory)
                
                # Handle relative paths
                if not os.path.isabs(expanded_dir):
                    new_dir = os.path.abspath(os.path.join(self.current_dir, expanded_dir))
                else:
                    new_dir = os.path.abspath(expanded_dir)
            
            # Normalize the path (resolve .. and .)
            new_dir = os.path.normpath(new_dir)
            
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                self.current_dir = new_dir
                return True
            else:
                print(f"Directory not found: {new_dir}")
                return False
                
        except Exception as e:
            print(f"Error changing directory: {str(e)}")
            return False

    def pwd(self) -> str:
        """
        Get current directory.
        
        :return: Current directory path
        """
        return self.current_dir

    def ls(self, path: Optional[str] = None) -> List[str]:
        """
        List directory contents.
        
        :param path: Path to list (defaults to current directory)
        :return: List of directory contents
        """
        target_dir = path if path else self.current_dir
        target_dir = os.path.abspath(os.path.expanduser(target_dir))
        
        if not os.path.exists(target_dir):
            return []
        
        try:
            return os.listdir(target_dir)
        except Exception:
            return []

    def mkdir(self, directory: str) -> bool:
        """
        Create a directory.
        
        :param directory: Directory to create
        :return: True if successful, False otherwise
        """
        try:
            target_dir = os.path.join(self.current_dir, directory)
            os.makedirs(target_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {str(e)}")
            return False

    def safe_run(self, command: str, black_list: Optional[List[str]] = None) -> Tuple[bytes, bytes, int]:
        """
        Run command with safety checks.
        
        :param command: Command to run
        :param black_list: List of forbidden commands
        :return: Tuple of (stdout, stderr, return_code)
        """
        if black_list is None:
            black_list = ["rm", "del", "format", "shutdown", "init"]
        
        # Check for blacklisted commands
        command_lower = command.lower()
        for forbidden in black_list:
            if forbidden in command_lower:
                raise ValueError(f"Command contains forbidden keyword: {forbidden}")
        
        return self.run(command)

    def get_history(self) -> List[str]:
        """Get command history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()

    def execute_script(self, script_path: str) -> Tuple[bytes, bytes, int]:
        """
        Execute a shell script file.
        
        :param script_path: Path to the script file
        :return: Tuple of (stdout, stderr, return_code)
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script file not found: {script_path}")
        
        if self.system == "Windows":
            return self.run(f"& '{script_path}'")
        else:
            return self.run(f"'{script_path}'")

    def get_system_info(self) -> dict:
        """Get system information."""
        return {
            "system": self.system,
            "shell": self.shell,
            "current_directory": self.current_dir,
            "python_version": sys.version,
            "architecture": platform.architecture()[0]
        }

    __version__ = "v1.1.0"
    __author__ = "Phoenix Editor"
    __license__ = "MIT License"


def create_vbash(current_dir: Optional[str] = None) -> VBash:
    """
    Factory function to create a VBash instance.
    
    :param current_dir: Starting directory
    :return: VBash instance
    """
    return VBash(current_dir)


if __name__ == "__main__":
    # Interactive shell mode
    vbash = VBash()
    
    print("[VBash] Cross-platform Shell Wrapper")
    print(f"[VBash] Version: {vbash.__version__}")
    print(f"[VBash] System: {vbash.system}")
    print(f"[VBash] Shell: {vbash.shell}")
    print("[VBash] Type 'exit' or 'quit' to exit")
    print("[VBash] Type 'help' for available commands")
    print("-" * 50)

    while True:
        try:
            command = input(f"{vbash.current_dir} > ").strip()
            
            if command.lower() in ["exit", "quit"]:
                break
            elif command.lower() == "help":
                print("Available commands:")
                print("  cd <dir>     - Change directory")
                print("  pwd          - Show current directory")
                print("  ls [dir]     - List directory contents")
                print("  mkdir <dir>  - Create directory")
                print("  history      - Show command history")
                print("  clear        - Clear screen")
                print("  exit/quit    - Exit shell")
                continue
            elif command.lower() == "clear":
                os.system("cls" if vbash.system == "Windows" else "clear")
                continue
            elif command.lower() == "history":
                for i, cmd in enumerate(vbash.history, 1):
                    print(f"{i}: {cmd}")
                continue
            elif command.lower().startswith("cd "):
                dir_path = command[3:].strip()
                vbash.cd(dir_path)
                continue
            elif command.lower() == "pwd":
                print(vbash.current_dir)
                continue
            elif command.lower().startswith("ls"):
                args = command[2:].strip()
                items = vbash.ls(args if args else None)
                for item in items:
                    print(item)
                continue
            elif command.lower().startswith("mkdir "):
                dir_name = command[6:].strip()
                if vbash.mkdir(dir_name):
                    print(f"Directory created: {dir_name}")
                continue
            
            # Execute the command
            stdout, stderr, returncode = vbash.run(command)
            
            if stdout:
                print(stdout.decode('utf-8', errors='replace'), end='')
            if stderr:
                print(stderr.decode('utf-8', errors='replace'), end='', file=sys.stderr)
            if returncode != 0:
                print(f"\nCommand exited with code: {returncode}")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit")
        except Exception as e:
            print(f"Error: {str(e)}")