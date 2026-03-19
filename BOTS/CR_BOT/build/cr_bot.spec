# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None
app_dir = Path("../app")

a = Analysis(
    [str(app_dir / "main.py")],
    pathex=[str(app_dir.parent)],
    binaries=[],
    datas=[
        (str(app_dir.parent / "profiles" / "default"), "profiles/default"),
    ],
    hiddenimports=["app.pipeline", "app.branding", "app.auth", "app.ui"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["proxy"],
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
    name="CR_BOT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CR_BOT",
)
