"""
library.vbash

Provieded A shell can run command in powershell / cmd / bash.
That is decided by your system.

Author: Phoenix Editor
Version: 1.0.0

License: MIT License
"""


class VBash:
    def __init__(self, current_dir="~/") -> None:
        """
        VBash, Provieded A shell can run command in powershell / cmd / bash.
        That is decided by your system.
        
        :param current_dir: Current directory. Default is "~/".
        """

        self.current_dir = current_dir

    def run(self, command) -> tuple[bytes, bytes]:
        """
        Run command in powershell / cmd / bash.
        That is decided by your system.

        :param command: Command to run.
        :return: tuple[bytes, bytes] - stdout, stderr
        """

        import platform
        import subprocess

        if platform.system() == "Windows":
            tool = subprocess.run(f"cd {self.current_dir} ; {command}")
        elif platform.system() == "Linux":
            tool = subprocess.run(f"cd {self.current_dir} ; {command}", shell=True)
        else:
            raise Exception("Your system is not supported.")
        
        return tool.stdout, tool.stderr

    def cd(self, directory) -> None:
        """
        Change current directory.
        :param directory: Directory to change to.
        """

        self.current_dir = directory

    def pwd(self) -> str:
        """
        Get current directory.
        :return: str - Current directory.
        """

        return self.current_dir
    
    def safe_run(self, command: str, black_list: list[str] = ["rm"]) -> tuple[bytes, bytes]:
        """
        Run command in powershell / cmd / bash.
        That is decided by your system.
        But if command failed, it will return None.
        You can add a blacklist to avoid command failed.
        
        :param command: Command to run.
        :param black_list: Blacklist to avoid command failed.
        :return: tuple[bytes, bytes] - stdout, stderr
        """

        import platform
        import subprocess

        for c in command.split(' '):
            if c in black_list:
                raise Exception("Command is in blacklist.")

        if platform.system() == "Windows":
            tool = subprocess.run(f"cd {self.current_dir} ; {command}")
        elif platform.system() == "Linux":
            tool = subprocess.run(f"cd {self.current_dir} ; {command}", shell=True)
        else:
            raise Exception("Your system is not supported.")
        
        if tool.returncode == 0:
            return tool.stdout, tool.stderr
        else:
            raise Exception("Command failed.")
        
    __version__ = "v1.0.0"
    __author__ = "Phoenix Editor"
    __license__ = "MIT License"


if __name__ == "__main__":
    vbash = VBash()
    print("[VBash] Build by Phoenix Editor.")
    print("[VBash] Version: 1.0.0")
    print("[VBash] Type 'exit' to exit.")
    print("\n")

    while True:
        command = input(f"{vbash.current_dir} > ")
        if command == "exit":
            break
        else:
            try:
                vbash.run(command)
            except Exception as e:
                print(e)
