"""
Hook for FAISS library.
Ensures FAISS binaries and dependencies are collected.
"""

from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# Collect all FAISS components
datas, binaries, hiddenimports = collect_all('faiss')

# Collect dynamic libraries
binaries += collect_dynamic_libs('faiss')

# Additional hidden imports
hiddenimports += [
    'faiss',
    'faiss.swigfaiss',
    'faiss.swigfaiss_avx2',
    'faiss.loader',
]
