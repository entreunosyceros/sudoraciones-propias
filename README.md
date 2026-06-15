# 💪 Sudoraciones propias 💪

<img width="1066" height="1832" alt="sudoraciones-portada" src="https://github.com/user-attachments/assets/c59911ed-bbee-4a42-bbb3-f6e6433536ec" />

Sistema personal de entrenamiento en **Python 3.12+** y Streamlit con progresión automática, calendario de progreso y módulo de nutrición... Esto está hecho por un motivo en particular ... pero si a alguien le sirve ... 

## Perfil objetivo

**Entrenamiento doméstico con equipamiento básico** — pensado para una audiencia muy amplia:

- Mancuernas
- Banco de press
- Barra ligera (~30 kg)
- Espacio en el suelo
- Bicicleta estática
- Paralelas *(opcional, complemento de calistenia)*

En la **barra lateral** puedes indicar qué material tienes. El plan se adapta automáticamente: si no tienes paralelas, esos ejercicios no se programan.

## Descripción

Aplicación modular para planificar y seguir entrenamientos durante 20 semanas (5 meses). Todo gira en torno a una pregunta:

> *¿Estoy entrenando y alimentándome de forma coherente con mi objetivo?*

Incluye:

- Plan semanal por niveles (adaptado a tu equipamiento)
- Seguimiento por ejercicio y por día
- Calendario y estadísticas con indicadores semanales
- Biblioteca de ejercicios con videos
- Complemento opcional en paralelas (calistenia)
- Módulo de nutrición con calculadora, tracking diario y estimación automática de macros
- Base local de alimentos en español + respaldo Open Food Facts

## Funcionalidades principales

### Entrenamiento

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
- **58 ejercicios en el plan** (42 principales + 16 complementos en paralelas 🪜).

### Nutrición

>El cálculo de calorías y gasto energético son datos son estimados. Los gastos calóricos son **estimaciones**. Sin pulsómetro o wearable no se puede conocer el gasto real con precisión.

- **Calculadora de calorías y macros** (Mifflin-St Jeor) con objetivos según mantener, volumen o definición.
- **Gasto energético estimado** desglosado: metabolismo basal, actividad diaria y entrenamiento (~320 kcal/sesión).
- **Tracking diario** de comidas con progreso respecto a tus objetivos.
- **Estimación automática de macros** al describir lo que comes en texto libre (botón «Estimar macros automáticamente»).
- **Registro de peso** diario vinculado al perfil nutricional.
- **Indicadores semanales** que cruzan entrenamientos completados, calorías ingeridas, balance estimado y tendencia de peso.

### Estimador de alimentos

<img width="1079" height="1835" alt="sudoraciones-nutricion" src="https://github.com/user-attachments/assets/112ea7a7-ed42-4685-b34d-e86aa7aac3c5" />

Al registrar una comida en **Tracking Diario**, describe lo que has comido en lenguaje natural. El sistema:

1. **Reconoce ingredientes** contra la base local `data/alimentos_es.json` (**148 alimentos**, incl. frutas de temporada: naranja, fresas, kiwi, mandarina, pera, melocotón, sandía, melón, arándanos…).
2. **Parsea cantidades** en gramos (`200 g`), unidades (`2 huevos`, `3 claras`), cucharadas (`1 cucharada de azúcar`), latas (`1 lata coca-cola`), litros/ml/cl, o usa la ración típica si no indicas cantidad.
3. **Separa platos compuestos** con `+`, `,`, `y` o `con` (ej: «pechuga de pollo con arroz»).
4. **Consulta Open Food Facts** como respaldo si un alimento no está en la base local (requiere conexión).
5. **Muestra un desglose orientativo** editable antes de guardar; las comidas estimadas quedan marcadas como tales.

**Ejemplos de descripción:**

- `200 g pechuga de pollo con 180 g arroz blanco cocido`
- `ensaladilla rusa, 2 huevos y pan integral`
- `hamburguesa de pollo, coca-cola y ensalada mixta`
- `rapante a la plancha con guisantes y patata`
- `yogur natural, galletas integrales y café solo`
- `bizcocho de limón y tónica`
- `fabada asturiana` (usa ración típica si no pones gramos)

**Categorías cubiertas en la base local:**

