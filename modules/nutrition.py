"""
Módulo de Nutrición
Proporciona calculadoras de calorías, macros y tracking básico de comidas
"""
import streamlit as st
import json
import os
import datetime
from typing import Dict, Any, List
from .base_trainer import BaseTrainer
from .estimador_alimentos import EstimadorAlimentos
from .paths import NUTRITION_FILE


class NutritionModule(BaseTrainer):
    """Módulo para gestión de nutrición y tracking de comidas"""
    
    def __init__(self):
        super().__init__()
        self.nutrition_file = NUTRITION_FILE
        self.nutrition_data = self.load_nutrition_data()
        self.estimador_alimentos = EstimadorAlimentos(usar_open_food_facts=True)
    
    def load_nutrition_data(self) -> Dict[str, Any]:
        """Cargar datos de nutrición"""
        if os.path.exists(self.nutrition_file):
            try:
                with open(self.nutrition_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Datos por defecto
        return {
            'profile': {
                'age': None,
                'weight': None,
                'height': None,
                'sex': 'M',
                'activity_level': 'moderate',
                'goal': 'maintain'
            },
            'targets': {
                'calories': None,
                'protein_g': None,
                'carbs_g': None,
                'fat_g': None
            },
            'daily_logs': {},
            'weight_log': {}
        }
    
    def save_nutrition_data(self):
        """Guardar datos de nutrición"""
        try:
            with open(self.nutrition_file, 'w', encoding='utf-8') as f:
                json.dump(self.nutrition_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error guardando datos de nutrición: {e}")
    
    def calculate_bmr(self, weight: float, height: float, age: int, sex: str) -> float:
        """Calcular tasa metabólica basal usando Mifflin-St Jeor"""
        if sex == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # Female
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calcular gasto energético total diario estimado (sin sesión de entrenamiento extra)"""
        return self._calculate_tdee_from_bmr(bmr, activity_level)
    
    def _log_weight_entry(self, date_str: str, weight: float):
        """Registrar peso en el historial"""
        if 'weight_log' not in self.nutrition_data:
            self.nutrition_data['weight_log'] = {}
        self.nutrition_data['weight_log'][date_str] = weight
    
    def render_energy_estimate_panel(self, weight: float, height: float, age: int, sex: str, activity_level: str, is_training_day: bool = True):
        """Mostrar desglose de gasto energético estimado"""
        bmr = self.calculate_bmr(weight, height, age, sex)
        activity_kcal = self.estimate_daily_activity_kcal(bmr, activity_level)
        training_kcal = self.estimate_training_kcal() if is_training_day else 0
        total = bmr + activity_kcal + training_kcal

        st.markdown("### 🔥 Gasto energético estimado")
        st.caption(
            "Valores orientativos calculados con fórmulas estándar. "
            "Sin pulsómetro, smartwatch o banda de frecuencia cardíaca no es posible conocer el gasto real."
        )
        st.markdown(f"- **Metabolismo basal (estimado):** {bmr:.0f} kcal")
        st.markdown(f"- **Actividad diaria (estimada):** {activity_kcal:.0f} kcal")
        st.markdown(f"- **Entrenamiento (estimado):** {training_kcal:.0f} kcal")
        st.markdown(f"- **Total estimado:** {total:.0f} kcal")
    
    def calculate_macros(self, calories: float, goal: str) -> Dict[str, float]:
        """Calcular distribución de macronutrientes"""
        macro_distributions = {
            'maintain': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
            'bulk': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
            'cut': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30}
        }

        distribution = macro_distributions.get(goal, macro_distributions['maintain'])
        protein_g = (calories * distribution['protein']) / 4
        carbs_g = (calories * distribution['carbs']) / 4
        fat_g = (calories * distribution['fat']) / 9

        return {
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'fat_g': round(fat_g, 1)
        }

    def render_calculator_tab(self):
        """Renderizar pestaña de calculadora de calorías y macros"""
        st.markdown("## 🧮 Calculadora de Calorías y Macros")
        st.info(
            "Estimaciones basadas en la fórmula de Mifflin-St Jeor. "
            "Son orientativas: el gasto real varía según genética, sueño, estrés y composición corporal."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Información Personal")
            
            age = st.number_input("Edad (años)", min_value=15, max_value=100, value=self.nutrition_data['profile'].get('age') or 30)
            weight = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=float(self.nutrition_data['profile'].get('weight') or 70.0), step=0.5)
            height = st.number_input("Altura (cm)", min_value=100, max_value=250, value=self.nutrition_data['profile'].get('height') or 170)
            sex = st.radio("Sexo", ['M', 'F'], index=0 if self.nutrition_data['profile'].get('sex', 'M') == 'M' else 1, horizontal=True)
            
            st.markdown("### 🏃 Nivel de Actividad")
            activity_options = {
                'sedentary': 'Sedentario (poco o ningún ejercicio)',
                'light': 'Ligero (ejercicio 1-3 días/semana)',
                'moderate': 'Moderado (ejercicio 3-5 días/semana)',
                'active': 'Activo (ejercicio 6-7 días/semana)',
                'very_active': 'Muy Activo (ejercicio intenso diario)'
            }
            
            activity_level = st.selectbox(
                "Nivel de actividad",
                list(activity_options.keys()),
                index=list(activity_options.keys()).index(self.nutrition_data['profile'].get('activity_level', 'moderate')),
                format_func=lambda x: activity_options[x]
            )
            
            st.markdown("### 🎯 Objetivo")
            goal_options = {
                'maintain': 'Mantener peso',
                'bulk': 'Ganar masa muscular (volumen)',
                'cut': 'Perder grasa (definición)'
            }
            
            goal = st.selectbox(
                "Tu objetivo",
                list(goal_options.keys()),
                index=list(goal_options.keys()).index(self.nutrition_data['profile'].get('goal', 'maintain')),
                format_func=lambda x: goal_options[x]
            )
            
            if st.button("💾 Guardar Perfil", type="primary"):
                self.nutrition_data['profile'] = {
                    'age': age,
                    'weight': weight,
                    'height': height,
                    'sex': sex,
                    'activity_level': activity_level,
                    'goal': goal
                }
                self._log_weight_entry(datetime.date.today().strftime('%Y-%m-%d'), weight)
                self.save_nutrition_data()
                st.success("✅ Perfil guardado correctamente")
                st.rerun()
        
        with col2:
            st.markdown("### 📊 Resultados estimados")
            
            bmr = self.calculate_bmr(weight, height, age, sex)
            tdee = self.calculate_tdee(bmr, activity_level)
            
            if goal == 'bulk':
                target_calories = tdee + 300
            elif goal == 'cut':
                target_calories = tdee - 500
            else:
                target_calories = tdee
            
            macros = self.calculate_macros(target_calories, goal)

            self.render_energy_estimate_panel(weight, height, age, sex, activity_level, is_training_day=True)
            st.markdown("---")
            st.markdown(f"**TDEE estimado (sin extra de entrenamiento):** {tdee:.0f} kcal/día")
            
            st.markdown(f"### 🎯 Objetivo: {goal_options[goal]}")
            st.metric("Calorías diarias objetivo (estimadas)", f"{target_calories:.0f} kcal")
            
            st.markdown("### 🍽️ Distribución de Macronutrientes")
            
            col_p, col_c, col_f = st.columns(3)
            with col_p:
                protein_pct = (macros['protein_g'] * 4 / target_calories) * 100
                st.metric("Proteínas", f"{macros['protein_g']:.0f}g", f"{protein_pct:.0f}%")
            with col_c:
                carbs_pct = (macros['carbs_g'] * 4 / target_calories) * 100
                st.metric("Carbohidratos", f"{macros['carbs_g']:.0f}g", f"{carbs_pct:.0f}%")
            with col_f:
                fat_pct = (macros['fat_g'] * 9 / target_calories) * 100
                st.metric("Grasas", f"{macros['fat_g']:.0f}g", f"{fat_pct:.0f}%")
            
            # Guardar targets
            if st.button("✅ Establecer como Objetivos"):
                self.nutrition_data['targets'] = {
                    'calories': round(target_calories),
                    'protein_g': macros['protein_g'],
                    'carbs_g': macros['carbs_g'],
                    'fat_g': macros['fat_g']
                }
                self.save_nutrition_data()
                st.success("🎯 Objetivos nutricionales establecidos")
                st.rerun()
    
    def render_tracking_tab(self):
        """Renderizar pestaña de tracking diario"""
        st.markdown("## 📝 Tracking Diario")
        
        # Verificar si hay objetivos establecidos
        if not self.nutrition_data['targets'].get('calories'):
            st.warning("⚠️ Primero establece tus objetivos en la pestaña 'Calculadora'")
            return
        
        # Seleccionar fecha
        selected_date = st.date_input("Fecha", datetime.date.today())
        date_str = selected_date.strftime('%Y-%m-%d')

        profile = self.nutrition_data.get('profile', {})
        if all(profile.get(k) is not None for k in ('age', 'weight', 'height')):
            st.markdown("### ⚖️ Peso del día")
            weight_col1, weight_col2 = st.columns([2, 1])
            with weight_col1:
                daily_weight = st.number_input(
                    "Peso (kg)",
                    min_value=30.0,
                    max_value=200.0,
                    value=float(self.nutrition_data.get('weight_log', {}).get(date_str, profile.get('weight', 70.0))),
                    step=0.1,
                    key=f"daily_weight_{date_str}"
                )
            with weight_col2:
                if st.button("💾 Guardar peso", key=f"save_weight_{date_str}"):
                    self._log_weight_entry(date_str, daily_weight)
                    self.nutrition_data['profile']['weight'] = daily_weight
                    self.save_nutrition_data()
                    st.success("Peso registrado")
                    st.rerun()

            self.render_energy_estimate_panel(
                daily_weight,
                profile['height'],
                profile['age'],
                profile.get('sex', 'M'),
                profile.get('activity_level', 'moderate'),
                is_training_day=True,
            )
            st.markdown("---")
        
        # Panel de resumen diario
        daily_log = self.nutrition_data['daily_logs'].get(date_str, {'meals': [], 'total': {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}})
        
        # Mostrar progreso
        st.markdown("### 📊 Resumen del Día")
        targets = self.nutrition_data['targets']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cal_progress = (daily_log['total']['calories'] / targets['calories']) * 100
            st.metric("Calorías", f"{daily_log['total']['calories']:.0f}/{targets['calories']:.0f}", f"{cal_progress:.0f}%")
        with col2:
            prot_progress = (daily_log['total']['protein_g'] / targets['protein_g']) * 100
            st.metric("Proteínas", f"{daily_log['total']['protein_g']:.0f}g/{targets['protein_g']:.0f}g", f"{prot_progress:.0f}%")
        with col3:
            carb_progress = (daily_log['total']['carbs_g'] / targets['carbs_g']) * 100
            st.metric("Carbohidratos", f"{daily_log['total']['carbs_g']:.0f}g/{targets['carbs_g']:.0f}g", f"{carb_progress:.0f}%")
        with col4:
            fat_progress = (daily_log['total']['fat_g'] / targets['fat_g']) * 100
            st.metric("Grasas", f"{daily_log['total']['fat_g']:.0f}g/{targets['fat_g']:.0f}g", f"{fat_progress:.0f}%")
        
        # Barras de progreso
        st.progress(min(cal_progress / 100, 1.0), text=f"Calorías: {cal_progress:.0f}%")
        
        st.markdown("---")
        
        # Añadir comida
        st.markdown("### ➕ Añadir Comida")
        st.caption(
            "Describe lo que has comido (ej: «200 g pechuga de pollo con 180 g arroz») "
            "y pulsa **Estimar macros** para rellenar calorías y macronutrientes automáticamente."
        )

        defaults_key = f"macros_estimados_{date_str}"
        detalle_key = f"detalle_estimacion_{date_str}"
        defaults = st.session_state.get(defaults_key, {})

        descripcion_comida = st.text_area(
            "Descripción de la comida",
            value=defaults.get('nombre', ''),
            placeholder="Ej: 200 g pechuga de pollo con 180 g arroz blanco cocido",
            key=f"descripcion_comida_{date_str}",
            height=80,
        )

        col_estimar, col_limpiar = st.columns([2, 1])
        with col_estimar:
            if st.button("🔍 Estimar macros automáticamente", type="secondary", use_container_width=True):
                if not descripcion_comida.strip():
                    st.warning("Escribe qué has comido antes de estimar.")
                else:
                    resultado = self.estimador_alimentos.estimar(descripcion_comida)
                    st.session_state[defaults_key] = resultado.a_dict()
                    st.session_state[detalle_key] = resultado.a_dict()
                    st.rerun()
        with col_limpiar:
            if st.button("🧹 Limpiar estimación", use_container_width=True):
                st.session_state.pop(defaults_key, None)
                st.session_state.pop(detalle_key, None)
                st.rerun()

        if st.session_state.get(detalle_key):
            detalle = st.session_state[detalle_key]
            with st.expander("📋 Desglose de la estimación (orientativa)", expanded=True):
                for aviso in detalle.get('avisos', []):
                    st.caption(f"ℹ️ {aviso}")
                if detalle.get('detalles'):
                    for item in detalle['detalles']:
                        st.markdown(
                            f"- **{item['alimento']}** ({item['gramos']} g, {item['fuente']}): "
                            f"{item['calorias']} kcal · P {item['proteinas_g']} g · "
                            f"C {item['carbohidratos_g']} g · G {item['grasas_g']} g"
                        )
                else:
                    st.warning("No se pudo desglosar la comida. Prueba con más detalle o gramos.")

        with st.form("add_meal"):
            meal_name = st.text_input(
                "Nombre para el registro",
                value=defaults.get('nombre', descripcion_comida),
                placeholder="Ej: Comida mediodía — pollo con arroz",
            )

            col_cal, col_prot, col_carb, col_fat = st.columns(4)
            with col_cal:
                meal_calories = st.number_input(
                    "Calorías (estimadas)",
                    min_value=0,
                    value=int(defaults.get('calories', 0)),
                    step=10,
                )
            with col_prot:
                meal_protein = st.number_input(
                    "Proteínas (g)",
                    min_value=0.0,
                    value=float(defaults.get('protein_g', 0.0)),
                    step=0.5,
                )
            with col_carb:
                meal_carbs = st.number_input(
                    "Carbohidratos (g)",
                    min_value=0.0,
                    value=float(defaults.get('carbs_g', 0.0)),
                    step=0.5,
                )
            with col_fat:
                meal_fat = st.number_input(
                    "Grasas (g)",
                    min_value=0.0,
                    value=float(defaults.get('fat_g', 0.0)),
                    step=0.5,
                )

            submitted = st.form_submit_button("➕ Añadir comida al día")
            if submitted and meal_name:
                if date_str not in self.nutrition_data['daily_logs']:
                    self.nutrition_data['daily_logs'][date_str] = {
                        'meals': [],
                        'total': {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0},
                    }

                meal = {
                    'name': meal_name,
                    'calories': meal_calories,
                    'protein_g': meal_protein,
                    'carbs_g': meal_carbs,
                    'fat_g': meal_fat,
                    'timestamp': datetime.datetime.now().strftime('%H:%M'),
                    'estimado': bool(defaults),
                }

                self.nutrition_data['daily_logs'][date_str]['meals'].append(meal)
                self.nutrition_data['daily_logs'][date_str]['total']['calories'] += meal_calories
                self.nutrition_data['daily_logs'][date_str]['total']['protein_g'] += meal_protein
                self.nutrition_data['daily_logs'][date_str]['total']['carbs_g'] += meal_carbs
                self.nutrition_data['daily_logs'][date_str]['total']['fat_g'] += meal_fat

                st.session_state.pop(defaults_key, None)
                st.session_state.pop(detalle_key, None)
                self.save_nutrition_data()
                st.success(f"✅ «{meal_name}» añadida al registro del día")
                st.rerun()
            elif submitted and not meal_name:
                st.error("Indica un nombre para la comida.")
        
        # Mostrar comidas del día
        st.markdown("### 🍽️ Comidas Registradas")
        if daily_log['meals']:
            for idx, meal in enumerate(daily_log['meals']):
                etiqueta_estimado = " · estimado" if meal.get('estimado') else ""
                with st.expander(f"{meal['timestamp']} — {meal['name']} ({meal['calories']} kcal{etiqueta_estimado})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"🥩 Proteínas: {meal['protein_g']}g")
                    with col2:
                        st.write(f"🍞 Carbohidratos: {meal['carbs_g']}g")
                    with col3:
                        st.write(f"🥑 Grasas: {meal['fat_g']}g")
                    
                    if st.button(f"🗑️ Eliminar", key=f"delete_meal_{idx}"):
                        # Restar del total
                        self.nutrition_data['daily_logs'][date_str]['total']['calories'] -= meal['calories']
                        self.nutrition_data['daily_logs'][date_str]['total']['protein_g'] -= meal['protein_g']
                        self.nutrition_data['daily_logs'][date_str]['total']['carbs_g'] -= meal['carbs_g']
                        self.nutrition_data['daily_logs'][date_str]['total']['fat_g'] -= meal['fat_g']
                        
                        # Eliminar comida
                        self.nutrition_data['daily_logs'][date_str]['meals'].pop(idx)
                        self.save_nutrition_data()
                        st.rerun()
        else:
            st.info("No hay comidas registradas para este día")

    def render_weekly_summary_tab(self):
        """Indicadores semanales de coherencia entre entrenamiento y nutrición"""
        st.markdown("## 📅 Indicadores Semanales")
        st.caption(
            "Resumen orientativo para responder: "
            "«¿Estoy entrenando y alimentándome de forma coherente con mi objetivo?»"
        )

        week_number = st.number_input(
            "Semana del programa",
            min_value=1,
            max_value=20,
            value=int(st.session_state.get('current_week', 1)),
            step=1,
        )
        summary = self.get_weekly_coherence_summary(int(week_number))

        st.markdown(f"### Semana {summary['week_number']}")

        col1, col2 = st.columns(2)
        with col1:
            planned = summary['training_planned']
            completed = summary['training_completed']
            st.metric("Entrenamientos completados", f"{completed}/{planned}" if planned else "—")
        with col2:
            if summary['avg_calories'] is not None:
                st.metric("Calorías medias ingeridas", f"{summary['avg_calories']:.0f} kcal")
            else:
                st.metric("Calorías medias ingeridas", "Sin registros")

        col3, col4 = st.columns(2)
        with col3:
            if summary['avg_balance'] is not None:
                sign = "+" if summary['avg_balance'] > 0 else ""
                st.metric("Balance medio estimado", f"{sign}{summary['avg_balance']:.0f} kcal/día")
            else:
                st.metric("Balance medio estimado", "Sin datos")
        with col4:
            if summary['weight_start'] is not None and summary['weight_end'] is not None:
                st.metric(
                    "Peso",
                    f"{summary['weight_start']:.1f} → {summary['weight_end']:.1f} kg",
                    f"{summary['weight_delta']:+.1f} kg" if summary['weight_delta'] is not None else None,
                )
            elif summary['weight_end'] is not None:
                st.metric("Peso actual (perfil)", f"{summary['weight_end']:.1f} kg")
            else:
                st.metric("Peso", "Sin registros")

        st.info(f"**Tendencia:** {summary['trend']}")

        if not summary['has_profile']:
            st.warning("Completa tu perfil en la calculadora para estimar balance energético.")
        elif summary['calorie_days'] == 0:
            st.warning("Registra comidas en Tracking Diario para calcular balance y calorías medias.")

        if summary['estimated_bmr']:
            with st.expander("🔥 Detalle del gasto energético estimado"):
                st.markdown(f"- Metabolismo basal (estimado): **{summary['estimated_bmr']} kcal**")
                st.markdown(f"- Actividad diaria (estimada): **{summary['estimated_activity_kcal']} kcal**")
                st.markdown(f"- Entrenamiento por sesión (estimado): **{summary['estimated_training_kcal']} kcal**")
                st.caption("Estimaciones sin pulsómetro ni wearable. Úsalas como referencia, no como verdad absoluta.")
    
    def render_nutrition_tab(self):
        """Renderizar pestaña completa de nutrición"""
        tab1, tab2, tab3 = st.tabs(["🧮 Calculadora", "📝 Tracking Diario", "📅 Indicadores Semanales"])
        
        with tab1:
            self.render_calculator_tab()
        
        with tab2:
            self.render_tracking_tab()

        with tab3:
            self.render_weekly_summary_tab()
