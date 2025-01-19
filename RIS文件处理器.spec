# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[('data\\config.json', 'data'), ('data\\ratings\\ajg_2024.json', 'data\\ratings'), ('data\\ratings\\ccf_data.json', 'data\\ratings'), ('data\\ratings\\FMS.json', 'data\\ratings'), ('data\\ratings\\zdy_ajg_all.json', 'data\\ratings'), ('data\\ratings\\zufe.json', 'data\\ratings'), ('data\\criteria\\abs3+.json', 'data\\criteria'), ('data\\criteria\\ccfC.json', 'data\\criteria'), ('data\\criteria\\FMS_b+.json', 'data\\criteria'), ('data\\profiles\\zufe.json', 'data\\profiles'), ('resources\\filter.ico', 'resources'), ('resources\\scopus.ris', 'resources')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'core', 'core.data_manager', 'core.data_types', 'core.paper_processor', 'gui', 'gui.main_window', 'utils', 'utils.translator'],
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
    name='RIS文件处理器',
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
    icon=['resources\\filter.ico'],
)
