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
    MAX_EXERCISES_PER_MUSCLE_GROUP = 6
    MAX_SUGGESTED_WARMUPS = 3
    DAY_KEYS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

    WARMUP_BY_MUSCLE_GROUP = {
        'pecho': ['Rotaciones de Hombros', 'Rotaciones de Brazos'],
        'espalda': ['Encogimientos Escapulares en Inversión', 'Rotaciones de Hombros', 'Rotaciones de Brazos'],
        'hombros': ['Rotaciones de Hombros', 'Rotaciones de Brazos'],
        'brazos': ['Rotaciones de Brazos', 'Rotaciones de Hombros'],
        'piernas': ['Círculos de Caderas', 'Balanceo de Piernas', 'Elevaciones de Rodillas'],
        'gemelos': ['Balanceo de Piernas', 'Círculos de Caderas'],
        'abs': ['Círculos de Caderas', 'Elevaciones de Rodillas'],
        'cardio': ['Jumping Jacks Suaves', 'Elevaciones de Rodillas'],
    }
    GENERAL_WARMUP_FILLERS = [
        'Rotaciones de Cuello',
        'Jumping Jacks Suaves',
        'Elevaciones de Rodillas',
    ]

    MUSCLE_GROUP_LABELS_ES = {
        'pecho': 'Pecho',
        'espalda': 'Espalda',
        'hombros': 'Hombros',
        'brazos': 'Brazos',
        'piernas': 'Piernas',
        'gemelos': 'Gemelos',
        'abs': 'Abdominales',
        'cardio': 'Cardio',
    }

    LEVEL_TRANSITION_INFO = {
        2: {
            'title': 'Nivel 2 — Intermedio (semanas 5-8)',
            'changes': [
                '**4 series** por ejercicio de fuerza',
                '**+1 día** de entrenamiento por semana (martes activo)',
                'Nuevos ejercicios desbloqueados en el catálogo',
                'Hasta **6 ejercicios por grupo** con rotación automática',
            ],
        },
        3: {
            'title': 'Nivel 3 — Avanzado (semanas 9-12)',
            'changes': [
                '**5 series** por ejercicio',
                'Más frecuencia de **abdominales** y cardio en el calendario',
                'Reps de fuerza se mantienen estables (sin más subidas)',
                'Rotación ampliada con más ejercicios en el pool',
            ],
        },
        4: {
            'title': 'Nivel 4 — Experto (semanas 13-20)',
            'changes': [
                '**6 series** por ejercicio — volumen máximo',
                'Plan avanzado: **6 días** de entrenamiento por semana',
                'Rotación entre todo el catálogo desbloqueado',
                'Prioriza la técnica y la recuperación entre sesiones',
            ],
        },
    }
    
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
    
    def _get_training_plan_module(self):
        """Instancia compartida de TrainingPlanModule con config y progreso actuales."""
        from .training_plan import TrainingPlanModule
        trainer = TrainingPlanModule()
        trainer.config = self.config
        trainer.progress_data = self.progress_data
        return trainer

    def has_training_progress(self) -> bool:
        """True si el usuario ha completado al menos un ejercicio."""
        for exercises in self.progress_data.get('completed_exercises', {}).values():
            if any(exercises.values()):
                return True
        return False

    def _get_max_week_with_progress(self) -> int:
        """Mayor número de semana con al menos un ejercicio completado."""
        max_week = 0
        for exercises in self.progress_data.get('completed_exercises', {}).values():
            for exercise_id, is_completed in exercises.items():
                if is_completed and '_week' in exercise_id:
                    try:
                        week_part = exercise_id.split('_week')[-1]
                        week_number = int(''.join(ch for ch in week_part if ch.isdigit()))
                        max_week = max(max_week, week_number)
                    except (IndexError, ValueError):
                        continue
        return max_week

    def get_auto_detected_week(self) -> int:
        """Auto-detectar la semana de entrenamiento actual basada en el progreso del usuario."""
        if not self.has_training_progress():
            return 1

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        program_week = min(max(self.get_calendar_week_for_date(today), 1), 20)
        max_week_with_progress = self._get_max_week_with_progress()

        if max_week_with_progress > 0:
            week_stats = self.get_week_completion_stats_for_week(max_week_with_progress)
            if week_stats['percentage'] >= 80:
                return min(max_week_with_progress + 1, 20)
            return max_week_with_progress

        return program_week

    def get_week_completion_stats_for_week(self, week_number: int) -> Dict[str, Any]:
        """Porcentaje de días de entrenamiento completados (≥80%) en una semana del programa."""
        week_stats = self._get_training_plan_module().get_week_completion_stats(week_number)
        training_days = [day for day in week_stats.get('days', []) if not day.get('is_rest_day') and day.get('total', 0) > 0]
        completed_training_days = sum(1 for day in training_days if day.get('percentage', 0) >= 80)
        total_training_days = len(training_days)
        percentage = (completed_training_days / total_training_days * 100) if total_training_days > 0 else 0
        return {
            'percentage': percentage,
            'completed_days': completed_training_days,
            'total_days': total_training_days,
        }
    
    def check_and_advance_week_automatically(self):
        """Verificar si la semana actual está completa y avanzar automáticamente"""
        current_week = st.session_state.get('current_week', 1)
        
        # No avanzar si ya estamos en la semana 20 (última)
        if current_week >= 20:
            return False
            
        # Calcular completado de la semana actual (fechas del programa, no rolling 7 días)
        completion_stats = self._get_training_plan_module().get_week_completion_stats(current_week)
        
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
        """Obtener estadísticas de completado de la semana actual del programa."""
        current_week = st.session_state.get('current_week', 1)
        from .training_plan import TrainingPlanModule
        tp = TrainingPlanModule()
        tp.config = self.config
        tp.progress_data = self.progress_data
        return tp.get_week_completion_stats(current_week)
    
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
    
    def _parse_rep_range_bounds(self, reps: str) -> tuple[int | None, int | None]:
        """Extraer límite inferior y superior numérico de un string de repeticiones."""
        if '(7+7+7)' in reps or 'segundo' in reps.lower() or 'km' in reps.lower():
            return None, None

        if '-' in reps:
            parts = reps.split('-', 1)
            try:
                low = int(''.join(c for c in parts[0] if c.isdigit()))
            except ValueError:
                return None, None
            max_num = ''.join(c for c in parts[1] if c.isdigit())
            if not max_num:
                return None, None
            return low, int(max_num)

        num = ''.join(c for c in reps if c.isdigit())
        if not num:
            return None, None
        value = int(num)
        return value, value

    def _get_progression_rep_base(self, base_reps: str) -> str:
        """Punto de partida en semana 1: 9-10 para rangos de fuerza habituales (tope ≤ 12 reps)."""
        _, high = self._parse_rep_range_bounds(base_reps)
        if high is not None and high <= 12:
            return '9-10'
        return base_reps

    def _get_sets_for_program_level(self, level: int) -> int:
        """Series por nivel del programa: 1→3, 2→4, 3→5, 4+→6."""
        return {1: 3, 2: 4, 3: 5}.get(level, 6)

    def _get_forearm_reps(self, level: int, week_in_cycle: int) -> str:
        """Repeticiones de antebrazo según nivel (series las marca el nivel del programa)."""
        if level <= 1:
            base = '9-10'
        elif level == 2:
            base = '10-12'
        elif level == 3:
            base = '10-12'
        else:
            base = '12-15'
        if level < 3:
            return self._apply_rep_increment(base, week_in_cycle - 1)
        return base

    def _is_plank_exercise(self, name: str) -> bool:
        return 'plancha' in name.lower()

    def _is_cardio_km_exercise(self, exercise: dict, reps: str) -> bool:
        reps_lower = reps.lower()
        name_lower = exercise.get('name', '').lower()
        return 'km' in reps_lower or 'bicicleta' in name_lower

    def _parse_time_range_seconds(self, reps: str) -> tuple[int | None, int | None, str]:
        """Parsear rangos temporales como '30-60 segundos' o '20-40 segundos por lado'."""
        if not any(c.isdigit() for c in reps) or 'segundo' not in reps.lower():
            return None, None, ''

        if '-' in reps:
            parts = reps.split('-', 1)
            try:
                min_s = int(''.join(c for c in parts[0] if c.isdigit()))
            except ValueError:
                return None, None, ''
            max_part = parts[1].strip()
            max_num = ''.join(c for c in max_part if c.isdigit())
            if not max_num:
                return None, None, ''
            max_s = int(max_num)
            suffix = max_part[len(max_num):].strip()
            if suffix and not suffix.startswith(' '):
                suffix = ' ' + suffix
            return min_s, max_s, suffix

        num = ''.join(c for c in reps if c.isdigit())
        if not num:
            return None, None, ''
        value = int(num)
        idx = reps.find(num)
        suffix = reps[idx + len(num):].strip()
        if suffix and not suffix.startswith(' '):
            suffix = ' ' + suffix
        elif not suffix:
            suffix = ' segundos'
        return value, value, suffix

    def _format_time_range(self, min_s: int, max_s: int, suffix: str) -> str:
        suffix = suffix or ' segundos'
        if min_s == max_s:
            return f"{min_s}{suffix}"
        return f"{min_s}-{max_s}{suffix}"

    def _progress_plank_time(self, original_reps: str, level: int) -> str:
        """Planchas: +10 segundos por cada cambio de nivel del programa."""
        min_s, max_s, suffix = self._parse_time_range_seconds(original_reps)
        if min_s is None or max_s is None:
            return original_reps
        bonus = (level - 1) * 10
        return self._format_time_range(min_s + bonus, max_s + bonus, suffix)

    def _apply_rep_increment(self, original_reps: str, increment: int) -> str:
        """Aplicar incremento numérico a repeticiones (rangos, unidades o sufijos)."""
        if increment <= 0 or not any(c.isdigit() for c in original_reps):
            return original_reps

        if '(7+7+7)' in original_reps:
            return original_reps

        try:
            if '-' in original_reps:
                parts = original_reps.split('-', 1)
                min_reps = int(parts[0].strip())
                max_reps_part = parts[1].strip()
                suffix = ''

                if ' ' in max_reps_part:
                    max_reps_num_str = max_reps_part.split(' ')[0]
                    suffix = ' ' + ' '.join(max_reps_part.split(' ')[1:])
                    max_reps = int(max_reps_num_str)
                else:
                    max_reps = int(max_reps_part)

                return f"{min_reps + increment}-{max_reps + increment}{suffix}"

            reps_part = original_reps.strip()
            suffix = ''

            if ' ' in reps_part:
                reps_num_str = reps_part.split(' ')[0]
                suffix = ' ' + ' '.join(reps_part.split(' ')[1:])
                reps = int(reps_num_str)
            else:
                reps_num_str = ''
                for char in reps_part:
                    if char.isdigit():
                        reps_num_str += char
                    else:
                        suffix += char
                if not reps_num_str:
                    return original_reps
                reps = int(reps_num_str)

            return f"{reps + increment}{suffix}"
        except (ValueError, IndexError):
            return original_reps

    def get_exercise_progression(self, exercise: dict, week_number: int) -> tuple[int, str]:
        """Calcular series y repeticiones/tiempo progresivos para un ejercicio y semana del programa."""
        week_info = self.get_week_info(week_number)
        level = week_info['level']
        week_in_cycle = week_info['week_in_cycle']

        base_reps = str(exercise.get('reps', ''))
        name = exercise.get('name', '')
        category = exercise.get('category', '')
        display_sets = self._get_sets_for_program_level(level)

        if self._is_cardio_km_exercise(exercise, base_reps):
            return 1, '15km' if level <= 2 else '20km'

        if category == 'forearm':
            return display_sets, self._get_forearm_reps(level, week_in_cycle)

        if self._is_plank_exercise(name):
            return display_sets, self._progress_plank_time(base_reps, level)

        if 'segundo' in base_reps.lower():
            return display_sets, base_reps

        progression_base = self._get_progression_rep_base(base_reps)
        if level >= 3:
            display_reps = progression_base
        else:
            week_bonus = week_in_cycle - 1
            level_bonus = (level - 1) * 2
            display_reps = self._apply_rep_increment(progression_base, week_bonus + level_bonus)
        return display_sets, display_reps

    def get_general_progression(self, level: int, original_reps: str, week_in_cycle: int = 1) -> str:
        """Compatibilidad: progresión de reps sin contexto de ejercicio completo."""
        if 'segundo' in original_reps.lower() or 'km' in original_reps.lower():
            if self._parse_time_range_seconds(original_reps)[0] is not None:
                return self._progress_plank_time(original_reps, level)
            return original_reps
        if level >= 3:
            return self._get_progression_rep_base(original_reps)
        week_bonus = week_in_cycle - 1
        level_bonus = (level - 1) * 2
        progression_base = self._get_progression_rep_base(original_reps)
        return self._apply_rep_increment(progression_base, week_bonus + level_bonus)

    def get_planned_exercises_for_group(self, muscle_group: str, day_key: str, week_number: int) -> list[dict]:
        """Devolver ejercicios planificados con tope de 6 por sesión, rotación y calistenia como complemento"""
        all_ex = self.config.get('exercises', {}).get(muscle_group, [])

        if muscle_group == 'abs':
            all_ex = all_ex + self.config.get('exercises', {}).get('abs_avanzados', [])

        current_level = (week_number - 1) // 4 + 1
        available_exercises = self._filter_exercises_by_level(all_ex, current_level)
        available_exercises = self.filter_exercises_by_equipment(available_exercises)
        primary, calisthenics = self._split_primary_and_calisthenics(available_exercises)

        if muscle_group == 'cardio':
            return primary

        reserve_calisthenics = 1 if calisthenics else 0
        max_total = self.MAX_EXERCISES_PER_MUSCLE_GROUP

        if muscle_group == 'brazos':
            non_forearm = [e for e in primary if e.get('category') != 'forearm']
            forearm_exercises = [e for e in primary if e.get('category') == 'forearm']
            chosen_forearm = self._choose_forearm_exercise_by_level(day_key, week_number, forearm_exercises)
            reserve_forearm = 1 if chosen_forearm else 0
            max_non_forearm = max_total - reserve_forearm - reserve_calisthenics
            rotated = self._choose_rotating_exercises(
                non_forearm, muscle_group, day_key, week_number, max_non_forearm
            )
            result = rotated + ([chosen_forearm] if chosen_forearm else [])
            return self._append_calisthenics_bonus(
                result, calisthenics, muscle_group, day_key, week_number, max_total=max_total
            )

        max_primary = max_total - reserve_calisthenics
        rotated = self._choose_rotating_exercises(primary, muscle_group, day_key, week_number, max_primary)
        return self._append_calisthenics_bonus(
            rotated, calisthenics, muscle_group, day_key, week_number, max_total=max_total
        )
    
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

        day_idx = self.DAY_KEYS.index(day_key) if day_key in self.DAY_KEYS else 0
        group_offset = sum(ord(c) for c in muscle_group) % 7
        rotation_index = ((week_number - 1) * 7 + day_idx + group_offset) % len(calisthenics)

        return calisthenics[rotation_index]

    def _append_calisthenics_bonus(
        self,
        primary_list: list[dict],
        calisthenics: list[dict],
        muscle_group: str,
        day_key: str,
        week_number: int,
        max_total: int | None = None,
    ) -> list[dict]:
        """Añadir como máximo un ejercicio de calistenia respetando el tope de la sesión"""
        if max_total is not None and len(primary_list) >= max_total:
            return primary_list
        chosen = self._choose_calisthenics_exercise(calisthenics, muscle_group, day_key, week_number)
        if chosen:
            return primary_list + [chosen]
        return primary_list

    def _get_rotation_index(self, muscle_group: str, day_key: str, week_number: int, pool_size: int) -> int:
        """Índice de rotación estable por grupo, día y semana"""
        if pool_size <= 0:
            return 0
        day_idx = self.DAY_KEYS.index(day_key) if day_key in self.DAY_KEYS else 0
        group_offset = sum(ord(c) for c in muscle_group) % pool_size
        return ((week_number - 1) * 7 + day_idx + group_offset) % pool_size

    def _choose_rotating_exercises(
        self,
        exercises: list[dict],
        muscle_group: str,
        day_key: str,
        week_number: int,
        max_count: int,
    ) -> list[dict]:
        """Seleccionar hasta max_count ejercicios rotando cuando el catálogo desbloqueado supera el tope"""
        if not exercises or max_count <= 0:
            return []

        sorted_exercises = sorted(
            exercises,
            key=lambda exercise: (exercise.get('difficulty_level', 1), exercise.get('name', '')),
        )
        if len(sorted_exercises) <= max_count:
            return sorted_exercises

        start = self._get_rotation_index(muscle_group, day_key, week_number, len(sorted_exercises))
        return [sorted_exercises[(start + index) % len(sorted_exercises)] for index in range(max_count)]

    def get_suggested_warmup_exercises(
        self,
        muscle_groups: list[str],
        day_key: str,
        week_number: int,
        max_count: int | None = None,
    ) -> list[dict]:
        """Elegir 2-3 ejercicios de calentamiento de la biblioteca según los grupos del día."""
        if max_count is None:
            max_count = self.MAX_SUGGESTED_WARMUPS

        warmup_catalog = {
            exercise['name']: exercise
            for exercise in self.config.get('exercises', {}).get('calentamiento', [])
        }
        if not warmup_catalog or not muscle_groups:
            return []

        scores: dict[str, int] = {}
        order: list[str] = []
        for muscle_group in muscle_groups:
            for name in self.WARMUP_BY_MUSCLE_GROUP.get(muscle_group, []):
                scores[name] = scores.get(name, 0) + 1
                if name not in order:
                    order.append(name)

        for name in self.GENERAL_WARMUP_FILLERS:
            if name not in order:
                order.append(name)

        ranked_names = sorted(
            [name for name in order if name in warmup_catalog],
            key=lambda name: (-scores.get(name, 0), order.index(name)),
        )
        available_names = [
            name for name in ranked_names
            if self.is_exercise_available(warmup_catalog[name])
        ]
        if not available_names:
            return []

        target_count = min(max(max_count, 2), self.MAX_SUGGESTED_WARMUPS, len(available_names))
        if len(available_names) > target_count:
            start = self._get_rotation_index('calentamiento', day_key, week_number, len(available_names))
            selected_names = [
                available_names[(start + index) % len(available_names)]
                for index in range(target_count)
            ]
        else:
            selected_names = available_names[:target_count]

        return [warmup_catalog[name] for name in selected_names]

    def get_week_context(self) -> Dict[str, Any]:
        """Contexto unificado de semanas: calendario, selector y auto-detección."""
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        today_date = datetime.datetime.now().date()
        today_week = self.get_training_week_for_date(today_str)
        selector_week = int(st.session_state.get('current_week', 1))
        auto_week = self.get_auto_detected_week()
        today_day_key = self.DAY_KEYS[today_date.weekday()]

        return {
            'today': today_str,
            'today_formatted': today_date.strftime('%d-%m-%Y'),
            'today_week': today_week,
            'today_day_key': today_day_key,
            'selector_week': selector_week,
            'auto_week': auto_week,
            'is_selector_aligned': selector_week == today_week,
            'week_info_today': self.get_week_info(today_week),
            'week_info_selector': self.get_week_info(selector_week),
        }

    def get_unlocked_exercise_pool(self, muscle_group: str, week_number: int) -> list[dict]:
        """Catálogo desbloqueado de un grupo (nivel + equipamiento), sin aplicar rotación."""
        all_exercises = list(self.config.get('exercises', {}).get(muscle_group, []))
        if muscle_group == 'abs':
            all_exercises.extend(self.config.get('exercises', {}).get('abs_avanzados', []))

        current_level = (week_number - 1) // 4 + 1
        available = self._filter_exercises_by_level(all_exercises, current_level)
        available = self.filter_exercises_by_equipment(available)

        seen: set[str] = set()
        pool: list[dict] = []
        for exercise in available:
            name = exercise.get('name', '')
            if name and name not in seen:
                seen.add(name)
                pool.append(exercise)
        return sorted(pool, key=lambda ex: (ex.get('difficulty_level', 1), ex.get('name', '')))

    def get_rotation_coverage_for_group(
        self, muscle_group: str, day_key: str, week_number: int
    ) -> Dict[str, Any]:
        """Cobertura del catálogo rotativo: pool, completados al menos una vez y sesión de hoy."""
        pool = self.get_unlocked_exercise_pool(muscle_group, week_number)
        today_exercises = self.get_planned_exercises_for_group(muscle_group, day_key, week_number)
        today_names = [ex['name'] for ex in today_exercises]

        completed_once: list[str] = []
        never_done: list[str] = []
        for exercise in pool:
            name = exercise['name']
            if self.get_exercise_completion_count(muscle_group, name) > 0:
                completed_once.append(name)
            else:
                never_done.append(name)

        rotating_other = [name for name in (ex['name'] for ex in pool) if name not in today_names]
        pool_total = len(pool)
        completed_count = len(completed_once)

        return {
            'muscle_group': muscle_group,
            'label': self.MUSCLE_GROUP_LABELS_ES.get(muscle_group, muscle_group.title()),
            'pool_total': pool_total,
            'completed_once': completed_count,
            'coverage_pct': (completed_count / pool_total * 100) if pool_total else 100,
            'today_names': today_names,
            'never_done': never_done,
            'rotating_other': rotating_other,
        }

    def should_show_level_transition_banner(self, week_number: int) -> bool:
        """Mostrar aviso al iniciar cada nuevo nivel (semanas 5, 9, 13, 17)."""
        return week_number in (5, 9, 13, 17)

    def render_week_coherence_panel(self):
        """Panel lateral: semana del calendario vs semana del selector."""
        ctx = self.get_week_context()
        today_info = ctx['week_info_today']
        selector_info = ctx['week_info_selector']

        st.markdown("### 📅 Semana del programa")
        st.markdown(
            f"**Hoy ({ctx['today_formatted']}):** Semana **{ctx['today_week']}** · "
            f"{today_info['level_name']}"
        )

        if ctx['is_selector_aligned']:
            st.success(f"Selector alineado: Semana {ctx['selector_week']}")
        else:
            st.warning(
                f"Selector en Semana **{ctx['selector_week']}** ({selector_info['level_name']}), "
                f"pero el calendario marca Semana **{ctx['today_week']}**. "
                f"Marca ejercicios con la semana del día que entrenas."
            )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📆 Semana de hoy", use_container_width=True, key="sync_calendar_week"):
                st.session_state.current_week = ctx['today_week']
                st.rerun()
        with col_b:
            if st.button("🎯 Auto-detectada", use_container_width=True, key="sync_auto_week"):
                st.session_state.current_week = ctx['auto_week']
                st.rerun()

        st.caption(
            f"Auto-detectada: Semana {ctx['auto_week']} · "
            f"Ciclo {today_info['week_in_cycle']}/4"
        )
    
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
        
        day_idx = self.DAY_KEYS.index(day_key) if day_key in self.DAY_KEYS else 0
        rotation_index = ((week_number - 1) * 7 + day_idx) % len(forearm_exercises)

        return forearm_exercises[rotation_index]

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

    def is_future_date(self, date_str: str) -> bool:
        """True si la fecha es posterior a hoy."""
        try:
            target = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            return target > datetime.date.today()
        except ValueError:
            return False

    def is_before_program_start(self, date_str: str) -> bool:
        """True si la fecha es anterior al inicio del programa."""
        start = self.progress_data.get('program_start_date')
        if not start:
            return False
        try:
            target = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            program_start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            return target < program_start
        except ValueError:
            return False

    def get_program_week_for_date(self, date_str: str) -> int:
        """Semana de entrenamiento del programa para una fecha (mapeo calendario)."""
        return self.get_calendar_week_for_date(date_str)

    def get_training_week_for_date(self, date_str: str) -> int:
        """Semana efectiva para planificar y marcar ejercicios."""
        if self.is_before_program_start(date_str):
            return 1
        if not self.has_training_progress():
            return 1

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if date_str == today:
            return self.get_auto_detected_week()

        return min(max(self.get_calendar_week_for_date(date_str), 1), 20)

    def get_pending_day_stats(self, week_number: int | None = None, is_future: bool = False) -> Dict[str, Any]:
        """Estadísticas vacías para días futuros o aún no alcanzados."""
        stats: Dict[str, Any] = {
            'completed': 0,
            'total': 0,
            'percentage': 0,
            'exercises': [],
            'muscle_groups': [],
            'is_rest_day': False,
            'is_empty_day': True,
            'is_future_day': is_future,
        }
        if week_number is not None:
            stats['calendar_week'] = week_number
        return stats

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

        if completed:
            if 'exercise_weeks' not in self.progress_data:
                self.progress_data['exercise_weeks'] = {}
            self.progress_data['exercise_weeks'][date_str] = week_number

        self.update_completed_workouts()
        self.save_progress_data()
        self.force_sync_progress()

        if completed:
            self.check_and_advance_week_automatically()

    def update_completed_workouts(self):
        """Actualizar la lista de días completados basándose en ejercicios marcados"""
        self._get_training_plan_module().update_completed_workouts()

    def get_day_completion_stats_internal(self, date_str: str, week_number: int) -> Dict[str, Any]:
        """Estadísticas de completado de un día (delegado al plan de entrenamiento)."""
        return self._get_training_plan_module().get_day_completion_stats(date_str, week_number)

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
        
        # Progresión dinámica según semana del programa
        display_sets, display_reps = self.get_exercise_progression(exercise, current_week)
        
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

    def render_youtube_url_editor(
        self,
        exercise: Dict[str, Any],
        muscle_group: str,
        *context_parts,
        show_video: bool = True,
    ) -> None:
        """Mostrar y permitir editar la URL de YouTube de un ejercicio."""
        exercise_name = exercise.get('name', '')
        youtube_url = exercise.get('youtube_url', '')

        if youtube_url and show_video:
            title = "### 🎥 Video Tutorial (Short)" if 'shorts/' in youtube_url else "### 🎥 Video Tutorial"
            st.markdown(title)
            self.render_youtube_video(youtube_url)

        st.markdown("### 🔗 Configurar Video Tutorial")
        input_key = self.generate_unique_key("youtube_url", muscle_group, exercise_name, *context_parts)
        new_url = st.text_input(
            "URL de YouTube:",
            value=youtube_url,
            key=input_key,
            placeholder="Ej: https://www.youtube.com/shorts/35_gCUE3SmM",
        )
        url_input = (new_url or "").strip()

        if url_input:
            is_valid, url_type = self.validate_youtube_url(url_input)
            if is_valid:
                if url_type == "shorts":
                    st.success("✅ YouTube Short válido")
                elif url_type == "video":
                    st.success("✅ Video de YouTube válido")
                elif url_type == "short_url":
                    st.success("✅ URL corta válida")
            else:
                st.error("❌ URL no válida")

        button_key = self.generate_unique_key("save_url", muscle_group, exercise_name, *context_parts)
        if st.button("💾 Guardar URL", key=button_key):
            is_valid, _url_type = self.validate_youtube_url(url_input)
            if is_valid:
                if self.update_exercise_youtube_url(muscle_group, exercise_name, url_input):
                    st.success("✅ URL guardada correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar")
            else:
                st.error("❌ URL no válida")

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
        """Selector de semana con aviso de alineación al calendario."""
        ctx = self.get_week_context()
        st.markdown("### 📅 Explorar otra semana")
        st.caption(
            f"Tu entrenamiento de **hoy** corresponde a la **Semana {ctx['today_week']}** del programa. "
            "Usa el selector solo para repasar o adelantar."
        )

        if not ctx['is_selector_aligned']:
            st.warning(
                f"Viendo Semana **{ctx['selector_week']}** · Hoy es Semana **{ctx['today_week']}** en el calendario."
            )

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            max_weeks = self.config.get('total_weeks', 20)
            selected_week = st.selectbox(
                "Semana a visualizar:",
                range(1, max_weeks + 1),
                index=ctx['selector_week'] - 1,
                format_func=lambda x: (
                    f"Semana {x}"
                    + (" · hoy" if x == ctx['today_week'] else "")
                    + (" · viendo" if x == ctx['selector_week'] else "")
                ),
                key="week_selector",
            )
            if selected_week != st.session_state.current_week:
                st.session_state.current_week = selected_week
                st.rerun()

        with col2:
            if st.button("📆 Hoy", help="Ir a la semana del calendario de hoy", use_container_width=True):
                st.session_state.current_week = ctx['today_week']
                st.rerun()

        with col3:
            if st.button("🎯 Auto", help="Semana según tu progreso", use_container_width=True):
                st.session_state.current_week = ctx['auto_week']
                st.rerun()

        st.markdown("---")
