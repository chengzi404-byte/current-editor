from buildLibs import *



def make_zip(output_zip, source_dir):
    with ZipFile(output_zip, 'w', ZIP_DEFLATED) as zipf:
        if not path.exists(source_dir):
            return
        
        for root, dirs, files in walk(source_dir):
            for file in files:
                file_path = path.join(root, file)
                arcname = path.relpath(file_path, path.dirname(source_dir))
                zipf.write(file_path, arcname)

build_spec = """
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""