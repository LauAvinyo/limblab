# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# This is so vedo can collect fonts and so on from the limbstaging server
vedo_datas = collect_data_files('vedo')

block_cipher = None

a = Analysis(
    ['limblab_gui/app.py'],
    pathex=['limblab_gui'],
    binaries=[],
    datas=[
        ('limblab_gui/left_icon.png', '.'),
        ('limblab_gui/threedots.png', '.'),
        ('limblab_gui/config.py', '.'),
    ] + vedo_datas,
    hiddenimports=[
        'main',
        'config',
        'NavigationMixin',
        'utils',
    ],
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
    name='LimbLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,     # False = windowed app, no terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # set to 'universal2' if you need Intel + Apple Silicon
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
    name='LimbLab',
)

app = BUNDLE(
    coll,
    name='LimbLab.app',
    icon=None,          # put an .icns path here if you have one, e.g. 'icon.icns'
    bundle_identifier='com.yourname.limblab',
)