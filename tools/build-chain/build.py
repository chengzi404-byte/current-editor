"""
Phoenix building tool chain

- building tool information
    version v0.1
    type    CLI     Command Line Interface

- folder information
    tools/build-cache               Building cache (Including Final EXE File, Build commands, and so on)
    tools/build-chain/build         Could released building application (Could use)
    tools/build-chain/released      Released ZIP Files

This tool is made by chengzi404@gitee
"""

from buildInfo import *
from buildLibs import *
from buildInit import *


version = input("Press the version of this package: s")
mode = input("Mode of build: \n[1] Input needed folders \n[2] Load in json file \nChoose:")
if mode == '1':
    needed_folders = input("Please press needed folders (Split as spaces): ").split()
    needed_files = input("Please press needed single files (Split as spaces): ").split()
    system("cls")
if mode == '2':
    json_file = input("Please input file path")
    with open(json_file, "r", encoding="utf-8") as fp:
        data = json.load(fp)
        needed_files = data["files"]
        needed_folders = data["folders"]

# Creating folders
init()

# Wrote building commands
if not (Path(__file__).parent / "build-cache" / "build.spec").exists():
    print(Fore.BLUE + "[INFO]", Fore.RESET + "Generating Building File...", end=" ")

    with open(f"{Path(__file__).parent / "build-cache" / "build.spec"}", "w", encoding="utf-8") as fp:
        fp.write(build_spec)

    print(Fore.GREEN + "Success!")

# Copying main.py
copyfile(f"{Path(__file__).parent.parent.parent / "main.py"}", f"{Path(__file__).parent / "build-cache" / "main.py"}")

# Running building
print(Fore.BLUE + "[INFO]", Fore.RESET + "Building EXE file...")
run(f"pyinstaller {Path(__file__).parent / "build-cache" / "build.spec"} --distpath {Path(__file__).parent / "build-cache"} --workpath {Path(__file__).parent / "build-cache"}")

# Copying needed files
print(Fore.BLUE + "[INFO]", Fore.RESET + "Copying needed files...")
copyfile(f"{Path(__file__).parent / "build-cache" / "main.exe"}", f"{Path(__file__).parent / "build" / "main.exe"}")
for folder in needed_folders:
    copytree(folder, f"{Path(__file__) / "build" / folder}", dirs_exist_ok=True)
for file in needed_files:
    copyfile(file, f"{Path(__file__) / "build" / file}")

# Zipping files
print(Fore.BLUE + "[INFO]", Fore.RESET + "Making ZIP file")
make_zip(f"{Path(__file__).parent / "released" / (version + ".zip")}", f"{Path(__file__) / "build" / file}")

# Done!
print(Fore.GREEN + "Done!")
print(Fore.RESET)

system("pause")