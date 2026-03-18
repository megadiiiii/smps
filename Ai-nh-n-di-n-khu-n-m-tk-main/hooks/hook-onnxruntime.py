"""
Hook for ONNX Runtime library.
Ensures all ONNX Runtime providers and dependencies are collected.
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

# Collect all ONNX Runtime components
datas, binaries, hiddenimports = collect_all('onnxruntime')

# Collect dynamic libraries
binaries += collect_dynamic_libs('onnxruntime')

# Additional hidden imports
hiddenimports += [
    'onnxruntime',
    'onnxruntime.capi',
    'onnxruntime.capi._pybind_state',
    'onnxruntime.capi.onnxruntime_pybind11_state',
    'onnxruntime.capi.onnxruntime_validation',
    'onnxruntime.datasets',
    'onnxruntime.tools',
    'onnxruntime.transformers',
]
