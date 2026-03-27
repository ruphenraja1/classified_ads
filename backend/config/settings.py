"""Django settings wrapper.

This file chooses between development and production settings based on the
`DJANGO_ENV` environment variable.

- `DJANGO_ENV=prod` -> loads `config.settings_prod`
- anything else -> loads `config.settings_dev`
"""

import os
from decouple import config
from importlib import import_module

# Temporarily force dev settings for testing
if config('DJANGO_ENV') == 'prod':
    _module = import_module('config.settings_prod')

else:
    _module = import_module('config.settings_dev')

# Expose everything from the selected module as if it were defined here.
for _k, _v in vars(_module).items():
    if _k.isupper():
        globals()[_k] = _v
