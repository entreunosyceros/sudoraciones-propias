# 💪 Sudoraciones propias 💪

<img width="1066" height="1832" alt="sudoraciones-portada" src="https://github.com/user-attachments/assets/c59911ed-bbee-4a42-bbb3-f6e6433536ec" />

Sistema personal de entrenamiento en Python + Streamlit con progresión automática, calendario de progreso y módulo de nutrición.

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

Aplicación modular para planificar y seguir entrenamientos durante 20 semanas. Todo gira en torno a una pregunta:

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

- **Plan de 20 semanas** en 4 niveles de dificultad, con progresión automática.
- **Equipamiento configurable** en la barra lateral: el plan solo programa ejercicios que puedes hacer con lo que tienes en casa.
- **Calendario de progreso** que respeta la fecha de inicio que elijas (sin forzar lunes).
- **Biblioteca de ejercicios** con filtros por grupo muscular y equipamiento.
- **58 ejercicios en el plan** (42 principales + 16 complementos en paralelas 🪜).

### Nutrición

- **Calculadora de calorías y macros** (Mifflin-St Jeor) con objetivos según mantener, volumen o definición.
- **Gasto energético estimado** desglosado: metabolismo basal, actividad diaria y entrenamiento (~320 kcal/sesión).
- **Tracking diario** de comidas con progreso respecto a tus objetivos.
- **Estimación automática de macros** al describir lo que comes en texto libre (botón «Estimar macros automáticamente»).
- **Registro de peso** diario vinculado al perfil nutricional.
- **Indicadores semanales** que cruzan entrenamientos completados, calorías ingeridas, balance estimado y tendencia de peso.

Los gastos calóricos son **estimaciones**. Sin pulsómetro o wearable no se puede conocer el gasto real con precisión.

### Estimador de alimentos

<img width="1079" height="1835" alt="sudoraciones-nutricion" src="https://github.com/user-attachments/assets/112ea7a7-ed42-4685-b34d-e86aa7aac3c5" />

Al registrar una comida en **Tracking Diario**, describe lo que has comido en lenguaje natural. El sistema:

1. **Reconoce ingredientes** contra la base local `data/alimentos_es.json` (~135 alimentos).
2. **Parsea cantidades** en gramos (`200 g`), unidades (`2 huevos`, `3 claras`), cucharadas (`1 cucharada de azúcar`), latas (`1 lata coca-cola`), litros/ml/cl, o usa la ración típica si no indicas cantidad.
3. **Separa platos compuestos** con `+`, `,`, `y` o `con` (ej: «pechuga de pollo con arroz»).
4. **Consulta Open Food Facts** como respaldo si un alimento no está en la base local (requiere conexión).
5. **Muestra un desglose orientativo** editable antes de guardar; las comidas estimadas quedan marcadas como tales.

**Ejemplos de descripción:**

- `200 g pechuga de pollo con 180 g arroz blanco cocido`
- `ensaladilla rusa, 2 huevos y pan integral`
- `hamburguesa de pollo, cocacola y ensalada mixta`
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
| Bebidas | Agua, zumo natural/comprado, coca-cola, té helado, tónica, batido de frutas, café, sidra |
| Otros | Fruta, membrillo, frutos secos, batido de proteínas, tofu |

Para ampliar la base, edita `data/alimentos_es.json` (campos: `nombre`, `aliases`, `por_100g`, `racion_tipica_g`).

## Complemento en paralelas (calistenia)

El entrenamiento principal sigue centrado en **mancuernas, banco y suelo**. Las paralelas son opcionales y actúan como añadido:

| Patrón | Ejercicios | Niveles |
|--------|-----------|---------|
| **Empuje** | Flexiones profundas, fondos inclinados/clásicos/de tríceps, pike push-ups, soporte isométrico | 1–3 |
| **Tirón** | Remo invertido clásico (neutro), supino, pies elevados, tuck australiano, encogimientos escapulares | 1–4 |
| **Core** | Elevaciones de rodillas, piernas estiradas, L-sit hold, L-sit a knee raise dinámico | 1–4 |

