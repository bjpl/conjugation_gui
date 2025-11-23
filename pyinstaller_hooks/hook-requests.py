"""
PyInstaller hook for requests package
Ensures SSL certificates and all components are bundled
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all requests submodules
hiddenimports = collect_submodules('requests')

# Additional hidden imports
hiddenimports += [
    'requests.adapters',
    'requests.auth', 
    'requests.cookies',
    'requests.exceptions',
    'requests.models',
    'requests.sessions',
    'requests.packages.urllib3',
    'requests.packages.urllib3.contrib.pyopenssl',
    'requests.packages.urllib3.util',
    'requests.packages.urllib3.util.retry',
    'urllib3',
    'urllib3.contrib.pyopenssl',
    'urllib3.util',
    'urllib3.util.retry',
    'certifi',
]

# Collect data files (includes CA certificates)
datas = collect_data_files('requests')
datas += collect_data_files('certifi')
datas += collect_data_files('urllib3')