from buildLibs import *

def init():
    try: mkdir(f"{Path(__file__).parent / "build"}")
    except: pass
    try: mkdir(f"{Path(__file__).parent / "build-cache"}")
    except: pass
    try: mkdir(f"{Path(__file__).parent / "released"}")
    except: pass
    try: mkdir(f"{Path(__file__).parent / "buld-cache" / "dist"}")
    except: pass
    try: mkdir(f"{Path(__file__).parent / "buld-cache" / "build"}")
    except: pass