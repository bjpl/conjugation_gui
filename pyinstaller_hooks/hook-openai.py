"""
PyInstaller hook for OpenAI package
Ensures all necessary OpenAI modules are included
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Collect all OpenAI submodules
hiddenimports = collect_submodules('openai')

# Additional hidden imports for OpenAI
hiddenimports += [
    'openai.api_resources',
    'openai.api_resources.abstract',
    'openai.api_resources.completion',
    'openai.api_resources.chat_completion',
    'openai.api_resources.edit',
    'openai.api_resources.image',
    'openai.api_resources.embedding',
    'openai.api_resources.file',
    'openai.api_resources.fine_tune',
    'openai.api_resources.model',
    'openai.api_resources.moderation',
    'openai.error',
    'openai.util',
    'openai.api_requestor',
    'openai.openai_object',
    'openai.version',
]

# Collect data files
datas = collect_data_files('openai')

# Collect dynamic libraries if any
binaries = collect_dynamic_libs('openai')