En el plan semanal aparece **1 ejercicio de calistenia rotativo** por sesión de cada grupo (pecho, espalda, hombros, brazos, abs). Los ejercicios marcados con 🪜 en el catálogo siguiente son ese complemento.

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

El plan dura **20 semanas** repartidas en **4 niveles**. Cada nivel desbloquea ejercicios nuevos; los anteriores se mantienen en la rutina. En cada sesión se realizan **todos los ejercicios principales** desbloqueados del grupo muscular, más **como máximo 1 ejercicio en paralelas** (🪜) rotando entre los disponibles.

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

> A partir de la semana 5 el calendario rota variaciones del ciclo base con más frecuencia de abdominales y cardio según el nivel.

---

### 🫸 Pecho (9 ejercicios)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Press de Banca con Mancuernas | 6-8 | Mancuernas |
| 1 | Flexiones de Pecho | 8-12 | Suelo |
| 1 | 🪜 Flexiones Profundas (Deficit Push-ups) | 8-12 | Paralelas |
| 2 | Press de Banca con Barra | 6-8 | Banco/barra |
| 2 | Aperturas con Mancuernas | 8-10 | Mancuernas |
| 2 | 🪜 Fondos con Torso Inclinado | 6-10 | Paralelas |
| 3 | Press Inclinado con Barra | 8-10 | Banco/barra |
| 3 | 🪜 Fondos Clásicos (Dips) | 6-8 | Paralelas |
| 4 | Flexiones con Mancuernas | 8-12 | Mancuernas |

---

### 🔙 Espalda (10 ejercicios)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Remo con Mancuernas | 8-10 | Mancuernas |
| 1 | Remo Inclinado con Mancuernas | 8-10 | Mancuernas |
| 1 | 🪜 Remo Invertido Clásico (Agarre Neutro) | 10-12 | Paralelas |
| 1 | 🪜 Encogimientos Escapulares en Inversión | 10-15 | Paralelas |
| 2 | Peso Muerto con Mancuernas | 8-10 | Mancuernas |
| 2 | 🪜 Remo Invertido Supino (Enfoque Dorsal y Bíceps) | 8-12 | Paralelas |
| 3 | Remo con Barra | 6-8 | Banco/barra |
| 3 | 🪜 Remo Invertido con Pies Elevados | 6-10 | Paralelas |
| 4 | Peso Muerto con Barra | 6-8 | Banco/barra |
| 4 | 🪜 Remo Australiano en Tuck (Pies Suspendidos) | 5-8 | Paralelas |

---

### 🤷 Hombros (7 ejercicios)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Press Militar con Mancuernas | 6-8 | Mancuernas |
| 1 | Elevaciones Laterales | 8-10 | Mancuernas |
| 2 | Elevaciones Frontales | 8-12 | Mancuernas |
| 2 | 🪜 Flexiones de Pica (Pike Push-ups) | 8-12 | Paralelas |
| 3 | Press Arnold | 8-10 | Mancuernas |
| 3 | 🪜 Soporte Isométrico (Soporte de Fondos) | 20-40 s | Paralelas |
| 4 | Elevaciones Posteriores | 10-12 | Mancuernas |

---

### 💪 Brazos (10 ejercicios)

Incluye trabajo de bíceps, tríceps y antebrazos. Los ejercicios de antebrazo rotan en el plan (1 por sesión).

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Curl de Bíceps | 6-8 | Mancuerna 12 kg |
| 1 | Extensiones de Tríceps | 8-10 | Mancuernas |
| 1 | Curl de Muñeca *(antebrazo)* | 8-10 | Mancuernas |
| 1 | 🪜 Flexiones de Tríceps (Agarre Neutro) | 8-12 | Paralelas |
| 2 | Curl Martillo | 8-10 | Mancuernas |
| 2 | Fondos en Silla | 6-12 | Banco |
| 2 | Curl de Muñeca Inverso *(antebrazo)* | 8-10 | Mancuernas |
| 2 | 🪜 Fondos con Enfoque en Tríceps | 6-10 | Paralelas |
| 3 | Pronación/Supinación con Mancuerna *(antebrazo)* | 8-10 | Mancuernas |
| 4 | Curl 21s | 21 (7+7+7) | Mancuernas |