| Categoría | Ejemplos |
|-----------|----------|
| Proteínas | Pollo, pescado, marisco, ternera, cerdo, huevos, claras, jamón, bacon, hamburguesas, albóndigas, chuletas |
| Pescado gallego | Merluza, bacalao, pulpo, rapante (gallo/meiga), zamburiñas, berberechos |
| Carbohidratos | Arroz, pasta, pan, patata, empanada, pizza |
| Legumbres y guisos | Lentejas, garbanzos, fabada, habas, guisantes, cocido, caldo gallego |
| Verduras y ensaladas | Grelos, brócoli, tomate, cebolla, lechuga, zanahoria, aceitunas, ensaladilla rusa |
| Platos preparados | Tortilla de patatas, pulpo a la gallega, lacón con grelos, cachopo, lasaña |
| Salsas y aliños | Mayonesa, alioli, ketchup, tomate frito, salsa barbacoa, salsa de soja, aceite de oliva |
| Especias | Pimentón dulce, orégano |
| Lácteos y postres | Yogur natural, quesos gallegos/asturianos, queso batido 0%, filloas, tarta de Santiago, bizcocho, galletas de canela, galletas integrales |
| Bebidas | Agua, zumo natural/comprado, coca-cola, té helado, tónica, batido de frutas, café, sidra, cerveza, shandy, vino |
| Fruta | Manzana, plátano, naranja, fresas, kiwi, mandarina, pera, melocotón, sandía, melón, arándanos |
| Otros | Membrillo, frutos secos, batido de proteínas, tofu |

Para ampliar la base, edita `data/alimentos_es.json` (campos: `nombre`, `aliases`, `por_100g`, `racion_tipica_g`).

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

## Nutrición e indicadores semanales

Pestaña **🍎 Nutrición** con tres subpestañas:

| Subpestaña | Qué hace |
|------------|----------|
| **Calculadora** | Perfil (edad, peso, altura, actividad, objetivo), TDEE estimado y distribución de macros |
| **Tracking Diario** | Registro de comidas, estimación automática de macros, progreso del día |
| **Indicadores Semanales** | Coherencia entre entrenamiento, ingesta y peso por semana del programa |

Indicadores semanales de ejemplo:

- Entrenamientos completados: 5/5
- Calorías medias ingeridas
- Balance medio estimado (kcal/día)
- Peso: tendencia semanal
- Veredicto: «Pérdida de peso consistente», «Peso estable», etc.

La pestaña **📈 Estadísticas** también muestra un resumen de coherencia semanal.

## Catálogo completo de ejercicios del programa

El plan dura **20 semanas** repartidas en **4 niveles**. Cada nivel desbloquea ejercicios nuevos; los anteriores siguen en el catálogo pero **no salen todos a la vez** en cada sesión.

**Regla de sesión:** como máximo **6 ejercicios por grupo muscular** ya que si cuidas la técnica, eso ya es un buen rato de ejercicio. Si hay más desbloqueados, la app **rota** la selección según semana y día para que vayas cubriendo todo el repertorio sin sesiones eternas.

| Nivel | Ejemplo pecho (aprox.) | Ejemplo brazos (aprox.) |
|-------|------------------------|-------------------------|
| 1 | 3 ejercicios (todos los desbloqueados) | 4 (bíceps, tríceps, antebrazo, calistenia) |
| 2 | 5 (4 principales + 1 🪜) | 6 (tope: alterna antebrazo y calistenia) |
| 3 | 6 (tope: 5 principales + 1 🪜) | 6 (rota entre curl 21s, antebrazos, etc.) |
| 4+ | 6 (rota entre press, flexiones, fondos…) | 6 (rota bíceps/tríceps/antebrazo/calistenia) |

Las tablas del catálogo listan **todo lo desbloqueable** por nivel, no necesariamente lo que verás el mismo día. 

