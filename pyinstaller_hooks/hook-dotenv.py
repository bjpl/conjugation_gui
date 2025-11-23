"""
PyInstaller hook for python-dotenv package
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect submodules
hiddenimports = collect_submodules('dotenv')

# Additional imports
hiddenimports += [
    'dotenv.main',
    'dotenv.parser',
    'dotenv.variables',
]

# Collect data files
datas = collect_data_files('dotenv')