---

### 🦵 Piernas (5 ejercicios)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Sentadillas con Mancuernas | 10-12 | Mancuernas |
| 1 | Sentadillas Sin Peso | 12-15 | Suelo |
| 2 | Zancadas con Mancuernas | 8-10/pierna | Mancuernas |
| 3 | Sentadillas Búlgaras | 8-10/pierna | Mancuernas |
| 4 | Sentadillas Pistol (Asistidas) | 5-8/pierna | Suelo |

---

### 🦶 Gemelos (5 ejercicios)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Elevaciones de Gemelos de Pie | 15-20 | Mancuernas |
| 1 | Elevaciones de Gemelos Sin Peso | 20-25 | Suelo |
| 2 | Elevaciones de Gemelos Sentado | 12-15 | Mancuernas |
| 3 | Elevaciones de Gemelos a Una Pierna | 8-12/pierna | Mancuernas |
| 4 | Saltos de Gemelos | 15-20 | Suelo |

---

### 🔥 Abdominales (11 ejercicios)

Combina ejercicios de suelo con complementos en paralelas (abs avanzados integrados en sesiones de abs).

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Abdominales Tradicionales | 15-20 | Suelo |
| 1 | Plancha | 30-60 s | Suelo |
| 1 | 🪜 Elevaciones de Rodillas en Paralelas | 10-15 | Paralelas |
| 2 | Plancha Lateral | 20-40 s/lado | Suelo |
| 2 | Abdominales Bajas | 12-15 | Suelo |
| 3 | Abdominales Laterales | 10-12/lado | Suelo |
| 3 | 🪜 Elevaciones de Piernas Estiradas en Paralelas | 8-12 | Paralelas |
| 4 | Plancha con Elevación de Brazos | 10-15/brazo | Suelo |
| 4 | V-Ups | 8-12 | Suelo |
| 4 | 🪜 L-Sit Hold en Paralelas | 10-20 s | Paralelas |
| 4 | 🪜 L-Sit a Knee Raise Dinámico | 6-10 | Paralelas |

---

### 🏃 Cardio (1 ejercicio)

| Nivel | Ejercicio | Reps | Equipo |
|-------|-----------|------|--------|
| 1 | Bicicleta Estática | 20 km | Bici estática |

---

### Ejercicios auxiliares (Biblioteca)

Disponibles en la pestaña **Biblioteca de Ejercicios** para calentamiento, estiramiento y movilidad. No forman parte del plan semanal principal, pero puedes usarlos libremente:

- **Calentamiento (8):** rotaciones de hombros, encogimientos escapulares en inversión, círculos de caderas, rotaciones de cuello/brazos, balanceo de piernas, elevaciones de rodillas, jumping jacks suaves.
- **Estiramiento (10):** pectorales, dorsales, hombros, tríceps, isquiotibiales, cuádriceps, gemelos, glúteos, cadera, espalda baja.
- **Movilidad (8):** gato-camello, bird dog, 90/90 hip switch, rotaciones torácicas, dislocaciones de hombro, círculos de tobillo, sentadilla profunda, world's greatest stretch.

---

**Total en plan de entrenamiento:** 58 ejercicios (42 principales + 16 complementos en paralelas 🪜).

## Progresión de entrenamiento

### Niveles (20 semanas)

- **Nivel 1 (Semanas 1-4):** adaptación inicial.
- **Nivel 2 (Semanas 5-8):** incremento de frecuencia.
- **Nivel 3 (Semanas 9-12):** incremento de volumen.
- **Nivel 4+ (Semanas 13-20):** plan avanzado.

### Frecuencia de abdominales por nivel

- **Nivel 1:** 2 días/semana
- **Nivel 2:** 3 días/semana
- **Nivel 3:** 4 días/semana
- **Nivel 4+:** 5 días/semana

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

- 🏋️ Plan de Entrenamiento — sesión del día, marcar ejercicios completados
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

Desarrollado con Python y Streamlit por entreunosyceros.
