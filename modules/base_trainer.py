"""
Módulo base del entrenamiento
Contiene la funcionalidad core del sistema
"""
import json
import os
import datetime
import hashlib
import shutil
from typing import Dict, List, Any
import streamlit as st

from .paths import (
    CONFIG_FILE,
    NUTRITION_FILE,
    PROGRESS_BACKUP_FILE,
    PROGRESS_FILE,
    USER_SETTINGS_FILE,
    app_path,
)


class BaseTrainer:
    """Clase base con funcionalidad core del sistema"""

    USER_SETTINGS_FILE = USER_SETTINGS_FILE

    DEFAULT_USER_EQUIPMENT = {
        'mancuernas': True,
        'barra': True,
        'banco': True,
        'suelo': True,
        'bicicleta': True,
        'paralelas': True,
    }

    USER_EQUIPMENT_LABELS = {
        'mancuernas': 'Mancuernas',
        'barra': 'Barra ligera (30 kg)',
        'banco': 'Banco de press',
        'suelo': 'Espacio en el suelo',
        'bicicleta': 'Bicicleta estática',
        'paralelas': 'Paralelas (opcional)',
    }

    BENCH_ONLY_EXERCISES = {'Fondos en Silla'}
    BAR_ONLY_EXERCISES = {'Peso Muerto con Barra'}
    BAR_BENCH_EXERCISES = {
        'Press de Banca con Barra',
        'Press Inclinado con Barra',
        'Remo con Barra',
    }

    ESTIMATED_TRAINING_KCAL_PER_SESSION = 320
    
    def __init__(self):
        """Inicializar la aplicación"""
        self.config = self.load_config()
        self.progress_data = self.load_progress_data()
        self.user_settings = self.load_user_settings()
        
        # Configurar estado de sesión con auto-detección de semana
        if 'current_week' not in st.session_state:
            # Auto-detectar la semana actual basada en el progreso
            auto_week = self.get_auto_detected_week()
            st.session_state.current_week = auto_week
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = 0
        
        # Inicializar sistema de mapeo calendario si no existe
        self.initialize_calendar_mapping()
        
        # Invalidar cache para asegurar datos frescos
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
    
    def get_auto_detected_week(self) -> int:
        """Auto-detectar la semana de entrenamiento actual basada en el progreso del usuario"""
        # Si no hay datos de progreso, empezar en semana 1
        if not self.progress_data.get('completed_exercises'):
            return 1
        
        # Buscar la semana más alta con progreso + 1 (la siguiente no completada)
        max_week_with_progress = 0
        
        for date_str, exercises in self.progress_data.get('completed_exercises', {}).items():
            for exercise_id, is_completed in exercises.items():
                if is_completed and '_week' in exercise_id:
                    # Extraer número de semana del ID del ejercicio
                    try:
                        week_part = exercise_id.split('_week')[-1]
                        week_number = int(week_part)
                        max_week_with_progress = max(max_week_with_progress, week_number)
                    except (IndexError, ValueError):
                        continue
        
        # Si hay progreso, verificar si la semana más alta está completada
        if max_week_with_progress > 0:
            # Verificar completado de la semana más alta encontrada
            week_stats = self.get_week_completion_stats_for_week(max_week_with_progress)
            
            if week_stats['percentage'] >= 80:  # Si está mayormente completada
                # Avanzar a la siguiente semana (máximo 20)
                return min(max_week_with_progress + 1, 20)
            else:
                # Continuar en la semana actual en progreso
                return max_week_with_progress
        
        # Si no hay progreso significativo, empezar en semana 1
        return 1
    
    def get_week_completion_stats_for_week(self, week_number: int) -> Dict[str, Any]:
        """Obtener estadísticas de completado para una semana específica"""
        # Obtener fechas de la semana
        week_dates = self.get_week_dates(week_number)
        if not week_dates or 'dates' not in week_dates:
            return {'percentage': 0, 'completed_days': 0, 'total_days': 0}
        
        total_training_days = 0
        completed_training_days = 0
        
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for date_str in week_dates['dates']:
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                day_key = day_names[date_obj.weekday()]
            except ValueError:
                continue
            
            # Verificar si es día de entrenamiento según el nivel
            week_info = self.get_week_info(week_number)
            training_days = week_info.get('days', [])
            
            if day_key in training_days:
                total_training_days += 1
                
                # Verificar si el día está completado
                day_stats = self.get_day_completion_stats_internal(date_str, week_number)
                if day_stats.get('percentage', 0) >= 80:  # Día considerado completado
                    completed_training_days += 1
        
        percentage = (completed_training_days / total_training_days * 100) if total_training_days > 0 else 0
        
        return {
            'percentage': percentage,
            'completed_days': completed_training_days,
            'total_days': total_training_days
        }
    
    def check_and_advance_week_automatically(self):
        """Verificar si la semana actual está completa y avanzar automáticamente"""
        current_week = st.session_state.get('current_week', 1)
        
        # No avanzar si ya estamos en la semana 20 (última)
        if current_week >= 20:
            return False
            
        # Calcular completado de la semana actual
        completion_stats = self.get_week_completion_stats()
        
        # Si está 100% completada, avanzar automáticamente
        if completion_stats['percentage'] >= 100:
            new_week = current_week + 1
            st.session_state.current_week = new_week
            
            # Mostrar mensaje de celebración
            st.success(f"🎉 ¡Semana {current_week} completada! Avanzando automáticamente a la Semana {new_week}")
            st.balloons()
            return True
        
        return False
    
    def get_week_completion_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de completado de la semana actual"""
        current_week = st.session_state.get('current_week', 1)
        
        # Obtener últimos 7 días
        today = datetime.datetime.now()
        week_start = today - datetime.timedelta(days=6)
        
        total_planned = 0
        total_completed = 0
        
        for i in range(7):
            check_date = week_start + datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            
            # Obtener ejercicios de esa fecha para la semana actual
            if date_str in self.progress_data.get('completed_exercises', {}):
                day_exercises = self.progress_data['completed_exercises'][date_str]
                week_suffix = f"_week{current_week}"
                
                # Filtrar solo ejercicios de la semana actual
                week_exercises = {k: v for k, v in day_exercises.items() if k.endswith(week_suffix)}
                
                if week_exercises:
                    total_planned += len(week_exercises)
                    total_completed += sum(1 for completed in week_exercises.values() if completed)
        
        percentage = (total_completed / total_planned * 100) if total_planned > 0 else 0
        
        return {
            'total_planned': total_planned,
            'total_completed': total_completed,
            'percentage': percentage,
            'week': current_week
        }
    
    # --- NUEVO: Utilidades para alternar antebrazos y progresión por nivel ---
    def _get_forearm_exercises(self) -> list[dict]:
        exercises = self.config.get('exercises', {}).get('brazos', [])
        return [e for e in exercises if e.get('category') == 'forearm']
    
    def _choose_forearm_exercise_name(self, day_key: str, week_number: int) -> str | None:
        forearms = self._get_forearm_exercises()
        if not forearms:
            return None
        # Rotación determinística por semana y día (0=lun..6=dom)
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_idx = day_names.index(day_key) if day_key in day_names else 0
        idx = ((week_number - 1) * 7 + day_idx) % len(forearms)
        return forearms[idx]['name']
    
    def _get_level_for_week(self, week_number: int) -> int:
        info = self.get_week_info(week_number)
        return info.get('level', 1)
    
    def get_forearm_progression(self, level: int) -> tuple[int, str]:
        """Progresión para antebrazos según nivel"""
        if level <= 1:
            return 1, '8-10'
        if level == 2:
            return 1, '10-12'
        if level == 3:
            return 2, '10-12'
        # nivel 4+
        return 2, '12-15'
    
    def get_planned_exercises_for_group(self, muscle_group: str, day_key: str, week_number: int) -> list[dict]:
        """Devolver ejercicios planificados aplicando progresión por nivel, alternancia de antebrazos y calistenia como complemento"""
        all_ex = self.config.get('exercises', {}).get(muscle_group, [])

        if muscle_group == 'abs':
            all_ex = all_ex + self.config.get('exercises', {}).get('abs_avanzados', [])
        
        # Obtener el nivel actual basado en la semana
        current_level = (week_number - 1) // 4 + 1
        
        # Filtrar ejercicios por nivel de dificultad (incluye ejercicios del nivel actual y anteriores)
        available_exercises = self._filter_exercises_by_level(all_ex, current_level)
        available_exercises = self.filter_exercises_by_equipment(available_exercises)
        primary, calisthenics = self._split_primary_and_calisthenics(available_exercises)
        
        if muscle_group == 'brazos':
            # En brazos: incluir todos los ejercicios principales, alternar antebrazos y añadir calistenia
            non_forearm = [e for e in primary if e.get('category') != 'forearm']
            forearm_exercises = [e for e in primary if e.get('category') == 'forearm']
            chosen = self._choose_forearm_exercise_by_level(day_key, week_number, forearm_exercises)
            result = non_forearm + ([chosen] if chosen else [])
            return self._append_calisthenics_bonus(result, calisthenics, muscle_group, day_key, week_number)
        
        elif muscle_group == 'piernas':
            return self._append_calisthenics_bonus(
                self._get_planned_leg_exercises(day_key, week_number, primary),
                calisthenics, muscle_group, day_key, week_number
            )
        
        else:
            return self._append_calisthenics_bonus(primary, calisthenics, muscle_group, day_key, week_number)
    
    def _split_primary_and_calisthenics(self, exercises: list[dict]) -> tuple[list[dict], list[dict]]:
        """Separar ejercicios principales (peso/suelo) de complementos de calistenia en paralelas"""
        primary = [e for e in exercises if e.get('category') != 'calisthenics']
        calisthenics = [e for e in exercises if e.get('category') == 'calisthenics']
        return primary, calisthenics

    def _choose_calisthenics_exercise(self, calisthenics: list[dict], muscle_group: str, day_key: str, week_number: int) -> dict | None:
        """Elegir un ejercicio de calistenia rotativo como complemento (máximo uno por sesión)"""
        if not calisthenics:
            return None

        calisthenics = sorted(calisthenics, key=lambda x: x.get('difficulty_level', 1))

        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_idx = day_names.index(day_key) if day_key in day_names else 0
        group_offset = sum(ord(c) for c in muscle_group) % 7
        rotation_index = ((week_number - 1) * 7 + day_idx + group_offset) % len(calisthenics)

        return calisthenics[rotation_index]

    def _append_calisthenics_bonus(self, primary_list: list[dict], calisthenics: list[dict], muscle_group: str, day_key: str, week_number: int) -> list[dict]:
        """Añadir como máximo un ejercicio de calistenia al final de la sesión"""
        chosen = self._choose_calisthenics_exercise(calisthenics, muscle_group, day_key, week_number)
        if chosen:
            return primary_list + [chosen]
        return primary_list
    
    def _filter_exercises_by_level(self, exercises: list[dict], current_level: int) -> list[dict]:
        """Filtrar ejercicios según el nivel de dificultad actual - incluye ejercicios del nivel actual y anteriores"""
        filtered_exercises = []
        
        for exercise in exercises:
            exercise_level = exercise.get('difficulty_level', 1)
            
            # Incluir ejercicios del nivel actual y anteriores
            if exercise_level <= current_level:
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def _choose_forearm_exercise_by_level(self, day_key: str, week_number: int, forearm_exercises: list[dict]) -> dict | None:
        """Elegir ejercicio de antebrazo según nivel y rotación"""
        if not forearm_exercises:
            return None
        
        # Ordenar por nivel de dificultad
        forearm_exercises.sort(key=lambda x: x.get('difficulty_level', 1))
        
        # Calcular índice de rotación
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_idx = day_names.index(day_key) if day_key in day_names else 0
        rotation_index = ((week_number - 1) * 7 + day_idx) % len(forearm_exercises)
        
        return forearm_exercises[rotation_index]
    
    def _get_planned_leg_exercises(self, day_key: str, week_number: int, available_exercises: list[dict]) -> list[dict]:
        """Obtener ejercicios de piernas planificados - incluye todos los ejercicios disponibles según nivel"""
        # Obtener el nivel actual
        current_level = (week_number - 1) // 4 + 1
        
        # Todos los ejercicios disponibles en el nivel actual
        # Los ejercicios ya están filtrados por nivel en get_planned_exercises_for_group
        return available_exercises
    
    def get_general_progression(self, level: int, original_reps: str) -> str:
        """
        Calcular progresión general de repeticiones según el nivel.
        Aumenta las repeticiones base según el nivel del usuario.
        """
        # Si no hay dígitos, devolver original
        if not any(c.isdigit() for c in original_reps):
            return original_reps

        try:
            # Intentar parsear rango "X-Y"
            if '-' in original_reps:
                parts = original_reps.split('-')
                min_reps = int(parts[0].strip())
                # Manejar caso "8-10 por pierna"
                max_reps_part = parts[1].strip()
                suffix = ""
                
                if " " in max_reps_part:
                    # Separar número del texto (ej: "10 por pierna")
                    max_reps_num_str = max_reps_part.split(' ')[0]
                    suffix = " " + " ".join(max_reps_part.split(' ')[1:])
                    max_reps = int(max_reps_num_str)
                else:
                    max_reps = int(max_reps_part)
                
                # Calcular incremento basado en nivel (nivel 1 es base)
                # Nivel 1: +0
                # Nivel 2: +2
                # Nivel 3: +4
                # Nivel 4+: +6
                increase = (level - 1) * 2
                
                new_min = min_reps + increase
                new_max = max_reps + increase
                
                return f"{new_min}-{new_max}{suffix}"
                
            # Intentar parsear número único "X"
            else:
                # Manejar posible sufijo
                reps_part = original_reps.strip()
                suffix = ""
                
                if " " in reps_part:
                    reps_num_str = reps_part.split(' ')[0]
                    suffix = " " + " ".join(reps_part.split(' ')[1:])
                    reps = int(reps_num_str)
                else:
                    # Soportar formatos como "20km"
                    reps_num_str = ""
                    for char in reps_part:
                        if char.isdigit():
                            reps_num_str += char
                        else:
                            suffix += char

                    if not reps_num_str:
                        return original_reps

                    reps = int(reps_num_str)
                
                increase = (level - 1) * 2
                new_reps = reps + increase
                
                return f"{new_reps}{suffix}"
                
        except Exception:
            # Si falla el parseo, devolver original
            return original_reps

    # --- FIN utilidades nuevas ---

    def load_user_settings(self) -> Dict[str, Any]:
        """Cargar preferencias del usuario (equipamiento disponible, etc.)"""
        if os.path.exists(self.USER_SETTINGS_FILE):
            try:
                with open(self.USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                equipment = {**self.DEFAULT_USER_EQUIPMENT, **data.get('available_equipment', {})}
                return {'available_equipment': equipment, **{k: v for k, v in data.items() if k != 'available_equipment'}}
            except (json.JSONDecodeError, OSError):
                pass
        return {'available_equipment': dict(self.DEFAULT_USER_EQUIPMENT)}

    def save_user_settings(self):
        """Guardar preferencias del usuario"""
        self.user_settings['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, indent=2, ensure_ascii=False)
        except OSError as e:
            st.error(f"Error guardando configuración de usuario: {e}")

    def get_user_equipment(self) -> Dict[str, bool]:
        """Obtener equipamiento disponible del usuario"""
        return self.user_settings.get('available_equipment', dict(self.DEFAULT_USER_EQUIPMENT))

    def set_user_equipment(self, equipment: Dict[str, bool]):
        """Actualizar equipamiento disponible del usuario"""
        self.user_settings['available_equipment'] = equipment
        self.save_user_settings()

    def is_exercise_available(self, exercise: dict) -> bool:
        """Comprobar si un ejercicio puede programarse según el equipamiento del usuario"""
        equipment_key = exercise.get('equipment')
        exercise_name = exercise.get('name', '')
        user_equipment = self.get_user_equipment()

        if equipment_key in ('dumbbells_8kg', 'dumbbells_10kg', 'dumbbell_12kg'):
            return user_equipment.get('mancuernas', True)
        if equipment_key == 'floor_space':
            return user_equipment.get('suelo', True)
        if equipment_key == 'stationary_bike':
            return user_equipment.get('bicicleta', True)
        if equipment_key == 'parallel_bars':
            return user_equipment.get('paralelas', False)
        if equipment_key == 'bench_press_30kg':
            has_bar = user_equipment.get('barra', True)
            has_bench = user_equipment.get('banco', True)
            if exercise_name in self.BENCH_ONLY_EXERCISES:
                return has_bench
            if exercise_name in self.BAR_ONLY_EXERCISES:
                return has_bar
            if exercise_name in self.BAR_BENCH_EXERCISES:
                return has_bar and has_bench
            return has_bar and has_bench

        return True

    def filter_exercises_by_equipment(self, exercises: list[dict]) -> list[dict]:
        """Filtrar ejercicios según el equipamiento disponible del usuario"""
        return [exercise for exercise in exercises if self.is_exercise_available(exercise)]

    def render_equipment_settings(self):
        """Renderizar selector de equipamiento doméstico disponible"""
        st.markdown("### 🏠 Tu equipamiento")
        st.caption(
            "Perfil objetivo: entrenamiento doméstico con material básico. "
            "Marca lo que tienes y el plan se adaptará automáticamente."
        )

        current = self.get_user_equipment()
        updated = {}
        for key, label in self.USER_EQUIPMENT_LABELS.items():
            is_optional = key == 'paralelas'
            help_text = "Complemento de calistenia. Si no las tienes, no se programan." if is_optional else None
            updated[key] = st.checkbox(label, value=current.get(key, True), key=f"equipment_{key}", help=help_text)

        if st.button("💾 Guardar equipamiento", type="primary", use_container_width=True):
            self.set_user_equipment(updated)
            st.success("✅ Plan adaptado a tu equipamiento")
            st.rerun()

        unavailable = [self.USER_EQUIPMENT_LABELS[k] for k, v in updated.items() if not v]
        if unavailable:
            st.caption(f"Sin programar: {', '.join(unavailable)}")

    def load_nutrition_data(self) -> Dict[str, Any]:
        """Cargar datos de nutrición (lectura compartida entre módulos)"""
        nutrition_file = NUTRITION_FILE
        if os.path.exists(nutrition_file):
            try:
                with open(nutrition_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            'profile': {},
            'targets': {},
            'daily_logs': {},
            'weight_log': {},
        }

    def estimate_daily_activity_kcal(self, bmr: float, activity_level: str) -> float:
        """Estimar kcal de actividad diaria sin contar el entrenamiento estructurado"""
        tdee = self._calculate_tdee_from_bmr(bmr, activity_level)
        return max(tdee - bmr, 0)

    def _calculate_tdee_from_bmr(self, bmr: float, activity_level: str) -> float:
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        return bmr * activity_multipliers.get(activity_level, 1.55)

    def estimate_training_kcal(self) -> float:
        """Estimación orientativa del gasto por sesión de entrenamiento"""
        return float(self.ESTIMATED_TRAINING_KCAL_PER_SESSION)

    def calculate_bmr(self, weight: float, height: float, age: int, sex: str) -> float:
        """Calcular tasa metabólica basal usando Mifflin-St Jeor"""
        if sex == 'M':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

    def get_weekly_coherence_summary(self, week_number: int) -> Dict[str, Any]:
        """Resumen semanal cruzando entrenamiento, nutrición y peso"""
        week_dates_info = self.get_week_dates(week_number) or {}
        dates = week_dates_info.get('dates', [])
        nutrition_data = self.load_nutrition_data()
        profile = nutrition_data.get('profile', {})
        targets = nutrition_data.get('targets', {})
        daily_logs = nutrition_data.get('daily_logs', {})
        weight_log = nutrition_data.get('weight_log', {})

        training_days_planned = 0
        training_days_completed = 0
        calorie_days = 0
        total_calories = 0
        total_balance = 0
        balance_days = 0

        age = profile.get('age')
        weight = profile.get('weight')
        height = profile.get('height')
        sex = profile.get('sex', 'M')
        activity_level = profile.get('activity_level', 'moderate')
        has_profile = all(value is not None for value in [age, weight, height])

        bmr = self.calculate_bmr(weight, height, age, sex) if has_profile else None
        activity_kcal = self.estimate_daily_activity_kcal(bmr, activity_level) if bmr else None
        training_kcal = self.estimate_training_kcal()
        target_calories = targets.get('calories')

        week_weights = []
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

        for date_str in dates:
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                day_key = day_names[date_obj.weekday()]
            except ValueError:
                continue

            day_stats = self.get_day_completion_stats_internal(date_str, week_number)
            if not day_stats.get('is_rest_day') and day_stats.get('total', 0) > 0:
                training_days_planned += 1
                if day_stats.get('percentage', 0) >= 80:
                    training_days_completed += 1

            day_log = daily_logs.get(date_str, {}).get('total', {})
            day_calories = day_log.get('calories', 0)
            if day_calories > 0:
                calorie_days += 1
                total_calories += day_calories

            if has_profile and day_calories > 0:
                is_training_day = (
                    not day_stats.get('is_rest_day')
                    and day_stats.get('total', 0) > 0
                )
                estimated_burn = bmr + activity_kcal + (training_kcal if is_training_day else 0)
                total_balance += day_calories - estimated_burn
                balance_days += 1

            if date_str in weight_log:
                week_weights.append((date_str, weight_log[date_str]))

        avg_calories = total_calories / calorie_days if calorie_days else None
        avg_balance = total_balance / balance_days if balance_days else None

        weight_start = week_weights[0][1] if week_weights else None
        weight_end = week_weights[-1][1] if week_weights else profile.get('weight')
        weight_delta = None
        if weight_start is not None and weight_end is not None:
            weight_delta = round(weight_end - weight_start, 1)

        trend = "Sin datos suficientes"
        goal = profile.get('goal', 'maintain')
        if weight_delta is not None:
            if goal == 'cut' and weight_delta < -0.1:
                trend = "Pérdida de peso consistente"
            elif goal == 'cut' and weight_delta > 0.1:
                trend = "Tendencia al alza — revisa ingesta o adherencia"
            elif goal == 'bulk' and weight_delta > 0.1:
                trend = "Ganancia de peso progresiva"
            elif goal == 'bulk' and weight_delta < -0.1:
                trend = "Pérdida de peso — posible déficit excesivo"
            elif abs(weight_delta) <= 0.1:
                trend = "Peso estable"
            else:
                trend = "Mantenimiento estable"

        return {
            'week_number': week_number,
            'dates': dates,
            'training_completed': training_days_completed,
            'training_planned': training_days_planned,
            'avg_calories': avg_calories,
            'calorie_days': calorie_days,
            'avg_balance': avg_balance,
            'balance_days': balance_days,
            'weight_start': weight_start,
            'weight_end': weight_end,
            'weight_delta': weight_delta,
            'trend': trend,
            'has_profile': has_profile,
            'target_calories': target_calories,
            'estimated_bmr': round(bmr) if bmr else None,
            'estimated_activity_kcal': round(activity_kcal) if activity_kcal else None,
            'estimated_training_kcal': round(training_kcal),
        }

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde config.json"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error(f"❌ Archivo config.json no encontrado en: {CONFIG_FILE}")
            return {}
        except json.JSONDecodeError:
            st.error("❌ Error al leer config.json")
            return {}

    def load_progress_data(self) -> Dict[str, Any]:
        """Cargar datos de progreso"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Migrar datos antiguos que no tienen exercise_weeks
                self.migrate_progress_data(data)
                return data
            except Exception as e:
                st.warning(f"Error cargando progress_data.json: {e}")
                # Crear archivo de backup
                backup_name = app_path(f"progress_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                try:
                    import shutil
                    shutil.copy(PROGRESS_FILE, backup_name)
                    st.info(f"Backup creado: {backup_name}")
                except:
                    pass
        
        # Datos por defecto
        current_month = datetime.datetime.now().strftime('%Y-%m')
        default_data = {
            "months": {},
            "current_month": current_month,
            "total_workouts": 0,
            "completed_exercises": {},
            "exercise_weeks": {}
        }
        
        # Crear archivo inicial si no existe
        if not os.path.exists(PROGRESS_FILE):
            self.save_progress_data_internal(default_data)
        
        return default_data

    def migrate_progress_data(self, data: Dict[str, Any]):
        """Migrar datos de progreso antiguos para añadir información de semanas"""
        # Si ya tiene exercise_weeks, no necesita migración
        if 'exercise_weeks' in data:
            return
        
        # Inicializar exercise_weeks
        data['exercise_weeks'] = {}
        
        # Para los datos existentes, asumiremos que fueron marcados en la semana 1
        # El usuario puede corregir esto manualmente si es necesario
        if 'completed_exercises' in data:
            for date_str in data['completed_exercises'].keys():
                # Intentar determinar la semana más probable basándose en los ejercicios
                data['exercise_weeks'][date_str] = 1  # Valor por defecto

    def get_total_exercises_count(self) -> int:
        """Obtener el número total de ejercicios en el sistema"""
        total = 0
        for exercises in self.config.get('exercises', {}).values():
            total += len(exercises)
        return total

    def initialize_calendar_mapping(self):
        """Inicializar el sistema de mapeo entre semanas de entrenamiento y semanas calendario"""
        if 'calendar_mapping' not in self.progress_data:
            # Configurar fecha de inicio del programa si no existe
            if 'program_start_date' not in self.progress_data:
                # Por defecto, empezar desde la fecha actual (sin ajustar a lunes)
                today = datetime.datetime.now()
                self.progress_data['program_start_date'] = today.strftime('%Y-%m-%d')
            
            # Crear mapeo de semanas usando la fecha exacta configurada
            self.progress_data['calendar_mapping'] = {}
            self.update_calendar_mapping()
            self.save_progress_data()

    def update_calendar_mapping(self):
        """Actualizar el mapeo entre semanas de entrenamiento y fechas calendario"""
        if 'program_start_date' not in self.progress_data or self.progress_data['program_start_date'] is None:
            return
        
        try:
            start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d')
            # NO ajustar al lunes - usar la fecha exacta especificada por el usuario
            
            mapping = {}
            for week_num in range(1, 21):  # Semanas 1-20
                week_start = start_date + datetime.timedelta(weeks=week_num - 1)
                week_dates = []
                for day_offset in range(7):  # Lunes a Domingo
                    date = week_start + datetime.timedelta(days=day_offset)
                    week_dates.append(date.strftime('%Y-%m-%d'))
                
                mapping[str(week_num)] = {
                    'start_date': week_start.strftime('%Y-%m-%d'),
                    'end_date': (week_start + datetime.timedelta(days=6)).strftime('%Y-%m-%d'),
                    'dates': week_dates
                }
            
            self.progress_data['calendar_mapping'] = mapping
        except Exception as e:
            st.error(f"Error actualizando mapeo calendario: {e}")

    def get_calendar_week_for_date(self, date_str: str) -> int:
        """Obtener qué semana de entrenamiento corresponde a una fecha específica"""
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            
            # Verificar mapeo directo
            mapping = self.progress_data.get('calendar_mapping', {})
            for week_num, week_info in mapping.items():
                if date_str in week_info.get('dates', []):
                    return int(week_num)
            
            # Si no hay mapeo, calcular basándose en la fecha de inicio
            if 'program_start_date' in self.progress_data and self.progress_data['program_start_date'] is not None:
                start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d')
                
                days_diff = (target_date - start_date).days
                week_num = (days_diff // 7) + 1
                
                # Limitar a semanas válidas (1-20)
                if week_num < 1:
                    return 1
                elif week_num > 20:
                    return 20
                return week_num
            
            # Fallback: semana actual de sesión
            return st.session_state.get('current_week', 1)
            
        except Exception as e:
            st.error(f"Error calculando semana para fecha {date_str}: {e}")
            return st.session_state.get('current_week', 1)

    def format_date_to_spanish(self, date_str: str) -> str:
        """Convertir fecha de formato YYYY-MM-DD a DD-MM-YYYY"""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            return date_str  # Devolver original si no se puede convertir

    def get_week_dates(self, week_number: int) -> Dict[str, Any]:
        """Obtener las fechas (Lunes a Domingo) para una semana de entrenamiento específica"""
        mapping = self.progress_data.get('calendar_mapping', {})
        week_key = str(week_number)
        
        if week_key in mapping:
            return mapping[week_key]
        if week_number in mapping:
            return mapping[week_number]
        
        # Si no hay mapeo, calcularlo dinámicamente
        if 'program_start_date' in self.progress_data and self.progress_data['program_start_date'] is not None:
            try:
                start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d')
                
                week_start = start_date + datetime.timedelta(weeks=week_number - 1)
                week_dates = []
                for day_offset in range(7):
                    date = week_start + datetime.timedelta(days=day_offset)
                    week_dates.append(date.strftime('%Y-%m-%d'))
                
                return {
                    'start_date': week_start.strftime('%Y-%m-%d'),
                    'end_date': (week_start + datetime.timedelta(days=6)).strftime('%Y-%m-%d'),
                    'dates': week_dates
                }
            except Exception as e:
                st.error(f"Error calculando fechas para semana {week_number}: {e}")
        
        # Fallback: semana actual basada en hoy
        today = datetime.datetime.now()
        dates = []
        for i in range(7):
            date = today + datetime.timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        
        return {
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': (today + datetime.timedelta(days=6)).strftime('%Y-%m-%d'),
            'dates': dates
        }

    def get_week_dates_formatted(self, week_number):
        """Get week dates in Spanish DD-MM-YYYY format"""
        week_dates = self.get_week_dates(week_number)
        if week_dates and 'start_date' in week_dates:
            return {
                'start_date': self.format_date_to_spanish(week_dates['start_date']),
                'end_date': self.format_date_to_spanish(week_dates['end_date']),
                'dates': [self.format_date_to_spanish(date) for date in week_dates.get('dates', [])]
            }
        return week_dates
    
    def get_all_weeks_formatted(self):
        """Get all weeks mapping in Spanish DD-MM-YYYY format"""
        mapping = self.progress_data.get('calendar_mapping', {})
        formatted_mapping = {}
        for week, week_data in mapping.items():
            formatted_mapping[week] = {
                'start_date': self.format_date_to_spanish(week_data['start_date']),
                'end_date': self.format_date_to_spanish(week_data['end_date']),
                'dates': [self.format_date_to_spanish(date) for date in week_data.get('dates', [])]
            }
        return formatted_mapping
    
    def display_calendar_mapping_formatted(self):
        """Display calendar mapping in Spanish format for debug/config purposes"""
        mapping = self.get_all_weeks_formatted()
        for week, week_data in mapping.items():
            st.caption(f"Semana {week}: {week_data['start_date']} a {week_data['end_date']}")
    
    def get_calendar_mapping_display_text(self):
        """Get calendar mapping as formatted text for display"""
        mapping = self.get_all_weeks_formatted()
        lines = []
        for week, week_data in mapping.items():
            lines.append(f"Semana {week}: {week_data['start_date']} a {week_data['end_date']}")
        return "\n".join(lines)

    def set_program_start_date(self, start_date: str):
        """Configurar fecha de inicio del programa de entrenamiento"""
        try:
            # Validar formato DD/MM/YYYY y convertir a formato interno YYYY-MM-DD
            if '/' in start_date:
                # Formato DD/MM/YYYY
                date_obj = datetime.datetime.strptime(start_date, '%d/%m/%Y')
                internal_date = date_obj.strftime('%Y-%m-%d')
            else:
                # Formato YYYY-MM-DD (compatibilidad)
                date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                internal_date = start_date
            
            self.progress_data['program_start_date'] = internal_date
            self.update_calendar_mapping()
            self.save_progress_data()
            return True
        except ValueError:
            st.error("Formato de fecha inválido. Use DD/MM/YYYY")
            return False
    
    def get_program_start_date_display(self):
        """Obtener fecha de inicio del programa en formato DD/MM/YYYY para mostrar"""
        if 'program_start_date' in self.progress_data and self.progress_data['program_start_date'] is not None:
            try:
                date_obj = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                return self.progress_data['program_start_date']
        return None
        
        # Guardar la migración
        self.save_progress_data_internal(data)

    def save_progress_data_internal(self, data: Dict[str, Any]):
        """Método interno para guardar datos específicos (usado en migración)"""
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_exercise_completion_count(self, muscle_group: str, exercise_name: str) -> int:
        """Contar cuántas veces se ha completado un ejercicio específico (todas las semanas)"""
        count = 0
        if 'completed_exercises' not in self.progress_data:
            return count
        
        for date_str, exercises_day in self.progress_data['completed_exercises'].items():
            for exercise_id, is_completed in exercises_day.items():
                if is_completed:
                    # Formato esperado: muscle_group_exercise_name_day_weekN
                    # Necesitamos extraer grupo y ejercicio, ignorando día y semana
                    parts = exercise_id.split('_')
                    if len(parts) >= 4:  # al menos: grupo_ejercicio_dia_weekN
                        # El grupo muscular es la primera parte
                        id_muscle_group = parts[0]
                        
                        # Buscar dónde termina el nombre del ejercicio y empieza el día
                        day_parts = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                        
                        # Encontrar el día en el ID
                        day_index = -1
                        for i, part in enumerate(parts):
                            if part in day_parts:
                                day_index = i
                                break
                        
                        if day_index > 1:  # debe haber al menos grupo_ejercicio_dia
                            # Reconstruir el nombre del ejercicio (sin día ni semana)
                            id_exercise_name = '_'.join(parts[1:day_index])
                            
                            # Verificar coincidencia exacta (ignorando semana)
                            if (id_muscle_group == muscle_group and 
                                id_exercise_name == exercise_name):
                                count += 1
        
        return count

    def get_total_exercise_completions(self) -> Dict[str, int]:
        """Obtener el conteo total de completados para todos los ejercicios"""
        completion_counts = {}
        
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            for exercise in exercises:
                exercise_key = f"{muscle_group}_{exercise['name']}"
                completion_counts[exercise_key] = self.get_exercise_completion_count(
                    muscle_group, exercise['name']
                )
        
        return completion_counts

    def save_progress_data(self):
        """Guardar datos de progreso"""
        # Añadir timestamp para debug
        self.progress_data['last_saved'] = datetime.datetime.now().isoformat()
        
        try:
            # Crear backup antes de guardar
            if os.path.exists(PROGRESS_FILE):
                shutil.copy(PROGRESS_FILE, PROGRESS_BACKUP_FILE)
            
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
            
            # Verificar que se guardó correctamente
            if os.path.exists(PROGRESS_FILE):
                file_size = os.path.getsize(PROGRESS_FILE)
                if file_size < 50:  # Archivo muy pequeño, posible error
                    st.error(f"⚠️ Advertencia: progress_data.json parece estar corrupto (tamaño: {file_size} bytes)")
                    # Restaurar backup si existe
                    if os.path.exists(PROGRESS_BACKUP_FILE):
                        shutil.copy(PROGRESS_BACKUP_FILE, PROGRESS_FILE)
            
            # Forzar recarga en streamlit
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
                    
        except Exception as e:
            st.error(f"❌ Error guardando progress_data.json: {e}")
            # Restaurar backup si existe
            if os.path.exists(PROGRESS_BACKUP_FILE):
                shutil.copy(PROGRESS_BACKUP_FILE, PROGRESS_FILE)

    def reload_progress_data(self):
        """Recargar datos de progreso desde archivo"""
        self.progress_data = self.load_progress_data()
    
    def force_sync_progress(self):
        """Forzar sincronización de datos de progreso"""
        try:
            # Guardar datos actuales
            temp_data = self.progress_data.copy()
            
            # Recargar desde archivo
            self.reload_progress_data()
            
            # Si los datos en memoria son más recientes, mantenerlos
            if temp_data.get('last_saved', '') > self.progress_data.get('last_saved', ''):
                self.progress_data = temp_data
                self.save_progress_data()
            
            # Limpiar caches de Streamlit
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            if hasattr(st, 'cache_resource'):
                st.cache_resource.clear()
                
        except Exception as e:
            st.warning(f"Problema sincronizando progreso: {e}")
        return self.progress_data

    def generate_unique_key(self, *args) -> str:
        """Generar clave única basada en argumentos"""
        key_string = "_".join(str(arg) for arg in args)
        hash_suffix = hashlib.md5(key_string.encode()).hexdigest()[:8]
        return f"{key_string}_{hash_suffix}"

    def get_week_info(self, week_number: int) -> Dict[str, Any]:
        """Obtener información sobre la semana y el nivel"""
        level = (week_number - 1) // 4 + 1
        week_in_cycle = (week_number - 1) % 4 + 1
        
        level_names = {
            1: "🟢 Principiante",
            2: "🟡 Intermedio",
            3: "🟠 Avanzado",
            4: "🔴 Experto"
        }
        
        level_descriptions = {
            1: "Plan básico - 4 entrenamientos, 3 días de descanso",
            2: "Incremento de frecuencia - 5 entrenamientos, 2 días de descanso",
            3: "Incremento de volumen - 5 entrenamientos intensificados, 2 días de descanso",
            4: "Plan avanzado completo - 6 entrenamientos, 1 día de descanso"
        }
        
        return {
            "level": level,
            "level_name": level_names.get(level, f"🔥 Maestro {level-3}"),
            "level_description": level_descriptions.get(level, "Plan de élite personalizado"),
            "week_in_cycle": week_in_cycle,
            "total_weeks_completed": week_number - 1
        }

    def mark_exercise_completed(self, date_str: str, exercise_id: str, completed: bool, week_number: int | None = None):
        """Marcar ejercicio específico como completado"""
        if 'completed_exercises' not in self.progress_data:
            self.progress_data['completed_exercises'] = {}
        
        if date_str not in self.progress_data['completed_exercises']:
            self.progress_data['completed_exercises'][date_str] = {}
        
        # Si no se proporciona week_number, usar la semana actual
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        
        # Determinar el ID correcto según el formato
        if '_week' in exercise_id:
            # Ya tiene sufijo de semana, usar tal como está
            unique_exercise_id = exercise_id
        else:
            # No tiene sufijo, añadir el de la semana actual
            unique_exercise_id = f"{exercise_id}_week{week_number}"
        
        self.progress_data['completed_exercises'][date_str][unique_exercise_id] = completed
        
        # Guardar la semana en la que se marcó este ejercicio para futura referencia
        if 'exercise_weeks' not in self.progress_data:
            self.progress_data['exercise_weeks'] = {}
        
        if date_str not in self.progress_data['exercise_weeks']:
            self.progress_data['exercise_weeks'][date_str] = week_number
        
        # Solo actualizar la semana si es la primera vez que se marca algo en esta fecha
        # o si estamos marcando como completado (no desmarcando)
        if completed or date_str not in self.progress_data['exercise_weeks']:
            self.progress_data['exercise_weeks'][date_str] = week_number
        
        # Recalcular días completados automáticamente
        self.update_completed_workouts()
        self.save_progress_data()
        
        # Forzar sincronización inmediata
        self.force_sync_progress()

    def update_completed_workouts(self):
        """Actualizar la lista de días completados basándose en ejercicios marcados"""
        if 'completed_exercises' not in self.progress_data:
            return
        
        if 'completed_workouts' not in self.progress_data:
            self.progress_data['completed_workouts'] = {}
        
        # Revisar cada fecha con ejercicios registrados
        for date_str in self.progress_data['completed_exercises'].keys():
            # Obtener semana para esta fecha
            week_number = self.progress_data.get('exercise_weeks', {}).get(date_str, 1)
            
            # Calcular estadísticas de completado para este día
            stats = self.get_day_completion_stats_internal(date_str, week_number)
            
            # Considerar el día como completado si tiene ≥80% de ejercicios realizados
            # o si es un día de descanso
            is_completed = stats['is_rest_day'] or stats['percentage'] >= 80
            
            # Obtener clave del mes
            month_key = date_str[:7]  # YYYY-MM
            
            if month_key not in self.progress_data['completed_workouts']:
                self.progress_data['completed_workouts'][month_key] = []
            
            # Añadir o remover de la lista según el estado
            if is_completed and date_str not in self.progress_data['completed_workouts'][month_key]:
                self.progress_data['completed_workouts'][month_key].append(date_str)
            elif not is_completed and date_str in self.progress_data['completed_workouts'][month_key]:
                self.progress_data['completed_workouts'][month_key].remove(date_str)
    
    def get_day_completion_stats_internal(self, date_str: str, week_number: int) -> Dict[str, Any]:
        """Método interno para calcular estadísticas de completado de un día"""
        # Obtener plan del día
        week_info = self.get_week_info(week_number)
        
        if week_number <= 4:
            week_key = f"semana{week_number}"
            if week_key not in self.config.get('weekly_schedule', {}):
                return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
            week_plan = self.config['weekly_schedule'][week_key]
        else:
            # Para semanas avanzadas, necesitamos importar el módulo training_plan
            try:
                from .training_plan import TrainingPlanModule
                trainer = TrainingPlanModule()
                trainer.config = self.config
                trainer.progress_data = self.progress_data
                week_plan = trainer.generate_advanced_week(week_number)
            except:
                return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
        
        # Determinar día de la semana
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_key = day_names[date_obj.weekday()]
        
        muscle_groups = week_plan.get(day_key, [])
        
        # Si no hay grupos musculares programados, es día de descanso
        if not muscle_groups:
            return {'completed': 0, 'total': 0, 'percentage': 100, 'exercises': [], 'muscle_groups': [], 'is_rest_day': True}
        
        total_exercises = 0
        completed_exercises = 0
        exercise_list = []
        
        for muscle_group in muscle_groups:
            if muscle_group in self.config.get('exercises', {}):
                # USAR lista planificada que alterna antebrazos
                planned = self.get_planned_exercises_for_group(muscle_group, day_key, week_number)
                for exercise in planned:
                    exercise_id = f"{muscle_group}_{exercise['name']}_{day_key}_week{week_number}"
                    is_completed = self.is_exercise_completed(date_str, exercise_id, week_number)
                    
                    exercise_list.append({
                        'name': exercise['name'],
                        'muscle_group': muscle_group,
                        'completed': is_completed
                    })
                    
                    total_exercises += 1
                    if is_completed:
                        completed_exercises += 1
                    if is_completed:
                        completed_exercises += 1
        
        percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 100
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'percentage': percentage,
            'exercises': exercise_list,
            'muscle_groups': muscle_groups,
            'is_rest_day': False
        }

    def render_exercise_details(self, exercise: Dict[str, Any], muscle_group: str, day_key: str, show_videos: bool, show_instructions: bool, show_tips: bool, week_number: int | None = None):
        """Renderizar detalles de un ejercicio completo"""
        if week_number is None:
            current_week = int(st.session_state.get('current_week', 1))
        else:
            current_week = week_number
        
        exercise_name = exercise['name']
        exercise_id = f"{muscle_group}_{exercise_name}_{day_key}_week{current_week}"
        
        # Obtener fecha actual para marcar progreso
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        is_completed = self.is_exercise_completed(current_date, exercise_id, current_week)
        
        # Checkbox de completado prominente
        col_checkbox, col_title = st.columns([1, 4])
        with col_checkbox:
            completed = st.checkbox(
                "✅ Marcar",
                value=is_completed,
                key=self.generate_unique_key("exercise_completed", exercise_id, current_date),
                help=f"Marcar {exercise_name} como completado hoy"
            )
            if completed != is_completed:
                self.mark_exercise_completed(current_date, exercise_id, completed, current_week)
                # Forzar recarga del progreso para asegurar persistencia
                self.reload_progress_data()
                # Forzar actualización de la interfaz para mostrar el progreso actualizado
                st.rerun()
                self.reload_progress_data()
                if completed:
                    st.success(f"🎉 ¡{exercise_name} completado!")
                else:
                    st.info(f"📋 {exercise_name} marcado como pendiente")
                st.rerun()
        
        # Progresión dinámica para antebrazos
        display_sets = exercise.get('sets', 1)
        display_reps = exercise.get('reps', '')
        if exercise.get('category') == 'forearm':
            level = self._get_level_for_week(current_week)
            s, r = self.get_forearm_progression(level)
            display_sets, display_reps = s, r
        
        with col_title:
            # Obtener nivel de dificultad del ejercicio
            difficulty_level = exercise.get('difficulty_level', 1)
            difficulty_colors = ["", "🟢", "🟡", "🟠", "🔴"]
            difficulty_names = ["", "Principiante", "Intermedio", "Avanzado", "Experto"]
            difficulty_emoji = difficulty_colors[difficulty_level] if difficulty_level <= 4 else "🔥"
            difficulty_name = difficulty_names[difficulty_level] if difficulty_level <= 4 else "Maestro"
            
            status_emoji = "✅" if completed else "⭕"
            st.markdown(f"### {status_emoji} {difficulty_emoji} {exercise_name}")
            st.markdown(f"**Series:** {display_sets} | **Reps:** {display_reps} | **Nivel:** {difficulty_name} | **Grupo:** {muscle_group.title()}")
        
        with st.expander(f"ℹ️ Ver detalles de {exercise_name}", expanded=False):
            # Información del ejercicio
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📊 Información:**")
                st.write(f"• Series: {display_sets}")
                st.write(f"• Repeticiones: {display_reps}")
                st.write(f"• Nivel: {difficulty_name} {difficulty_emoji}")
                st.write(f"• Grupo Muscular: {muscle_group.title()}")
                
                st.markdown("**📝 Descripción:**")
                st.write(exercise.get('description', ''))
            
            with col2:
                # ...existing code...
                pass

    # --- NUEVOS MÉTODOS: estado de ejercicios y utilidades de YouTube ---
    def is_exercise_completed(self, date_str: str, exercise_id: str, week_number: int | None = None) -> bool:
        """Comprobar si un ejercicio (con sufijo de semana) está marcado como completado para una fecha dada."""
        if 'completed_exercises' not in self.progress_data:
            return False
        if week_number is None:
            week_number = st.session_state.get('current_week', 1)
        day_map = self.progress_data.get('completed_exercises', {}).get(date_str, {})
        
        # Determinar el ID correcto según el formato
        if '_week' in exercise_id:
            # Ya tiene sufijo de semana, usar tal como está
            unique_id = exercise_id
        else:
            # No tiene sufijo, añadir el de la semana actual
            unique_id = f"{exercise_id}_week{week_number}"
        
        # Buscar ÚNICAMENTE el ID con sufijo de semana específico (formato actual)
        if unique_id in day_map:
            return bool(day_map.get(unique_id))
        
        # Compatibilidad SOLO para formato antiguo sin sufijos (no buscar otras semanas)
        base_id = exercise_id.replace(f"_week{week_number}", "") if '_week' in exercise_id else exercise_id
        if base_id in day_map and '_week' not in base_id:
            return bool(day_map.get(base_id))
        
        # NO buscar en otras semanas - garantizar independencia semanal
        return False

    def validate_youtube_url(self, url: str) -> tuple[bool, str]:
        """Validar URL de YouTube. Devuelve (es_valida, tipo)."""
        if not url or not isinstance(url, str):
            return False, 'empty'
        
        u = url.strip()
        
        # Tipos soportados con prioridad específica
        if 'youtube.com/shorts/' in u:
            return True, 'shorts'
        if 'youtube.com/watch' in u and 'v=' in u:
            return True, 'video'
        if 'youtu.be/' in u:
            return True, 'short_url'
        
        # Aceptar otras urls de youtube como válidas
        if 'youtube.com' in u:
            return True, 'video'
        
        return False, 'invalid'

    def extract_video_id(self, url: str) -> str:
        """Extraer ID del video de YouTube de cualquier formato de URL."""
        if not url:
            return ""
        
        import re
        
        # Para shorts: https://www.youtube.com/shorts/pvb7SYiaMAw
        shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
        if shorts_match:
            return shorts_match.group(1)
        
        # Para videos normales: https://www.youtube.com/watch?v=VIDEO_ID
        watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
        if watch_match:
            return watch_match.group(1)
        
        # Para URLs cortas: https://youtu.be/VIDEO_ID
        youtu_be_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
        if youtu_be_match:
            return youtu_be_match.group(1)
        
        return ""

    def render_youtube_video(self, url: str):
        """Renderizar video de YouTube (acepta watch, shorts y youtu.be)."""
        if not url:
            return
        
        try:
            # Extraer ID del video
            video_id = self.extract_video_id(url)
            
            if not video_id:
                st.warning("No se pudo extraer el ID del video de YouTube")
                st.markdown(f"[🎥 Ver video en YouTube]({url})")
                return
            
            # Para shorts, usar iframe HTML personalizado con mejor formato
            if 'shorts/' in url:
                # Crear iframe responsivo para shorts
                iframe_html = f"""
                <div style="display: flex; justify-content: center; margin: 10px 0;">
                    <iframe 
                        width="315" 
                        height="560" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        title="YouTube video player" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                        allowfullscreen
                        style="border-radius: 8px;">
                    </iframe>
                </div>
                """
                st.markdown(iframe_html, unsafe_allow_html=True)
                
                # Enlace adicional por si el iframe no funciona
                st.markdown(f"[🔗 Ver en YouTube]({url})", help="Si el video no se reproduce, haz clic aquí")
                
            else:
                # Para videos normales, usar st.video con URL convertida
                embed_url = f"https://www.youtube.com/watch?v={video_id}"
                st.video(embed_url)
                
        except Exception as e:
            st.warning(f"No se pudo renderizar el video: {e}")
            # Fallback: mostrar enlace directo
            st.markdown(f"[🎥 Ver video en YouTube]({url})")

    def render_youtube_video_old(self, url: str):
        """Renderizar video de YouTube (método anterior como fallback)."""
        if not url:
            return
        # Streamlit soporta directamente st.video con URLs de YouTube
        try:
            st.video(url)
        except Exception as e:
            st.warning(f"No se pudo renderizar el video: {e}")

    def update_exercise_youtube_url(self, muscle_group: str, exercise_name: str, new_url: str) -> bool:
        """Actualizar la URL de YouTube de un ejercicio tanto en memoria como en config.json"""
        try:
            exercises = self.config.get('exercises', {}).get(muscle_group, [])
            updated = False
            for ex in exercises:
                if ex.get('name') == exercise_name:
                    ex['youtube_url'] = new_url
                    updated = True
                    break
            if not updated:
                st.error("Ejercicio no encontrado en la configuración")
                return False
            # Guardar en disco
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            # Limpiar cache para reflejar cambios
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"No se pudo actualizar la URL: {e}")
            return False

    def render_week_selector(self):
        """Renderizar selector de semana simplificado"""
        st.markdown("### 📅 Selector de Semana")
        
        # Crear columns para el selector y el botón
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Selector de semana
            current_week = st.session_state.get('current_week', 1)
            max_weeks = self.config.get('total_weeks', 20)
            
            selected_week = st.selectbox(
                "Selecciona la semana:",
                range(1, max_weeks + 1),
                index=current_week - 1,
                format_func=lambda x: f"Semana {x}" + (" (Actual)" if x == current_week else ""),
                key="week_selector"
            )
            
            # Actualizar la semana actual si cambió
            if selected_week != st.session_state.current_week:
                st.session_state.current_week = selected_week
                st.rerun()
        
        with col2:
            # Botón para ir a la semana actual
            if st.button("🎯 Ir a Semana Actual", help="Ir a la semana detectada automáticamente"):
                auto_week = self.get_auto_detected_week()
                st.session_state.current_week = auto_week
                st.rerun()
        
        st.markdown("---")
