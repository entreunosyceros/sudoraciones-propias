"""
Módulo de Información
Contiene toda la lógica de la pestaña de información
"""
import json
import os
import streamlit as st
from .base_trainer import BaseTrainer


class InfoModule(BaseTrainer):
    """Módulo para gestionar la información"""

    MUSCLE_GROUP_LABELS = {
        'pecho': 'Pecho',
        'espalda': 'Espalda',
        'hombros': 'Hombros',
        'brazos': 'Brazos',
        'piernas': 'Piernas',
        'gemelos': 'Gemelos',
        'abs': 'Abdominales',
        'abs_avanzados': 'Abdominales avanzados',
        'cardio': 'Cardio',
        'calentamiento': 'Calentamiento',
        'estiramiento': 'Estiramiento',
        'movilidad': 'Movilidad',
    }

    LEVEL_NAMES = {
        1: 'Principiante',
        2: 'Intermedio',
        3: 'Avanzado',
        4: 'Experto',
    }

    CALISTHENICS_SECTIONS = (
        ('empuje', '🏋️ Patrón de Empuje (Pecho, Tríceps, Hombros)', {'pecho', 'hombros', 'brazos'}),
        ('tiron', '⚓ Patrón de Tirón (Espalda y Bíceps)', {'espalda'}),
        ('core', '🧠 Core y Abdominales', {'abs', 'abs_avanzados'}),
    )

    def _get_training_group_counts(self) -> dict[str, int]:
        """Contar ejercicios por grupo muscular de entrenamiento"""
        training_groups = ['pecho', 'espalda', 'hombros', 'brazos', 'piernas', 'gemelos', 'abs', 'abs_avanzados', 'cardio']
        exercises = self.config.get('exercises', {})
        return {group: len(exercises.get(group, [])) for group in training_groups if exercises.get(group)}

    def _get_parallel_bars_exercises(self) -> list[dict]:
        """Obtener todos los ejercicios en paralelas con metadatos de grupo"""
        rows = []
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            for exercise in exercises:
                if exercise.get('equipment') == 'parallel_bars':
                    rows.append({
                        'muscle_group': muscle_group,
                        'name': exercise.get('name', ''),
                        'level': exercise.get('difficulty_level', 1),
                        'description': exercise.get('description', ''),
                        'reps': exercise.get('reps', ''),
                    })
        return rows

    def _get_food_database_count(self) -> int:
        """Contar alimentos en la base local"""
        ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'alimentos_es.json')
        if not os.path.exists(ruta):
            return 0
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return len(json.load(f).get('alimentos', []))
        except (json.JSONDecodeError, OSError):
            return 0

    def _render_nutrition_documentation(self):
        """Documentar el módulo de nutrición y estimador de alimentos"""
        food_count = self._get_food_database_count()
        st.subheader("🍎 Nutrición y estimador de alimentos")
        st.markdown(f"""
        La pestaña **Nutrición** responde junto al entrenamiento a la pregunta central del programa.
        Todo el gasto calórico es **estimado** (Mifflin-St Jeor + actividad + ~320 kcal/sesión);
        sin pulsómetro o wearable no es posible conocer el gasto real.

        #### Subpestañas

        | Subpestaña | Contenido |
        |------------|-----------|
        | **Calculadora** | Perfil, TDEE, objetivos de calorías y macros (mantener / volumen / definición) |
        | **Tracking Diario** | Registro de comidas, barra de progreso del día, estimación automática de macros |
        | **Indicadores Semanales** | Entrenamientos vs plan, calorías medias, balance estimado y tendencia de peso |

        #### Estimación automática de macros

        En **Tracking Diario**, describe lo que has comido y pulsa **Estimar macros automáticamente**:

        - Base local **`data/alimentos_es.json`** con **{food_count} alimentos** en español
        - Respaldo **Open Food Facts** si un alimento no está en la base (requiere internet)
        - Cantidades en gramos (`200 g`), unidades (`2 huevos`) o ración típica por defecto
        - Platos compuestos separados con `+`, `,`, `y` o `con`
        - Desglose editable antes de guardar; comidas estimadas quedan marcadas

        **Ejemplos:** «200 g pechuga de pollo con arroz», «ensaladilla y pan», «hamburguesa de cerdo con cocacola»

        #### Categorías en la base local

        Proteínas (pollo, pescado, marisco, cerdo, hamburguesas, albóndigas, chuletas…),
        carbohidratos (arroz, pasta, pan, patata…), legumbres (lentejas, garbanzos, fabada, habas…),
        verduras y ensaladas (incl. ensaladilla rusa), platos preparados gallegos y del norte,
        salsas, lácteos, postres, bebidas (agua, zumos, refrescos, té helado, batidos…) y más.
        """)

        st.caption(
            "Para añadir alimentos, edita data/alimentos_es.json "
            "(nombre, aliases, por_100g, racion_tipica_g)."
        )

    def _render_calisthenics_documentation(self):
        """Documentar el complemento de calistenia en paralelas"""
        parallel_exercises = self._get_parallel_bars_exercises()
        if not parallel_exercises:
            return

        st.subheader("🪜 Complemento en Paralelas (Calistenia)")
        st.markdown("""
        Las paralelas son un **añadido opcional** al entrenamiento principal con mancuernas y banco.
        No sustituyen tu plan base: en cada sesión se mantiene el trabajo con peso y se incluye
        **como máximo 1 ejercicio de calistenia** por grupo muscular, rotando entre los disponibles
        según tu nivel desbloqueado.
        """)

        for _, title, groups in self.CALISTHENICS_SECTIONS:
            section_exercises = [
                ex for ex in parallel_exercises
                if ex['muscle_group'] in groups and not (
                    ex['muscle_group'] == 'espalda' and ex['name'] == 'Encogimientos Escapulares en Inversión'
                )
            ]
            if not section_exercises:
                continue

            st.markdown(f"#### {title}")
            for exercise in sorted(section_exercises, key=lambda x: (x['level'], x['name'])):
                level_name = self.LEVEL_NAMES.get(exercise['level'], f"Nivel {exercise['level']}")
                st.markdown(
                    f"- **{exercise['name']}** — *{level_name}* ({exercise['reps']})\n"
                    f"  {exercise['description']}"
                )

        warmup_scapular = [
            ex for ex in parallel_exercises
            if ex['muscle_group'] == 'calentamiento'
        ]
        if warmup_scapular:
            st.markdown("#### 🔥 Calentamiento y Accesorios")
            for exercise in warmup_scapular:
                st.markdown(
                    f"- **{exercise['name']}** — *Disponible en cualquier nivel* ({exercise['reps']})\n"
                    f"  {exercise['description']}"
                )
            st.caption(
                "También disponible como complemento rotativo en sesiones de espalda."
            )

        unique_count = len({ex['name'] for ex in parallel_exercises})
        st.info(
            f"**{unique_count} ejercicios** en paralelas integrados en el programa. "
            "Consúltalos todos en la pestaña **Biblioteca de Ejercicios** filtrando por equipamiento «Paralelas»."
        )

    def render_info_tab(self):
        """Renderizar pestaña de información"""
        # Logo al principio de la pestaña
        if os.path.exists("img/logo.png"):
            st.image("img/logo.png", width=200)
        
        st.header("ℹ️ Información del Programa")
        
        st.markdown("""
        ## 🏠 Perfil objetivo
        
        **Entrenamiento doméstico con equipamiento básico.** Pensado para quien entrena en casa
        con material accesible y quiere seguimiento de progreso y nutrición sin complicaciones.
        
        | Material | Rol |
        |----------|-----|
        | Mancuernas | Entrenamiento principal |
        | Banco + barra ligera | Press, remo, peso muerto |
        | Suelo | Flexiones, sentadillas, core |
        | Bicicleta estática | Cardio |
        | Paralelas *(opcional)* | Complemento de calistenia |
        
        Configura lo que tienes en la **barra lateral → Tu equipamiento**. El plan se adapta:
        si no marcas paralelas, esos ejercicios no se programan.
        
        ---
        
        ## 🎯 Pregunta central del programa
        
        *«¿Estoy entrenando y alimentándome de forma coherente con mi objetivo?»*
        
        Plan de entrenamiento, seguimiento, calendario, estadísticas, nutrición e indicadores
        semanales giran en torno a esa pregunta. Los gastos calóricos son **estimaciones** —
        sin pulsómetro o wearable no es posible conocer el gasto real con precisión.
        """)
        
        # Título y descripción principal
        st.markdown("""
        ## 💪 **SUDORACIONES - Sistema de Entrenamiento Personal**
        
        **Un programa de entrenamiento inteligente diseñado para maximizar tus resultados con equipamiento básico.**
        
        Este sistema está optimizado para personas que quieren entrenar desde casa con mancuernas,
        banco y equipamiento mínimo, con un **complemento opcional en paralelas** para variedad y progresión
        en calistenia, pero con resultados efectivos y seguimiento profesional.
        """)
        
        # Crear columnas para la información principal
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.subheader("💡 Características Principales")
            total_exercises = self.get_total_exercises_count()
            food_count = self._get_food_database_count()
            st.markdown(f"""
            - **Plan Optimizado**: {total_exercises} ejercicios especializados
            - **Seguimiento Automático**: Progreso basado en completado
            - **Calendario Dinámico**: Visualización de entrenamiento mensual
            - **Videos Integrados**: Tutoriales YouTube y Shorts
            - **Sistema de Niveles**: Progresión automática inteligente
            - **Nutrición integrada**: Calculadora, tracking y estimador de macros
            - **Base de alimentos**: {food_count} alimentos en español + Open Food Facts
            """)
        
        with col2:
            st.subheader("📅 Estructura del Programa")
            total_exercises = self.get_total_exercises_count()
            st.markdown(f"""
            - **Progresión automática**: 4 niveles de dificultad
            - **20 semanas** de entrenamiento continuo
            - **{total_exercises} ejercicios** en 8 grupos musculares especializados
            - **Adaptación inteligente** según el progreso
            - **Sistema de niveles** desde principiante a experto
            """)
            
            st.subheader("🎯 Sistema de Progresión")
            st.markdown("""
            - **Nivel 1**: Principiante (Semanas 1-4)
            - **Nivel 2**: Intermedio (Semanas 5-8)
            - **Nivel 3**: Avanzado (Semanas 9-12)
            - **Nivel 4**: Experto (Semanas 13-20)
            """)

        # Equipamiento necesario
        st.subheader("🏋️ Equipamiento Necesario")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            ### Equipamiento Básico:
            - **2 Mancuernas de 10kg**
            - **1 Mancuerna de 12kg**
            - **1 Banco de press (30kg)**
            - **1 Bicicleta estática**
            - **Espacio en el suelo**
            """)
            st.markdown("""
            ### Complemento opcional:
            - **1 Par de paralelas** — calistenia integrada como añadido (máx. 1 ejercicio/sesión)
            """)
        
        with col4:
            st.markdown("""
            ### Ventajas del Sistema:
            - ✅ **Mínimo equipamiento requerido**
            - ✅ **Entrenamiento principal con peso**
            - ✅ **Calistenia opcional en paralelas**
            - ✅ **Entrenamiento desde casa**
            - ✅ **Seguimiento automático**
            - ✅ **Videos instructivos incluidos**
            """)

        # Principios de entrenamiento
        st.subheader("⚡ Principios de Entrenamiento")
        
        principles_col1, principles_col2 = st.columns(2)
        
        with principles_col1:
            st.markdown("""
            ### 🔥 Metodología
            - **Intensidad**: Alta intensidad hasta el fallo muscular
            - **Frecuencia**: 3-4 entrenamientos por semana
            - **Descanso**: 3-5 minutos entre series
            - **Progresión**: Incremento gradual de peso o repeticiones
            """)
        
        with principles_col2:
            st.markdown("""
            ### 📈 Seguimiento
            - **Registro automático** de ejercicios completados
            - **Estadísticas detalladas** de progreso
            - **Calendario visual** con porcentajes de completado
            - **Indicadores semanales** de coherencia entrenamiento + nutrición
            - **Registro de peso** y tracking de comidas diario
            """)

        # Grupos musculares trabajados
        st.subheader("💪 Grupos Musculares Trabajados")

        group_counts = self._get_training_group_counts()
        abs_total = group_counts.get('abs', 0) + group_counts.get('abs_avanzados', 0)
        parallel_count = len({ex['name'] for ex in self._get_parallel_bars_exercises()})
        
        muscle_col1, muscle_col2, muscle_col3 = st.columns(3)
        
        with muscle_col1:
            st.markdown(f"""
            **Tren Superior:**
            - 🫸 Pecho ({group_counts.get('pecho', 0)} ejercicios)
            - 🔙 Espalda ({group_counts.get('espalda', 0)} ejercicios)
            - 🤷 Hombros ({group_counts.get('hombros', 0)} ejercicios)
            - 💪 Brazos ({group_counts.get('brazos', 0)} ejercicios con antebrazos)
            """)
        
        with muscle_col2:
            st.markdown(f"""
            **Tren Inferior:**
            - 🦵 Piernas ({group_counts.get('piernas', 0)} ejercicios)
            - 🦶 Gemelos ({group_counts.get('gemelos', 0)} ejercicios)
            - 🏃 Cardio ({group_counts.get('cardio', 0)} ejercicio)
            """)
        
        with muscle_col3:
            st.markdown(f"""
            **Core y Abs:**
            - 🔥 Abdominales ({abs_total} ejercicios)
            - 🪜 Paralelas ({parallel_count} ejercicios de complemento)
            - 💪 Trabajo de core completo
            """)

        self._render_calisthenics_documentation()

        self._render_nutrition_documentation()

        # Estadísticas del programa
        st.subheader("📊 Estadísticas del Programa")
        
        if hasattr(self, 'config') and self.config:
            # Estadísticas de ejercicios
            exercise_stats = {}
            for muscle_group, exercises in self.config.get('exercises', {}).items():
                exercise_stats[muscle_group] = len(exercises)
            
            if exercise_stats:
                for group, count in exercise_stats.items():
                    label = self.MUSCLE_GROUP_LABELS.get(group, group.title())
                    st.markdown(f"- **{label}**: {count} ejercicios")
            
            # Estadísticas generales
            total_exercises = sum(len(exercises) for exercises in self.config.get('exercises', {}).values())
            base_weeks = len(self.config.get('weekly_schedule', {}))
            total_weeks = base_weeks * 5  # 4 semanas base × 5 ciclos = 20 semanas totales
            
            # Contar ejercicios con video
            exercises_with_video = sum(1 for muscle_group, exercises in self.config.get('exercises', {}).items() 
                                     for exercise in exercises if exercise.get('youtube_url'))
            
            st.markdown(f"""
            ### 📈 Resumen General:
            - **Total de ejercicios**: {total_exercises}
            - **Ejercicios con video**: {exercises_with_video}/{total_exercises}
            - **Semanas programadas**: {total_weeks} (ciclo de {base_weeks} semanas × 5)
            - **Cobertura de video**: {(exercises_with_video/total_exercises*100):.1f}%
            """)
