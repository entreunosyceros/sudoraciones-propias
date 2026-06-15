# Política de seguridad

## Versiones con soporte

| Versión | Soportada |
| ------- | --------- |
| 1.4.x   | ✅        |
| < 1.4   | ❌        |

## Alcance

Este proyecto es una aplicación **local/personal** (Streamlit) para planificación de entrenamiento y nutrición. En el ámbito de seguridad nos interesa especialmente:

- Ejecución de código o comandos no previstos a través de entradas de usuario.
- Lectura o escritura de archivos fuera de las rutas previstas de la aplicación.
- Exposición involuntaria de datos personales (progreso, nutrición, peso) entre usuarios o en red.
- Dependencias con vulnerabilidades conocidas que afecten al entorno de ejecución.
- Empaquetado `.deb` o scripts de instalación que alteren el sistema de forma insegura.

**Fuera de alcance habitual:** recomendaciones médicas o deportivas, precisión nutricional de terceros (Open Food Facts) o la seguridad de YouTube/vídeos externos embebidos.

## Cómo reportar una vulnerabilidad

1. **No** abras un issue público con detalles del fallo.
2. Usa [GitHub Security Advisories](https://github.com/sapoclay/sudoraciones-propias/security/advisories/new) (**Report a vulnerability**) si tienes acceso.
3. Si no puedes usar Advisories, abre un issue con título `SECURITY (sin detalles)` y pide un canal privado; no incluyas pasos de explotación en público.

Incluye, en la medida de lo posible:

- Descripción del problema y componente afectado.
- Pasos para reproducirlo.
- Impacto estimado (local, red, datos del usuario).
- Versión o commit afectado.
- Sugerencia de mitigación, si la tienes.

## Qué esperar

- **Acuse de recibo** en un plazo razonable (habitualmente en pocos días).
- Evaluación del informe y, si procede, parche o mitigación en una versión posterior.
- Crédito al informante en las notas de la corrección, salvo que prefiera anonimato.

## Buenas prácticas para usuarios

- Ejecuta la app en entornos de confianza; por defecto escucha en `8508`.
- No compartas `progress_data.json`, `nutrition_data.json` ni `user_settings.json` si contienen datos personales.
- Mantén Python y las dependencias actualizadas (`pip install -r requirements.txt --upgrade`).
- Descarga releases y paquetes `.deb` solo desde [releases oficiales](https://github.com/sapoclay/sudoraciones-propias/releases) del repositorio.
