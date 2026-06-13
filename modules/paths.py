"""Rutas absolutas de la aplicación (independientes del directorio de trabajo)."""
from __future__ import annotations

import os

_APP_ROOT = os.environ.get('SUDORACIONES_APP_ROOT')
if _APP_ROOT:
    APP_ROOT = os.path.abspath(_APP_ROOT)
else:
    APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_path(*parts: str) -> str:
    return os.path.join(APP_ROOT, *parts)


CONFIG_FILE = app_path('config.json')
PROGRESS_FILE = app_path('progress_data.json')
PROGRESS_BACKUP_FILE = app_path('progress_data_backup.json')
USER_SETTINGS_FILE = app_path('user_settings.json')
NUTRITION_FILE = app_path('nutrition_data.json')
LOGO_FILE = app_path('img', 'logo.png')
