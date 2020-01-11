import os
from typing import Any
from typing import Dict
from typing import Optional


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_envvars: Dict[str, Any] = {}

with open(os.path.join(ROOT_DIR, '.env')) as f:
    for line in f:
        key, value = tuple(line.split('='))
        _envvars[key] = value


def get_setting(key: str, type: type, default: Optional[Any] = None) -> Any:
    return _envvars.get(key, default)


API_KEY = get_setting('API_KEY', str, '')
