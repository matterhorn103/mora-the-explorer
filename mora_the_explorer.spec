# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src/pyinstaller.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('LICENSE.md', '.'),
        ('README.md', '.'),
        ('explorer.ico', '.'),
        ('pyproject.toml', '.'),
        ('src/mora_the_explorer/version.txt', '.'),
        ('src/mora_the_explorer/config.toml', '.'),
    ],
    #hiddenimports=['plyer.platforms.win.notification', 'plyer.platforms.macosx.notification', 'plyer.platforms.linux.notification'],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mora_the_explorer',
    icon='explorer.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mora_the_explorer',
)
app = BUNDLE(
    coll,
    name='mora_the_explorer.app',
    icon='explorer.ico',
    bundle_identifier=None,
)
