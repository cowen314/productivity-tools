from pathlib import Path
from sys import platform

if platform.startswith('win32'):
    _app_data_dir = Path.home() / 'AppData' / 'Roaming' / 'toggl-importer'
else:
    _app_data_dir = Path.home() / '.config' / 'toggl-importer'

_app_data_dir.mkdir(mode=0o0700, parents=True, exist_ok=True)
app_settings_file = _app_data_dir / 'config.json'

toggl_secrets_file = _app_data_dir / 'toggl-secrets.json'