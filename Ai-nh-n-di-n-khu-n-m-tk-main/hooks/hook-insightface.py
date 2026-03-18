"""
Hook for InsightFace library.
Ensures all InsightFace modules and data files are collected.
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all InsightFace components
datas, binaries, hiddenimports = collect_all('insightface')

# Ensure all submodules are included
hiddenimports += collect_submodules('insightface')

# Additional specific imports that might be missed
hiddenimports += [
    'insightface.app',
    'insightface.app.face_analysis',
    'insightface.model_zoo',
    'insightface.model_zoo.model_zoo',
    'insightface.model_zoo.arcface_onnx',
    'insightface.model_zoo.retinaface',
    'insightface.model_zoo.scrfd',
    'insightface.model_zoo.landmark',
    'insightface.model_zoo.attribute',
    'insightface.model_zoo.inswapper',
    'insightface.utils',
    'insightface.utils.face_align',
    'insightface.utils.transform',
    'insightface.utils.storage',
    'insightface.data',
    'insightface.thirdparty',
    'insightface.thirdparty.face3d',
]

# Collect data files (model configs, etc.)
datas += collect_data_files('insightface')
