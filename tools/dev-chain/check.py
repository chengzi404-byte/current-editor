from pathlib import Path
from subprocess import Popen, PIPE
from sys import executable


def check_complie():
    main_path = Path(__file__).parent.parent.parent / "main.py"

    runtool = Popen([executable, main_path], stdin=PIPE, 
                            stderr=PIPE, stdout=PIPE)

    _, stderr = runtool.communicate()

    if stderr == b'': return True