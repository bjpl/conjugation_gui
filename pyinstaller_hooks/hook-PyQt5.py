"""
PyInstaller hook for PyQt5
Ensures all PyQt5 components are properly bundled
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os

# Collect all PyQt5 submodules
hiddenimports = collect_submodules('PyQt5')

# Essential PyQt5 modules
hiddenimports += [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtPrintSupport',
    'PyQt5.sip',
]

# Collect data files (includes Qt plugins and resources)
datas = collect_data_files('PyQt5')

# Collect Qt binaries and libraries
binaries = collect_dynamic_libs('PyQt5')

# Add Qt platform plugins specifically for Windows
try:
    import PyQt5
    qt_root = os.path.dirname(PyQt5.__file__)
    
    # Platform plugins
    platforms_dir = os.path.join(qt_root, 'Qt', 'plugins', 'platforms')
    if os.path.exists(platforms_dir):
        for plugin in os.listdir(platforms_dir):
            if plugin.endswith('.dll'):
                datas.append((os.path.join(platforms_dir, plugin), 'platforms'))
    
    # Image format plugins
    imageformats_dir = os.path.join(qt_root, 'Qt', 'plugins', 'imageformats')
    if os.path.exists(imageformats_dir):
        for plugin in os.listdir(imageformats_dir):
            if plugin.endswith('.dll'):
                datas.append((os.path.join(imageformats_dir, plugin), 'imageformats'))
    
    # Styles
    styles_dir = os.path.join(qt_root, 'Qt', 'plugins', 'styles')
    if os.path.exists(styles_dir):
        for plugin in os.listdir(styles_dir):
            if plugin.endswith('.dll'):
                datas.append((os.path.join(styles_dir, plugin), 'styles'))
                
except ImportError:
    pass