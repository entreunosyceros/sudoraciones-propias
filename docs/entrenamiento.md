# Entrenamiento

> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)


## Perfil objetivo

**Entrenamiento doméstico con equipamiento básico** — pensado para una audiencia muy amplia:

- Mancuernas
- Banco de press
- Barra ligera (~30 kg)
- Espacio en el suelo
- Bicicleta estática
- Paralelas *(opcional, complemento de calistenia)*

En la **barra lateral** puedes indicar qué material tienes. El plan se adapta automáticamente: si no tienes paralelas, esos ejercicios no se programan.


## Funcionalidades de entrenamiento

<img width="1073" height="1829" alt="sudoraciones-biblioteca" src="https://github.com/user-attachments/assets/8a005daa-2f02-41b0-aa8c-cb20c3ffe9dd" />

- **Plan de 20 semanas** en 4 niveles de dificultad, con progresión automática de repeticiones, series, tiempos de plancha y distancia en bici.
- **Sesión de hoy** como vista principal: entrenamiento del día según el calendario del programa (no el selector manual).
- **Semana única visible:** la barra lateral muestra la semana de hoy vs. la del selector, con botones para alinearlas.
- **Rotación inteligente:** como máximo **6 ejercicios por grupo muscular y sesión**; cuando desbloqueas más, la app alterna cuáles salen según semana y día.
- **Cobertura del catálogo:** cuántos ejercicios de cada grupo has probado al menos una vez y cuáles quedan en rotación.
- **Calentamiento sugerido:** 2-3 ejercicios de la biblioteca según los grupos del día (opcional, no cuenta en el progreso; aunque siempre es recomendable calentar para evitar lesiones).
- **Avisos de nivel** al iniciar semanas 5, 9, 13 y 17 (series, frecuencia y ejercicios nuevos).
- **Equipamiento configurable** en la barra lateral: el plan solo programa ejercicios que puedes hacer con lo que tienes en casa.
- **Calendario de progreso** que respeta la fecha de inicio que elijas (sin forzar lunes).
- **Biblioteca de ejercicios** con filtros por grupo muscular y equipamiento.
- **Demostración GIF o YouTube:** si existe un GIF en `img/exercises/` se muestra solo el GIF; si no, el vídeo de YouTube (lista de nombres en `img/exercises/README.md`).
- **58 ejercicios en el plan** (42 principales + 16 complementos en paralelas 🪜).


## Complemento en paralelas (calistenia)

El entrenamiento principal se centra en **mancuernas, banco y suelo**. Las paralelas son opcionales y actúan como añadido dentro del **tope de 6 ejercicios por grupo y sesión**:

| Patrón | Ejercicios | Niveles |
|--------|-----------|---------|
| **Empuje** | Flexiones profundas, fondos inclinados/clásicos/de tríceps, pike push-ups, soporte isométrico | 1–3 |
| **Tirón** | Remo invertido clásico (neutro), supino, pies elevados, tuck australiano, encogimientos escapulares | 1–4 |
| **Core** | Elevaciones de rodillas, piernas estiradas, L-sit hold, L-sit a knee raise dinámico | 1–4 |

Si tienes paralelas (o dos sillas que puedan soportar tu peso) y hay calistenia desbloqueada para ese grupo, **1 de los 6 huecos de la sesión** se reserva para un ejercicio 🪜 rotativo (pecho, espalda, hombros, brazos, abs). El resto son ejercicios principales con peso o suelo.


## Equipamiento configurable

Archivo `user_settings.json`:

```json
{
  "available_equipment": {
    "mancuernas": true,
    "barra": true,
    "banco": true,
    "suelo": true,
    "bicicleta": true,
    "paralelas": false
  }
}
```

También editable desde la app (barra lateral). Si `paralelas` es `false`, fondos, remos invertidos y ejercicios de core en barras **no se programan**.


## Coherencia y claridad en el plan

La app distingue **tres referencias de semana**:

| Concepto | Qué es |
|----------|--------|
| **Semana de hoy** | La que marca tu calendario según la fecha de inicio del programa |
| **Semana del selector** | La que eliges para explorar o repasar otra semana |
| **Semana auto-detectada** | Inferida por tu progreso guardado |

### Vista del plan

| Modo | Uso |
|------|-----|
| **Hoy** (por defecto) | Sesión del día con la semana del calendario — la forma recomendada de entrenar |
| **Semana completa** | Todos los días de la semana del selector (repaso o adelanto) |

### Barra lateral

- Muestra la **semana de hoy** y si el selector está alineado.
- Botones **Semana de hoy** y **Auto-detectada** para sincronizar el selector.

### Avisos de cambio de nivel

En las semanas **5, 9, 13 y 17** aparece un banner con los cambios del nuevo nivel (series, días de entrenamiento, rotación) y los ejercicios recién desbloqueados.

### Cobertura del catálogo (rotación)

En cada sesión, un panel indica por grupo muscular:

- Cuántos ejercicios desbloqueados has hecho **al menos una vez** (ej. Pecho: 4/9).
- Cuáles tocan **hoy** en la rotación (máx. 6).
- Cuáles **aún no has probado** o saldrán en otras sesiones.


## Pestañas de la aplicación

- 🏋️ Plan de Entrenamiento — **sesión de hoy**, calentamiento sugerido, cobertura de rotación, marcar ejercicios
- 📊 Progreso — calendario mensual y vista semanal
- 📈 Estadísticas — métricas de entrenamiento e indicadores de coherencia
- 📚 Biblioteca de Ejercicios — catálogo con filtros (GIF o YouTube)
- 🍎 Nutrición — calculadora, tracking diario con estimador de macros, indicadores semanales
- ℹ️ Información — documentación del programa dentro de la app


> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)

