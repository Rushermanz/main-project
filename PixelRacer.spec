# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static'), ('pixel_racer', 'pixel_racer'), ('assets', 'assets'), ('pixel_racer.db', '.'), ('current_player.json', '.'), ('db_utils.py', '.'), ('bahrain_bot1_run.json', '.'), ('bahrain_bot2_run.json', '.'), ('bahrain_bot3_run.json', '.'), ('baku_bot1_run.json', '.'), ('baku_bot2_run.json', '.'), ('baku_bot3_run.json', '.'), ('silverstone_bot1_run.json', '.'), ('silverstone_bot2_run.json', '.'), ('silverstone_bot3_run.json', '.'), ('spain_bot1_run.json', '.'), ('spain_bot2_run.json', '.'), ('spain_bot3_run.json', '.'), ('usa_bot1_run.json', '.'), ('usa_bot2_run.json', '.'), ('usa_bot3_run.json', '.')],
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
    [],
    exclude_binaries=True,
    name='PixelRacer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PixelRacer',
)
