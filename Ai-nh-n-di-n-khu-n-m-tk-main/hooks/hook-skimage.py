"""
Hook for scikit-image library.
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all skimage components
datas, binaries, hiddenimports = collect_all('skimage')

# Ensure transform module is included
hiddenimports += [
    'skimage.transform',
    'skimage.transform._geometric',
    'skimage.transform._warps',
    'skimage._shared',
    'skimage._shared.geometry',
    'skimage.io',
    'skimage.color',
    'skimage.util',
]
