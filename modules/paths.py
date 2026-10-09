"""Rutas absolutas de la aplicación (independientes del directorio de trabajo)."""
from __future__ import annotations

import os
import re
import shutil
import unicodedata

_APP_ROOT = os.environ.get('SUDORACIONES_APP_ROOT')
if _APP_ROOT:
    APP_ROOT = os.path.abspath(_APP_ROOT)
else:
    APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_path(*parts: str) -> str:
    return os.path.join(APP_ROOT, *parts)


def exercise_gif_slug(name: str) -> str:
    """Slug de archivo para un ejercicio: minúsculas, sin acentos, espacios → _."""
    normalized = unicodedata.normalize('NFKD', name or '')
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    slug = ascii_name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    return slug.strip('_')


def exercise_gif_relpath(name: str) -> str:
    """Ruta relativa esperada del GIF de un ejercicio."""
    return os.path.join('img', 'exercises', f'{exercise_gif_slug(name)}.gif')


def resolve_exercise_gif(exercise: dict) -> str | None:
    """Ruta absoluta del GIF si existe en disco; None si falta."""
    rel = exercise.get('gif') or exercise_gif_relpath(exercise.get('name', ''))
    if not rel:
        return None
    parts = rel.replace('\\', '/').split('/')
    path = app_path(*parts)
    if os.path.isfile(path):
        return path
    return None


def _default_user_data_dir() -> str:
    """Directorio escribible para datos del usuario (progreso, nutrición, ajustes)."""
    override = os.environ.get('SUDORACIONES_DATA_DIR')
    if override:
        return os.path.abspath(override)

    # Instalación del sistema (.deb): no escribir en /opt ni /usr
    if APP_ROOT.startswith('/opt/') or APP_ROOT.startswith('/usr/'):
        xdg = os.environ.get('XDG_DATA_HOME') or os.path.join(
            os.path.expanduser('~'), '.local', 'share'
        )
        return os.path.join(xdg, 'sudoraciones')

    # Desarrollo local: datos junto al código (si el directorio es escribible)
    if os.access(APP_ROOT, os.W_OK):
        return APP_ROOT

    xdg = os.environ.get('XDG_DATA_HOME') or os.path.join(
        os.path.expanduser('~'), '.local', 'share'
    )
    return os.path.join(xdg, 'sudoraciones')


DATA_DIR = _default_user_data_dir()


def data_path(*parts: str) -> str:
    return os.path.join(DATA_DIR, *parts)


def ensure_data_dir() -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR


def _migrate_legacy_data_file(filename: str) -> None:
    """Si el .deb dejó datos en /opt, copiarlos una vez al directorio del usuario."""
    dest = data_path(filename)
    if os.path.exists(dest):
        return
    legacy = app_path(filename)
    if legacy == dest or not os.path.exists(legacy):
        return
    try:
        ensure_data_dir()
        shutil.copy2(legacy, dest)
    except OSError:
        pass


CONFIG_FILE = app_path('config.json')
LOGO_FILE = app_path('img', 'logo.png')
EXERCISES_GIF_DIR = app_path('img', 'exercises')

PROGRESS_FILE = data_path('progress_data.json')
PROGRESS_BACKUP_FILE = data_path('progress_data_backup.json')
USER_SETTINGS_FILE = data_path('user_settings.json')
NUTRITION_FILE = data_path('nutrition_data.json')

for _name in (
    'progress_data.json',
    'progress_data_backup.json',
    'user_settings.json',
    'nutrition_data.json',
):
    _migrate_legacy_data_file(_name)
