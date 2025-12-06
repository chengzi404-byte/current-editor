from subprocess import run
from os import mkdir
from time import time
from pathlib import Path
import json

class Version:
    def __init__(self):
        with open(f"{Path(__file__).parent / "release.json"}", "r", encoding="utf-8") as fp:
            self.releaseData = json.load(fp)

        self.lastRelease = self.releaseData["last"]
 
        self.packTime = time()
        self.buildVer = f"build+{self.packTime}"
        self.snapVer = f"{self.lastRelease}-snapshot"
        self.releaseVer = f"{self.releaseVer}"

    @property
    def buildVer(self): return self.buildVer
    
    @property
    def snapVer(self): return self.snapVer

def packing(version):
    packVer = version.getVersion()
    run(f"git archive --format=zip --output={packVer}/source-code.zip {packVer}")

def release(version):
    run(f"""git tag -a {version.version} -m "Snapshot version {version.getVersion()}" """)