Las tablas siguientes muestran **repeticiones de referencia en la semana 1** del programa (rangos de fuerza típicos: **9-10**). A partir de ahí la app ajusta automáticamente series/reps/tiempos según la semana y el nivel (ver [Progresión de entrenamiento](#progresión-de-entrenamiento)).

**Equipamiento del programa:** mancuernas (8 kg, 10 kg y 12 kg), banco con barra (30 kg), bicicleta estática, espacio en el suelo y, opcionalmente, paralelas.

### Estructura semanal base (ciclo de 4 semanas)

| Día | Grupos musculares |
|-----|-------------------|
| Lunes | Pecho, espalda, abdominales |
| Martes | Descanso |
| Miércoles | Piernas, gemelos, cardio |
| Jueves | Descanso |
| Viernes | Brazos, hombros, cardio, abdominales |
| Sábado | Pecho, brazos |
| Domingo | Descanso |

> A partir de la semana 5 el calendario rota variaciones del ciclo base con más frecuencia de abdominales y cardio según el nivel. Los ejercicios dentro de cada sesión también rotan cuando el catálogo del grupo supera 6.

---

### 🫸 Pecho (9 en catálogo · hasta 6 por sesión)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Press de Banca con Mancuernas | 9-10 | Mancuernas |
| 1 | Flexiones de Pecho | 9-10 | Suelo |
| 1 | 🪜 Flexiones Profundas (Deficit Push-ups) | 9-10 | Paralelas |
| 2 | Press de Banca con Barra | 9-10 | Banco/barra |
| 2 | Aperturas con Mancuernas | 9-10 | Mancuernas |
| 2 | 🪜 Fondos con Torso Inclinado | 9-10 | Paralelas |
| 3 | Press Inclinado con Barra | 9-10 | Banco/barra |
| 3 | 🪜 Fondos Clásicos (Dips) | 9-10 | Paralelas |
| 4 | Flexiones con Mancuernas | 9-10 | Mancuernas |

---

### 🔙 Espalda (10 en catálogo · hasta 6 por sesión)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Remo con Mancuernas | 9-10 | Mancuernas |
| 1 | Remo Inclinado con Mancuernas | 9-10 | Mancuernas |
| 1 | 🪜 Remo Invertido Clásico (Agarre Neutro) | 9-10 | Paralelas |
| 1 | 🪜 Encogimientos Escapulares en Inversión | 10-15 | Paralelas |
| 2 | Peso Muerto con Mancuernas | 9-10 | Mancuernas |
| 2 | 🪜 Remo Invertido Supino (Enfoque Dorsal y Bíceps) | 9-10 | Paralelas |
| 3 | Remo con Barra | 9-10 | Banco/barra |
| 3 | 🪜 Remo Invertido con Pies Elevados | 9-10 | Paralelas |
| 4 | Peso Muerto con Barra | 9-10 | Banco/barra |
| 4 | 🪜 Remo Australiano en Tuck (Pies Suspendidos) | 9-10 | Paralelas |

---

### 🤷 Hombros (7 en catálogo · hasta 6 por sesión)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Press Militar con Mancuernas | 9-10 | Mancuernas |
| 1 | Elevaciones Laterales | 9-10 | Mancuernas |
| 2 | Elevaciones Frontales | 9-10 | Mancuernas |
| 2 | 🪜 Flexiones de Pica (Pike Push-ups) | 9-10 | Paralelas |
| 3 | Press Arnold | 9-10 | Mancuernas |
| 3 | 🪜 Soporte Isométrico (Soporte de Fondos) | 20-40 s | Paralelas |
| 4 | Elevaciones Posteriores | 9-10 | Mancuernas |

---

### 💪 Brazos (10 en catálogo · hasta 6 por sesión)

Incluye bíceps, tríceps y antebrazos. **1 antebrazo por sesión** (rotativo) dentro del tope de 6; el resto alterna bíceps/tríceps y, si aplica, 1 calistenia 🪜.

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Curl de Bíceps | 9-10 | Mancuerna 12 kg |
| 1 | Extensiones de Tríceps | 9-10 | Mancuernas |
| 1 | Curl de Muñeca *(antebrazo)* | 9-10 | Mancuernas |
| 1 | 🪜 Flexiones de Tríceps (Agarre Neutro) | 9-10 | Paralelas |
| 2 | Curl Martillo | 9-10 | Mancuernas |
| 2 | Fondos en Silla | 9-10 | Banco |
| 2 | Curl de Muñeca Inverso *(antebrazo)* | 9-10 | Mancuernas |
| 2 | 🪜 Fondos con Enfoque en Tríceps | 9-10 | Paralelas |
| 3 | Pronación/Supinación con Mancuerna *(antebrazo)* | 9-10 | Mancuernas |
| 4 | Curl 21s | 21 (7+7+7) | Mancuernas |

---

### 🦵 Piernas (5 ejercicios)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Sentadillas con Mancuernas | 9-10 | Mancuernas |
| 1 | Sentadillas Sin Peso | 12-15 | Suelo |
| 2 | Zancadas con Mancuernas | 9-10/pierna | Mancuernas |
| 3 | Sentadillas Búlgaras | 9-10/pierna | Mancuernas |
| 4 | Sentadillas Pistol (Asistidas) | 9-10/pierna | Suelo |

---

### 🦶 Gemelos (5 ejercicios)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Elevaciones de Gemelos de Pie | 15-20 | Mancuernas |
| 1 | Elevaciones de Gemelos Sin Peso | 20-25 | Suelo |
| 2 | Elevaciones de Gemelos Sentado | 12-15 | Mancuernas |
| 3 | Elevaciones de Gemelos a Una Pierna | 8-12/pierna | Mancuernas |
| 4 | Saltos de Gemelos | 15-20 | Suelo |

---

### 🔥 Abdominales (11 en catálogo · hasta 6 por sesión)

Combina suelo y paralelas (abs avanzados integrados en sesiones de abs). En niveles altos rota planchas, abdominales y ejercicios 🪜.

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Abdominales Tradicionales | 15-20 | Suelo |
| 1 | Plancha | 30-60 s | Suelo |
| 1 | 🪜 Elevaciones de Rodillas en Paralelas | 10-15 | Paralelas |
| 2 | Plancha Lateral | 20-40 s/lado | Suelo |
| 2 | Abdominales Bajas | 12-15 | Suelo |
| 3 | Abdominales Laterales | 10-12/lado | Suelo |
| 3 | 🪜 Elevaciones de Piernas Estiradas en Paralelas | 9-10 | Paralelas |
| 4 | Plancha con Elevación de Brazos | 10-15/brazo | Suelo |
| 4 | V-Ups | 9-10 | Suelo |
| 4 | 🪜 L-Sit Hold en Paralelas | 10-20 s | Paralelas |
| 4 | 🪜 L-Sit a Knee Raise Dinámico | 9-10 | Paralelas |

---

### 🏃 Cardio (1 ejercicio)

| Nivel | Ejercicio | Reps (sem. 1) | Equipo |
|-------|-----------|---------------|--------|
| 1 | Bicicleta Estática | 15 km | Bici estática |

---

### Ejercicios auxiliares (Biblioteca)

Disponibles en la pestaña **Biblioteca de Ejercicios** para calentamiento, estiramiento y movilidad:

- **Calentamiento (8):** rotaciones de hombros, encogimientos escapulares en inversión, círculos de caderas, rotaciones de cuello/brazos, balanceo de piernas, elevaciones de rodillas, jumping jacks suaves.  
  → El plan sugiere **2-3 por sesión** según los grupos del día (no cuentan en el progreso).
- **Estiramiento (10):** pectorales, dorsales, hombros, tríceps, isquiotibiales, cuádriceps, gemelos, glúteos, cadera, espalda baja.
- **Movilidad (8):** gato-camello, bird dog, 90/90 hip switch, rotaciones torácicas, dislocaciones de hombro, círculos de tobillo, sentadilla profunda, world's greatest stretch.

---

**Total en plan de entrenamiento:** 58 ejercicios (42 principales + 16 complementos en paralelas 🪜).

## Progresión de entrenamiento

La app calcula **series y repeticiones visibles** en el plan, la biblioteca y las estadísticas según la semana del programa. Punto de partida en **semana 1** para rangos de fuerza habituales: **9-10 repeticiones** y **3 series** (nivel 1).

### Reglas automáticas

| Tipo | Semana 1 | Series por nivel | Progresión de reps |
|------|----------|------------------|-------------------|
| **Fuerza** (tope ≤ 12 reps en plantilla) | 9-10 | N1: **3** · N2: **4** · N3: **5** · N4+: **6** | N1-2: +1 rep/semana del ciclo y +2/nivel; N3+: reps fijas en 9-10 (o plantilla) |
| **Planchas** | 30-60 s (según ejercicio) | 3 / 4 / 5 / 6 series | +10 s por cada cambio de nivel |
| **Bicicleta** | 15 km (niveles 1-2) | 1 sesión | 20 km desde nivel 3 |
| **Alto volumen** (> 12 reps: gemelos, abdominales…) | Valor de plantilla | 3 / 4 / 5 / 6 series | N1-2: +1 rep/semana y +2/nivel; N3+: reps fijas |
| **Curl 21s, tiempos auxiliares** | Sin cambio automático | 3 / 4 / 5 / 6 series | Valor fijo de plantilla |

### Niveles (20 semanas)

- **Nivel 1 (Semanas 1-4):** adaptación inicial — **3 series**, reps 9-10 en fuerza, +1 rep por semana del ciclo.
- **Nivel 2 (Semanas 5-8):** incremento de frecuencia — **4 series**, +2 reps respecto al punto de partida del nivel 1.
- **Nivel 3 (Semanas 9-12):** incremento de volumen — **5 series**, reps de fuerza se mantienen en 9-10 (sin más subidas de reps).
- **Nivel 4+ (Semanas 13-20):** plan avanzado — **6 series**, reps de fuerza estables.

### Frecuencia de abdominales por nivel

- **Nivel 1:** 2 días/semana
- **Nivel 2:** 3 días/semana
- **Nivel 3:** 4 días/semana
- **Nivel 4+:** 5 días/semana

### Rotación por grupo muscular

La app aplica estas reglas al montar cada sesión del plan:

| Regla | Detalle |
|-------|---------|
| **Tope** | 6 ejercicios por grupo muscular y sesión |
| **Niveles bajos** | Si hay ≤ 6 desbloqueados, se muestran todos |
| **Niveles altos** | Ventana rotativa según **semana del programa + día de la semana + grupo** |
| **Calistenia 🪜** | Reserva 1 hueco dentro del tope cuando hay paralelas y ejercicios desbloqueados |
| **Brazos** | 1 antebrazo rotativo por sesión; el resto completa hasta 6 |
| **Cardio** | Siempre 1 ejercicio (bicicleta) |

**Ejemplo nivel 4 — pecho un viernes vs un sábado:** la combinación de press, flexiones y fondos cambia; no repites los mismos 9 del catálogo en una sola sesión.

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

## Instalación (.deb)

```bash
wget https://github.com/sapoclay/sudoraciones-propias/releases/download/v1.4.0/sudoraciones_1.4.0_amd64.deb
sudo dpkg -i sudoraciones_1.4.0_amd64.deb
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

## Pestañas de la aplicación

- 🏋️ Plan de Entrenamiento — **sesión de hoy**, calentamiento sugerido, cobertura de rotación, marcar ejercicios
- 📊 Progreso — calendario mensual y vista semanal
- 📈 Estadísticas — métricas de entrenamiento e indicadores de coherencia
- 📚 Biblioteca de Ejercicios — catálogo con filtros y videos
- 🍎 Nutrición — calculadora, tracking diario con estimador de macros, indicadores semanales
- ℹ️ Información — documentación del programa dentro de la app

## Estructura principal

```text
data/
└── alimentos_es.json          # Base local de alimentos (español)

modules/
├── __init__.py
├── base_trainer.py            # Planificación, equipamiento, coherencia semanal
├── estimador_alimentos.py     # Parser y estimación de macros desde texto
├── exercise_library.py
├── info.py
├── nutrition.py
├── progress_calendar.py
├── statistics.py
└── training_plan.py
```

Archivos clave:

- `main_app.py`: aplicación principal
- `run_app.py`: launcher
- `config.json`: configuración de ejercicios y plan
- `user_settings.json`: equipamiento disponible del usuario
- `progress_data.json`: progreso del usuario
- `nutrition_data.json`: perfil nutricional, comidas diarias y registro de peso

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

---

<img width="1079" height="1834" alt="sudoraciones-info" src="https://github.com/user-attachments/assets/f1f61266-dcaf-4ac7-9b84-cd4f6a9298f4" />

Desarrollado con Python, Streamlit, ☕ y 🚬 por entreunosyceros.
