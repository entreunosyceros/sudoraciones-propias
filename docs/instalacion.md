# Instalación y uso

> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)


## Instalación (.deb)

```bash
wget https://github.com/sapoclay/sudoraciones-propias/releases/download/v1.4.2/sudoraciones_1.4.2_amd64.deb
sudo dpkg -i sudoraciones_1.4.2_amd64.deb
sudo apt-get install -f
```

### Comandos del launcher

```bash
sudoraciones start
sudoraciones stop
sudoraciones restart
sudoraciones status
sudoraciones log
```

Si el puerto `8508` está ocupado, usa `sudoraciones restart`.


## Uso desde código fuente

```bash
git clone https://github.com/sapoclay/sudoraciones-propias.git
cd sudoraciones-propias
python3 run_app.py
```

Acceso web:

- Local: `http://localhost:8508`
- Red: `http://0.0.0.0:8508`


## Estructura principal

```text
data/
└── alimentos_es.json          # Base local de alimentos (español)

img/
├── logo.png
└── exercises/                 # GIFs animados por ejercicio (opcionales)
    └── README.md              # Tabla ejercicio → nombre de archivo

modules/
├── __init__.py
├── base_trainer.py            # Planificación, equipamiento, coherencia semanal
├── estimador_alimentos.py     # Parser y estimación de macros desde texto
├── exercise_library.py
├── info.py
├── nutrition.py
├── paths.py
├── progress_calendar.py
├── statistics.py
└── training_plan.py

scripts/
└── add_gif_fields.py          # Regenerar campos gif en config.json
```

Archivos clave:

- `main_app.py`: aplicación principal
- `run_app.py`: launcher
- `config.json`: configuración de ejercicios y plan
- `user_settings.json`: equipamiento disponible del usuario *(local, no se sube a GitHub)*
- `progress_data.json`: progreso del usuario *(local, no se sube a GitHub)*
- `nutrition_data.json`: perfil nutricional, comidas y peso *(local, no se sube a GitHub)*


## Requisitos

- Python 3.12+
- Navegador moderno
- Linux/macOS/Windows
- Internet (para videos de YouTube)


## Solución rápida de problemas

### La app no inicia

1. Verifica Python 3.12+.
2. Ejecuta desde la raíz del proyecto: `python3 run_app.py`.

### Dependencias

```bash
source venv_sudoraciones/bin/activate
pip install -r requirements.txt
```


> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)

