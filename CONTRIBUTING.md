# Guía de contribución

¡Gracias por interesarte en **Sudoraciones propias**! Este proyecto es software libre (GPL-3.0) pensado para entrenamiento doméstico y seguimiento nutricional. Cualquier mejora bien planteada es bienvenida.

## Antes de empezar

- Lee el [README](README.md) para entender el alcance del proyecto.
- Revisa [issues abiertas](https://github.com/sapoclay/sudoraciones-propias/issues) por si alguien ya trabaja en lo mismo.
- Para dudas de comportamiento en la comunidad, consulta el [Código de conducta](CODE_OF_CONDUCT.md).

## Cómo puedes ayudar

- **Reportar errores** con pasos claros para reproducirlos.
- **Proponer mejoras** explicando el problema que resuelven.
- **Enviar pull requests** con cambios acotados y probados.
- **Mejorar documentación** (README, comentarios, textos de la app).
- **Ampliar la base de alimentos** en `data/alimentos_es.json` (nombre, aliases, macros por 100 g, ración típica).

## Entorno de desarrollo

Requisitos: **Python 3.12+** y navegador moderno.

```bash
git clone https://github.com/sapoclay/sudoraciones-propias.git
cd sudoraciones-propias
python3 -m venv venv_sudoraciones
source venv_sudoraciones/bin/activate
pip install -r requirements.txt
python3 run_app.py
```

La app queda disponible en `http://localhost:8508`.

### Instalación con `.deb` (opcional)

Si pruebas el empaquetado Debian:

```bash
bash packaging/build_deb.sh
sudo dpkg -i sudoraciones_1.4.0_amd64.deb
sudoraciones start
```

## Estilo de código

- Sigue el estilo del código existente (nombres, imports, nivel de comentarios).
- Cambios **mínimos y enfocados**: no mezcles varias funcionalidades en un mismo PR.
- Los textos visibles para el usuario van en **español**.
- No incluyas secretos, rutas personales ni datos reales de progreso en los commits.

## Pull requests

1. Crea una rama descriptiva desde `main` (por ejemplo `fix/calendario-semana-1`).
2. Describe **qué** cambias y **por qué**.
3. Indica cómo lo has probado (pasos manuales o capturas si aplica).
4. Si tocas nutrición o entrenamiento, menciona el impacto en usuarios con datos guardados (`progress_data.json`, `config.json`).
5. Actualiza el README solo si el cambio lo requiere.

Usa la [plantilla de pull request](.github/pull_request_template.md) al abrir el PR.

## Reportar problemas de seguridad

No abras issues públicas para vulnerabilidades. Sigue la [política de seguridad](SECURITY.md).

## Licencia

Al contribuir, aceptas que tu aportación se publique bajo la misma licencia del proyecto: [GPL-3.0](LICENSE).
