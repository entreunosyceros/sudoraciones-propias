#!/usr/bin/env python3
"""Añadir/actualizar el campo gif en config.json y regenerar img/exercises/README.md.

No crea archivos GIF; solo rutas esperadas según el slug del nombre del ejercicio.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.paths import exercise_gif_relpath  # noqa: E402


def main() -> int:
    config_path = ROOT / 'config.json'
    cfg = json.loads(config_path.read_text(encoding='utf-8'))

    rows: list[tuple[str, str, str]] = []
    for group, exercises in cfg.get('exercises', {}).items():
        for ex in exercises:
            name = ex.get('name', '')
            rel = exercise_gif_relpath(name).replace('\\', '/')
            ex['gif'] = rel
            rows.append((group, name, Path(rel).name))

    config_path.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )

    exercises_dir = ROOT / 'img' / 'exercises'
    exercises_dir.mkdir(parents=True, exist_ok=True)
    (exercises_dir / '.gitkeep').touch()

    readme = exercises_dir / 'README.md'
    lines = [
        '# GIFs de ejercicios',
        '',
        'Coloca aquí un GIF animado por ejercicio. El nombre del archivo debe coincidir',
        'exactamente con la columna **Archivo** (slug sin acentos).',
        '',
        'Convención: minúsculas, espacios → `_`, sin acentos. Ejemplo:',
        '`Press de Banca con Mancuernas` → `press_de_banca_con_mancuernas.gif`',
        '',
        'En la app, si el archivo GIF existe se muestra **solo el GIF** (sustituye al vídeo).',
        'Si falta el GIF, se muestra YouTube como respaldo.',
        '',
        '| Grupo | Ejercicio | Archivo |',
        '|-------|-----------|---------|',
    ]
    for group, name, filename in rows:
        lines.append(f'| `{group}` | {name} | `{filename}` |')
    lines.append('')
    readme.write_text('\n'.join(lines), encoding='utf-8')

    print(f'Actualizados {len(rows)} ejercicios en {config_path}')
    print(f'Lista regenerada: {readme}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
