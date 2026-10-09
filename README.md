# Sudoraciones Propias

[![Versión](https://img.shields.io/badge/versión-1.4.1-2ea44f)](https://github.com/entreunosyceros/sudoraciones-propias/releases)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Licencia](https://img.shields.io/badge/licencia-GPL--3.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/entreunosyceros/sudoraciones-propias?display_name=tag)](https://github.com/entreunosyceros/sudoraciones-propias/releases)
[![Plataforma](https://img.shields.io/badge/plataforma-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](docs/instalacion.md)

<img width="1066" height="1832" alt="sudoraciones-portada" src="https://github.com/user-attachments/assets/c59911ed-bbee-4a42-bbb3-f6e6433536ec" />

Sistema personal de entrenamiento en **Python 3.12+** y Streamlit: progresión automática, calendario, nutrición y seguimiento en casa… Hecho por un motivo en particular, pero si a alguien le sirve, genial.

## Documentación

La guía completa está dividida por temas. Puedes moverte entre páginas con la barra de navegación de cada documento:

| Tema | Descripción |
|------|-------------|
| [Índice de docs](docs/README.md) | Punto de entrada a toda la documentación |
| [Entrenamiento](docs/entrenamiento.md) | Plan, equipamiento, paralelas y coherencia de semanas |
| [Nutrición](docs/nutricion.md) | Calculadora, tracking y estimador de macros |
| [Catálogo](docs/catalogo.md) | Ejercicios por grupo y nivel |
| [Progresión](docs/progresion.md) | Series, reps, niveles y rotación |
| [Instalación](docs/instalacion.md) | `.deb`, código fuente y solución de problemas |

También: [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Código de conducta](CODE_OF_CONDUCT.md)

## En una frase

Aplicación modular para planificar y seguir **20 semanas** de entrenamiento doméstico con una pregunta central:

> *¿Estoy entrenando y alimentándome de forma coherente con mi objetivo?*

**Equipamiento típico:** mancuernas, banco, barra ligera, suelo, bici estática y paralelas *(opcional)*.

## Inicio rápido

### Desde código fuente

```bash
git clone https://github.com/entreunosyceros/sudoraciones-propias.git
cd sudoraciones-propias
python3 run_app.py
```

Abre `http://localhost:8508` (el launcher intenta abrir el navegador solo).

### Paquete `.deb`

```bash
wget https://github.com/entreunosyceros/sudoraciones-propias/releases/download/v1.4.1/sudoraciones_1.4.1_amd64.deb
sudo dpkg -i sudoraciones_1.4.1_amd64.deb
```

Más detalle en [Instalación](docs/instalacion.md).

## Qué incluye

- Plan de 20 semanas en 4 niveles, sesión de hoy y rotación (máx. 6 ejercicios por grupo)
- Calentamiento sugerido, biblioteca con **GIF o YouTube**, calendario y estadísticas
- Nutrición: TDEE, macros, tracking diario y estimador desde texto libre
- Equipamiento configurable en la barra lateral

Detalle completo: [Entrenamiento](docs/entrenamiento.md) · [Nutrición](docs/nutricion.md)

---

<img width="1079" height="1834" alt="sudoraciones-info" src="https://github.com/user-attachments/assets/f1f61266-dcaf-4ac7-9b84-cd4f6a9298f4" />

Desarrollado con Python, Streamlit, ☕ y 🚬 por [entreunosyceros](https://github.com/entreunosyceros).
