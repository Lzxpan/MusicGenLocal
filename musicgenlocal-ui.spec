# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

project_root = Path.cwd()

datas = []
datas += [(str(project_root / "prompts"), "prompts")]
datas += copy_metadata("transformers")
datas += copy_metadata("torch")
datas += copy_metadata("sentencepiece")
datas += collect_data_files("transformers")
datas += collect_data_files("huggingface_hub")
datas += collect_data_files("sentencepiece")
datas += collect_data_files("scipy")

binaries = []
binaries += collect_dynamic_libs("torch")
binaries += collect_dynamic_libs("PySide6")
binaries += collect_dynamic_libs("sentencepiece")

hiddenimports = []
hiddenimports += collect_submodules("transformers")
hiddenimports += collect_submodules("sentencepiece")
hiddenimports += collect_submodules("scipy")
hiddenimports += [
    "PySide6.QtMultimedia",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtCore",
]

a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MusicGenLocal-Studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
