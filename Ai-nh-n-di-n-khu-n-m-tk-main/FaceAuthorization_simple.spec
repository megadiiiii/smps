# -*- mode: python ; coding: utf-8 -*-
"""
Simplified PyInstaller spec for Face Authorization
"""

import os
from pathlib import Path

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = SPEC_DIR

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'app.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, 'templates'), 'templates'),
        (os.path.join(PROJECT_ROOT, 'static'), 'static'),
        (os.path.join(PROJECT_ROOT, 'models_data'), 'models_data'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tcl', 'tk', 'tkinter', 'matplotlib', 'PyQt5', 'PyQt6', 'pytest'],
    noarchive=False,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceAuthorization',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceAuthorization',
)
