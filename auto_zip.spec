# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    [
    'src/auto_zip/__init__.py',
    'src/auto_zip/config.py',
    'src/auto_zip/decorators.py',
    'src/auto_zip/i18n.py',
    'src/auto_zip/lang.py',
    'src/auto_zip/log_config.py',
    'src/auto_zip/main.py',
    'src/auto_zip/utils.py',
    ],
    pathex=[os.path.abspath('src/auto_zip')],
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
    name='自动压缩txt文件v1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)