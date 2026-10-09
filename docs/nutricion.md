# Nutrición

> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)


## Resumen

>El cálculo de calorías y gasto energético son datos son estimados. Los gastos calóricos son **estimaciones**. Sin pulsómetro o wearable no se puede conocer el gasto real con precisión.

- **Calculadora de calorías y macros** (Mifflin-St Jeor) con objetivos según mantener, volumen o definición.
- **Gasto energético estimado** desglosado: metabolismo basal, actividad diaria y entrenamiento (~320 kcal/sesión).
- **Tracking diario** de comidas con progreso respecto a tus objetivos.
- **Estimación automática de macros** al describir lo que comes en texto libre (botón «Estimar macros automáticamente»).
- **Registro de peso** diario vinculado al perfil nutricional.
- **Indicadores semanales** que cruzan entrenamientos completados, calorías ingeridas, balance estimado y tendencia de peso.


## Estimador de alimentos

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


## Indicadores semanales

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


> **Documentación:** [Inicio](../README.md) · [Índice](README.md) · [Entrenamiento](entrenamiento.md) · [Nutrición](nutricion.md) · [Catálogo](catalogo.md) · [Progresión](progresion.md) · [Instalación](instalacion.md)

