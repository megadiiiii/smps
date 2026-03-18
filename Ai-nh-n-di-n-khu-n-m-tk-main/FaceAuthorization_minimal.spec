# -*- mode: python ; coding: utf-8 -*-
"""
Minimal PyInstaller spec file for testing
"""

import os
import sys
from pathlib import Path

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = SPEC_DIR

# Minimal data files
datas = [
    (os.path.join(PROJECT_ROOT, 'templates'), 'templates'),
    (os.path.join(PROJECT_ROOT, 'static'), 'static'),
    (os.path.join(PROJECT_ROOT, 'models_data'), 'models_data'),
]

# Minimal hidden imports
hiddenimports = []

# No binaries for testing
binaries = []

# Analysis
a = Analysis(
    [os.path.join(PROJECT_ROOT, 'app.py')],
    pathex=[PROJECT_ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'scipy',
        'sklearn',
        'pandas',
        'sympy',
        'pydantic',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=[],
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
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
    name='FaceAuthorization',
)
