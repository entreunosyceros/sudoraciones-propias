"""
Módulo de Progreso y Calendario
Contiene toda la lógica de la pestaña de progreso
"""
import datetime
import calendar
from typing import Dict, Any
import streamlit as st
from .base_trainer import BaseTrainer


class ProgressModule(BaseTrainer):
    """Módulo para gestionar el progreso y calendario"""
    
    # Diccionarios de traducción para meses
    MONTH_NAMES_ES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    MONTH_ABBR_ES = {
        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR',
        5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AGO',
        9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
    }
    
    def get_month_name_es(self, month: int) -> str:
        """Obtener nombre del mes en español"""
        return self.MONTH_NAMES_ES.get(month, f'Mes {month}')
    
    def get_day_completion_stats_filtered(self, date_str: str, filter_week: int | None = None) -> Dict[str, Any]:
        """Obtener estadísticas de completado de un día filtradas por semana"""
        if self.is_future_date(date_str):
            return self.get_pending_day_stats(is_future=True)
        if self.is_before_program_start(date_str):
            return self.get_pending_day_stats()

        if filter_week is None:
            week_num = int(st.session_state.get('current_week', 1))
        else:
            week_num = filter_week
        
        # Determinar si según el plan de la semana este día debería ser de descanso
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_key = day_names[date_obj.weekday()]
        
        # Obtener plan de la semana correspondiente
        week_plan = {}
        if week_num <= 4:
            week_key = f"semana{week_num}"
            week_plan = self.config.get('weekly_schedule', {}).get(week_key, {})
        else:
            from .training_plan import TrainingPlanModule
            trainer = TrainingPlanModule()
            trainer.config = self.config
            trainer.progress_data = self.progress_data
            week_plan = trainer.generate_advanced_week(week_num)
        
        muscle_groups_planned = week_plan.get(day_key, []) or []
        is_rest_day_planned = len(muscle_groups_planned) == 0
        
        # Si es día de descanso según el plan, devolverlo inmediatamente
        if is_rest_day_planned:
            return {
                'completed': 0,
                'total': 0,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': [],
                'is_rest_day': True,
                'is_empty_day': False
            }
        
        # Obtener ejercicios de esa fecha
        exercises_data = self.progress_data.get('completed_exercises', {}).get(date_str, {})
        
        # Si no hay datos pero el día debería tener entrenamiento, mostrar día vacío
        if not exercises_data:
            # Calcular ejercicios esperados según el plan del día
            expected_total = 0
            for mg in muscle_groups_planned:
                planned_list = self.get_planned_exercises_for_group(mg, day_key, week_num)
                expected_total += len(planned_list)
            
            return {
                'completed': 0,
                'total': expected_total,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': muscle_groups_planned,
                'is_rest_day': False,
                'is_empty_day': True
            }
        
        # Filtrar solo ejercicios de la semana especificada
        week_suffix = f"_week{week_num}"
        filtered_exercises = {}
        
        for exercise_id, is_completed in exercises_data.items():
            if exercise_id.endswith(week_suffix):
                filtered_exercises[exercise_id] = is_completed
        
        # Si no hay ejercicios de la semana especificada pero el día debería tener entrenamiento
        if not filtered_exercises:
            # Calcular ejercicios esperados según el plan del día
            expected_total = 0
            for mg in muscle_groups_planned:
                planned_list = self.get_planned_exercises_for_group(mg, day_key, week_num)
                expected_total += len(planned_list)
            
            return {
                'completed': 0,
                'total': expected_total,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': muscle_groups_planned,
                'is_rest_day': False,
                'is_empty_day': True
            }
        
        # Calcular estadísticas de los ejercicios filtrados
        total_exercises = len(filtered_exercises)
        completed_exercises = sum(1 for completed in filtered_exercises.values() if completed)
        
        # Extraer grupos musculares
        muscle_groups = set()
        exercise_list = []
        for exercise_id, is_completed in filtered_exercises.items():
            parts = exercise_id.split('_')
            if len(parts) >= 2:
                mg = parts[0]
                name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                muscle_groups.add(mg)
                exercise_list.append({'name': name, 'muscle_group': mg, 'completed': is_completed})
        
        percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'percentage': percentage,
            'exercises': exercise_list,
            'muscle_groups': list(muscle_groups),
            'is_rest_day': False,
            'is_empty_day': False
        }
    
    def get_month_abbr_es(self, month: int) -> str:
        """Obtener abreviación del mes en español"""
        return self.MONTH_ABBR_ES.get(month, f'M{month}')

    def get_month_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Obtener estadísticas del mes"""
        month_key = f"{year:04d}-{month:02d}"
        completed_days = self.progress_data.get('completed_workouts', {}).get(month_key, [])
        
        # Obtener días del mes
        days_in_month = calendar.monthrange(year, month)[1]
        
        return {
            'completed': len(completed_days),
            'total_days': days_in_month,
            'completion_rate': (len(completed_days) / days_in_month) * 100 if days_in_month > 0 else 0,
            'completed_dates': completed_days
        }

    def get_month_stats_filtered(self, year: int, month: int, filter_week: int) -> Dict[str, Any]:
        """Obtener estadísticas del mes filtradas por semana específica"""
        _, last_day = calendar.monthrange(year, month)
        
        total_days = 0
        completed_days = 0
        total_exercises = 0
        completed_exercises = 0
        
        for day in range(1, last_day + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            day_stats = self.get_day_completion_stats_filtered(date_str, filter_week)
            
            if not day_stats.get('is_empty_day', True):
                total_days += 1
                total_exercises += day_stats.get('total', 0)
                completed_exercises += day_stats.get('completed', 0)
                if day_stats.get('percentage', 0) == 100:
                    completed_days += 1
        
        completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'completed': completed_exercises,
            'total': total_exercises,
            'completion_rate': completion_rate,
            'total_days': total_days,
            'completed_days': completed_days
        }

    def get_week_number_for_date(self, date_str: str) -> int:
        """Determinar qué número de semana corresponde a una fecha específica"""
        if self.is_future_date(date_str):
            return self.get_program_week_for_date(date_str)

        # Mapeo explícito guardado al marcar ejercicios
        if 'exercise_weeks' in self.progress_data and date_str in self.progress_data['exercise_weeks']:
            return self.progress_data['exercise_weeks'][date_str]

        # Semana del programa según calendario (fuente canónica)
        program_week = self.get_program_week_for_date(date_str)

        # Si la fecha tiene ejercicios registrados, validar contra la semana del programa
        if 'completed_exercises' in self.progress_data and date_str in self.progress_data['completed_exercises']:
            exercise_ids = list(self.progress_data['completed_exercises'][date_str].keys())
            if exercise_ids:
                from collections import Counter
                week_numbers = []
                for exercise_id in exercise_ids:
                    if '_week' in exercise_id:
                        try:
                            week_part = exercise_id.split('_week')[-1]
                            week_num = int(''.join(ch for ch in week_part if ch.isdigit()))
                            week_numbers.append(week_num)
                        except (ValueError, IndexError):
                            continue
                if week_numbers:
                    return Counter(week_numbers).most_common(1)[0][0]

        return program_week

    def get_day_completion_stats(self, date_str: str, week_number: int | None = None) -> Dict[str, Any]:
        """Obtener estadísticas de finalización para un día específico"""
        if self.is_future_date(date_str):
            return self.get_pending_day_stats(is_future=True)
        if self.is_before_program_start(date_str):
            return self.get_pending_day_stats()

        # Si no se proporciona week_number, usar el mapeo calendario
        if week_number is None:
            week_number = self.get_calendar_week_for_date(date_str)
        
        # Determinar día de la semana (clave en español)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        day_key = day_names[date_obj.weekday()]
        
        # Obtener plan de la semana correspondiente
        week_plan = {}
        if week_number <= 4:
            week_key = f"semana{week_number}"
            week_plan = self.config.get('weekly_schedule', {}).get(week_key, {})
        else:
            from .training_plan import TrainingPlanModule
            trainer = TrainingPlanModule()
            trainer.config = self.config
            trainer.progress_data = self.progress_data
            week_plan = trainer.generate_advanced_week(week_number)
        
        muscle_groups_planned = week_plan.get(day_key, []) or []
        is_rest_day_planned = len(muscle_groups_planned) == 0
        
        # Prioridad: si el plan marca descanso, devolver descanso SIEMPRE
        if is_rest_day_planned:
            return {
                'completed': 0,
                'total': 0,
                'percentage': 0,
                'exercises': [],
                'muscle_groups': [],
                'is_rest_day': True,
                'is_empty_day': False,
                'calendar_week': week_number
            }
        
        # 1) Si hay datos en la fecha, calcular en base a los ejercicios reales de ese día
        exercises_data = self.progress_data.get('completed_exercises', {}).get(date_str)
        if exercises_data:
            # Filtrar solo ejercicios de la semana calendario correspondiente
            week_suffix = f"_week{week_number}"
            filtered_exercises = {k: v for k, v in exercises_data.items() if k.endswith(week_suffix)}
            
            if filtered_exercises:
                total_exercises = len(filtered_exercises)
                completed_exercises = sum(1 for completed in filtered_exercises.values() if completed)
                
                # Extraer grupos musculares presentes en los IDs
                muscle_groups = set()
                exercise_list = []
                for exercise_id, is_completed in filtered_exercises.items():
                    parts = exercise_id.split('_')
                    if len(parts) >= 2:
                        mg = parts[0]
                        name = '_'.join(parts[1:-2]) if len(parts) > 3 else parts[1]
                        muscle_groups.add(mg)
                        exercise_list.append({'name': name, 'muscle_group': mg, 'completed': is_completed})
                
                percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
                return {
                    'completed': completed_exercises,
                    'total': total_exercises,
                    'percentage': percentage,
                    'exercises': exercise_list,
                    'muscle_groups': list(muscle_groups),
                    'is_rest_day': False,
                    'is_empty_day': False,
                    'calendar_week': week_number
                }
        
        # 2) Si NO hay datos en la fecha actual, calcular ejercicios esperados según el plan del día
        expected_total = 0
        for mg in muscle_groups_planned:
            planned_list = self.get_planned_exercises_for_group(mg, day_key, week_number)
            expected_total += len(planned_list)
        
        return {
            'completed': 0,
            'total': expected_total,
            'percentage': 0,
            'exercises': [],
            'muscle_groups': muscle_groups_planned,
            'is_rest_day': False,
            'is_empty_day': True,
            'calendar_week': week_number
        }

    # Wrapper simple para la vista acumulativa (todas semanas) reutilizando la lógica existente
    def get_day_completion_stats_accumulated(self, date_str: str) -> Dict[str, Any]:
        """Obtener estadísticas combinadas para un día (acumulativo).

        La idea: identificar semana correspondiente y reutilizar la lógica del módulo de plan.
        """
        if self.is_future_date(date_str):
            return self.get_pending_day_stats(is_future=True)
        if self.is_before_program_start(date_str):
            return self.get_pending_day_stats()

        week_num = self.get_program_week_for_date(date_str)
        from .training_plan import TrainingPlanModule
        tp = TrainingPlanModule()
        tp.config = self.config
        tp.progress_data = self.progress_data
        return tp.get_day_completion_stats(date_str, week_num)

    def render_calendar(self, year: int, month: int, view_week: int | None = None):
        """Renderizar calendario con porcentajes filtrados por semana específica o acumulativo"""
        current_week = st.session_state.get('current_week', 1)
        month_name = self.get_month_name_es(month)
        
        if view_week is None:
            st.subheader(f"📅 {month_name} {year} - Progreso Acumulativo (Todas las Semanas)")
            st.caption("*Mostrando progreso combinado de todas las semanas completadas*")
        else:
            week_info = self.get_week_info(view_week)
            st.subheader(f"📅 {month_name} {year} - Semana {view_week} ({week_info['level_name']})")
            st.caption(f"*Mostrando solo progreso de la Semana {view_week}: {week_info['level_description']}*")
        
        # Obtener estadísticas del mes según la vista seleccionada
        if view_week is None:
            stats = self.get_month_stats(year, month)
        else:
            stats = self.get_month_stats_filtered(year, month, view_week)
        
        # Crear calendario
        cal = calendar.monthcalendar(year, month)
        
        # Nombres de días
        days_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        # CSS para el calendario con gradientes de progreso
        st.markdown("""
        <style>
        .calendar-day {
            text-align: center;
            padding: 8px;
            margin: 2px;
            border-radius: 8px;
            min-height: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }
        .day-perfect {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            color: white;
        }
        .day-good {
            background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
            color: white;
        }
        .day-partial {
            background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
            color: white;
        }
        .day-none {
            background: #ddd;
            color: #666;
        }
        .day-rest {
            background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
            color: #1b5e20;
            border: 2px solid #43a047;
        }
        .day-today {
            border: 3px solid #0984e3;
        }
        .day-empty {
            background: transparent;
        }
        .percentage-text {
            font-size: 10px;
            margin-top: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar estadísticas del mes (usar completed_days en vez de completed ejercicios)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Días con Entrenamiento", stats.get('completed_days', 0), f"de {stats.get('total_days', 0)}")
        with col2:
            st.metric("Tasa de Cumplimiento", f"{stats.get('completion_rate',0):.1f}%")
        with col3:
            if stats.get('completed_days',0) > 0:
                avg_per_week = stats.get('completed_days',0) / 4.33  # Promedio mensual aproximado
                st.metric("Promedio Semanal", f"{avg_per_week:.1f}", "días/semana")
        
        # Leyenda de colores
        st.markdown("#### Leyenda del Calendario")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🟢 **100%** - Entrenamiento completo")
        with col2:
            st.markdown("🟡 **80-99%** - Casi completo")
        with col3:
            st.markdown("🟠 **1-79%** - Parcialmente completado")
        with col4:
            st.markdown("⚪ **0%** - Sin entrenamientos")
        
        st.info("✅ **Días de descanso** se marcan automáticamente como completados con un ✓")
        
        st.markdown("---")
        
        # Cabecera con días de la semana
        header_cols = st.columns(7)
        for i, day_name in enumerate(days_names):
            with header_cols[i]:
                st.markdown(f"**{day_name}**")
        
        # Renderizar semanas
        today = datetime.datetime.now()
        current_week = st.session_state.get('current_week', 1)
        
        for week in cal:
            week_cols = st.columns(7)
            for i, day in enumerate(week):
                with week_cols[i]:
                    if day == 0:
                        st.markdown('<div class="calendar-day day-empty"></div>', unsafe_allow_html=True)
                    else:
                        date_str = f"{year:04d}-{month:02d}-{day:02d}"
                        
                        # Usar función específica según la vista seleccionada
                        if view_week is None:
                            # Vista acumulativa: mostrar progreso de todas las semanas
                            day_stats = self.get_day_completion_stats_accumulated(date_str)
                        else:
                            # Vista específica: mostrar solo progreso de la semana seleccionada
                            day_stats = self.get_day_completion_stats_filtered(date_str, view_week)
                        
                        # Determinar clase CSS según porcentaje y tipo de día
                        if day_stats.get('is_future_day', False):
                            css_class = "day-none"
                            percentage_text = ""
                        elif day_stats.get('is_rest_day', False):
                            css_class = "day-rest"
                            percentage_text = "✓"
                        elif day_stats.get('is_empty_day', False):
                            # Día sin entrenar - mostrarlo en blanco/gris
                            css_class = "day-none"
                            percentage_text = ""  # Sin texto
                        elif day_stats['percentage'] == 100:
                            css_class = "day-perfect"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        elif day_stats['percentage'] >= 80:
                            css_class = "day-good"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        elif day_stats['percentage'] > 0:
                            css_class = "day-partial"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        else:
                            css_class = "day-none"
                            percentage_text = f"{day_stats['percentage']:.0f}%"
                        
                        # Agregar clase especial si es hoy
                        today_class = ""
                        if (year == today.year and month == today.month and day == today.day):
                            today_class = " day-today"
                        
                        # Crear tooltip con información
                        if day_stats.get('is_future_day', False):
                            tooltip = f"Día {day}: Pendiente (aún no llega)"
                        elif day_stats.get('is_rest_day', False):
                            tooltip = f"Día {day}: Día de descanso ✓"
                        elif day_stats.get('is_empty_day', False):
                            tooltip = f"Día {day}: Sin entrenar"
                        else:
                            tooltip = f"Día {day}: {day_stats['percentage']:.0f}% completado"
                            if day_stats['total'] > 0:
                                tooltip += f"\nEjercicios: {day_stats['completed']}/{day_stats['total']}"
                                tooltip += f"\nGrupos: {', '.join(day_stats['muscle_groups'])}"
                        
                        st.markdown(f"""
                        <div class=\"calendar-day {css_class}{today_class}\" title=\"{tooltip}\">\n                            <div>{day}</div>\n                            <div class=\"percentage-text\">{percentage_text}</div>\n                        </div>
                        """, unsafe_allow_html=True)
        
        # Información adicional
        st.info("""
        **Calendario automático basado en ejercicios completados:**
        - Los porcentajes se calculan automáticamente desde el plan de entrenamiento
        - Un día se considera "completado" cuando ≥80% de ejercicios están hechos
        - Los colores indican el nivel de progreso del día
        - No es necesario marcar días manualmente
        """)

    def render_week_calendar(self, view_week: int):
        """Renderizar sólo los días entrenados (no descanso) de una semana concreta"""
        week_dates = self.get_week_dates(view_week)
        if not week_dates or 'dates' not in week_dates:
            st.warning("No hay fechas para la semana seleccionada.")
            return
        dates_list = week_dates['dates']
        week_info = self.get_week_info(view_week)
        st.subheader(f"📅 Semana {view_week} - {week_info['level_name']}")
        st.caption(f"{week_dates['start_date']} ➜ {week_dates['end_date']}")
        st.markdown("**Solo se muestran los días con entrenamiento planificado o registrado (se excluyen descansos).**")

        day_names_map = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
        training_days = []
        for idx, date_str in enumerate(dates_list):
            stats = self.get_day_completion_stats_filtered(date_str, view_week)
            if stats.get('is_rest_day'):
                continue  # excluir descanso
            # También excluir días totalmente vacíos sin ejercicios esperados
            if stats.get('total',0) == 0:
                continue
            training_days.append((idx, date_str, stats))

        if not training_days:
            st.info("No hay días entrenados registrados en esta semana todavía.")
            return

        # Estilos sencillos para tarjetas semanales
        st.markdown("""
        <style>
        /* Tarjeta de día de entrenamiento (semanal) accesible en tema claro/oscuro */
        .week-day-card {border:1px solid #d0d0d0; border-radius:10px; padding:12px; margin-bottom:8px; background:#f5f7fa; color:#222;}
        .week-day-header {display:flex; justify-content:space-between; align-items:center;}
        .badge {padding:2px 6px; border-radius:6px; font-size:11px; font-weight:600; letter-spacing:.3px;}
        .badge-full {background:#00b894; color:#fff;}
        /* Mejor contraste: texto oscuro sobre fondo amarillo claro */
        .badge-good {background:#fdcb6e; color:#3d2b00;}
        .badge-part {background:#fd79a8; color:#fff;}
        .badge-empty {background:#b2bec3; color:#fff;}
        /* Adaptación a modo oscuro del sistema */
        @media (prefers-color-scheme: dark) {
            .week-day-card {background:#2b2f33; border:1px solid #444; color:#f1f3f5;}
        }
        </style>
        """, unsafe_allow_html=True)

        for idx, date_str, stats in training_days:
            date_obj = datetime.datetime.strptime(date_str,'%Y-%m-%d')
            pretty = date_obj.strftime('%d-%m-%Y')
            pct = stats.get('percentage',0)
            if pct >= 100:
                badge_class='badge-full'; label='100%'
            elif pct >= 80:
                badge_class='badge-good'; label=f"{pct:.0f}%"
            elif pct > 0:
                badge_class='badge-part'; label=f"{pct:.0f}%"
            else:
                badge_class='badge-empty'; label='0%'
            completed = stats.get('completed',0)
            total = stats.get('total',0)
            mg = ', '.join(stats.get('muscle_groups',[])) if stats.get('muscle_groups') else '—'
            st.markdown(f"""
            <div class='week-day-card'>
              <div class='week-day-header'>
                <div><strong>{day_names_map[idx]}</strong> · {pretty}</div>
                <div class='badge {badge_class}'>{label}</div>
              </div>
              <div style='margin-top:6px;font-size:13px;'>Ejercicios: {completed}/{total} · Grupos: {mg}</div>
            </div>
            """, unsafe_allow_html=True)

        st.info("Resumen semanal basado únicamente en los días con trabajo efectivo (no se listan descansos).")

    def calculate_current_streak(self) -> int:
        """Calcular racha de días de ENTRENAMIENTO consecutivos ignorando días de descanso.

        Lógica:
        - Se recorre hacia atrás desde hoy.
        - Día de descanso (según plan) NO suma racha pero TAMPOCO la rompe.
        - Día con entrenamiento planificado y con >=1 ejercicio completado suma racha.
        - Día con entrenamiento planificado pero 0 ejercicios completados ROMPE la racha.
        """
        self.reload_progress_data()
        today = datetime.date.today()
        streak = 0
        # Revisar hasta 60 días hacia atrás para asegurar continuidad en semanas largas
        # MODELO B: Días de entrenamiento consecutivos (ignorando descansos).
        # Reglas:
        # - Días de descanso no suman ni rompen.
        # - Se cuenta un día solo si tiene ≥1 ejercicio COMPLETADO perteneciente a su semana (sufijo _weekN correcto).
        # - Primer día planificado sin ejercicios completados corta la racha.
        for i in range(60):
            check_date = today - datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            week_num = self.get_week_number_for_date(date_str)
            day_stats = self.get_day_completion_stats_filtered(date_str, week_num)
            if day_stats.get('is_rest_day'):
                continue  # descanso ignora
            total = day_stats.get('total', 0)
            completed = day_stats.get('completed', 0)
            percentage = (completed / total * 100) if total > 0 else 0
            completed_day = (total > 0) and (percentage >= 80)
            if completed_day:
                streak += 1
            else:
                if i == 0:
                    # Hoy incompleto: no rompe, solo se ignora
                    continue
                break
        return streak

    def render_progress_tab(self):
        """Renderizar pestaña de progreso con calendario"""
        st.header("📊 Tu Progreso de Entrenamiento")

        # Inicializar estado de navegación del calendario
        current_date = datetime.datetime.now()

        if 'calendar_year' not in st.session_state:
            st.session_state.calendar_year = current_date.year
        if 'calendar_month' not in st.session_state:
            st.session_state.calendar_month = current_date.month

        # Selector de semana para vista del calendario (apilado arriba)
        st.markdown("### 👁️ Vista del Calendario")
        view_options = ["Todas las Semanas (Acumulativo)"] + [f"Semana {i}" for i in range(1, 21)]
        selected_view = st.selectbox(
            "Mostrar progreso de:",
            options=view_options,
            index=0,
            key="calendar_view_selector"
        )
        if selected_view == "Todas las Semanas (Acumulativo)":
            view_week = None
            # Calendario inmediatamente tras selector
            self.render_calendar(st.session_state.calendar_year, st.session_state.calendar_month, view_week)
            st.caption("*Vista acumulativa: muestra progreso de todas las semanas entrenadas*")
        else:
            view_week = int(selected_view.split()[-1])
            # Calendario semanal inmediatamente tras selector
            self.render_week_calendar(view_week)
            week_view_info = self.get_week_info(view_week)
            st.caption(f"*Vista específica: Semana {view_week} · {week_view_info['level_name']} ({week_view_info['level_description']})*")
        if view_week is None:
            # Controles mensuales debajo del calendario (solo acumulativo)
            with st.expander("⚙️ Ajustes de Mes", expanded=False):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    year_options = list(range(current_date.year - 1, current_date.year + 2))
                    year_index = year_options.index(st.session_state.calendar_year) if st.session_state.calendar_year in year_options else 1
                    selected_year = st.selectbox("Año:", options=year_options, index=year_index, key="year_selector")
                    st.session_state.calendar_year = selected_year
                with col2:
                    month_names = [self.get_month_name_es(i) for i in range(1, 13)]
                    month_index = st.session_state.calendar_month - 1
                    selected_month_name = st.selectbox("Mes:", options=month_names, index=month_index, key="month_selector")
                    selected_month = month_names.index(selected_month_name) + 1
                    st.session_state.calendar_month = selected_month
                with col3:
                    col_prev, col_today, col_next = st.columns(3)
                    with col_prev:
                        if st.button("⬅️ Mes", key="btn_prev_month"):
                            if st.session_state.calendar_month == 1:
                                st.session_state.calendar_year -= 1
                                st.session_state.calendar_month = 12
                            else:
                                st.session_state.calendar_month -= 1
                            st.rerun()
                    with col_today:
                        now = datetime.datetime.now()
                        month_abbrs = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
                        label = f"📅 {now.day} {month_abbrs[now.month-1]}"
                        if st.button(label, key="calendar_today_btn", help="Ir al mes actual"):
                            st.session_state.calendar_year = now.year
                            st.session_state.calendar_month = now.month
                            st.rerun()
                    with col_next:
                        if st.button("Mes ➡️", key="btn_next_month"):
                            if st.session_state.calendar_month == 12:
                                st.session_state.calendar_year += 1
                                st.session_state.calendar_month = 1
                            else:
                                st.session_state.calendar_month += 1
                            st.rerun()
        # Información de semana actual
        current_week = st.session_state.get('current_week', 1)
        week_info = self.get_week_info(current_week)
        st.info(f"📅 **Semana Actual: {current_week}** - {week_info['level_name']} | {week_info['level_description']}")
        st.markdown("---")

        # Estadísticas generales
        st.subheader("📈 Estadísticas Generales")
        total_completed = 0
        months_data = []
        for i in range(6):
            date = current_date - datetime.timedelta(days=30 * i)
            stats = self.get_month_stats(date.year, date.month)
            total_completed += stats['completed']
            months_data.append({'Mes': f"{calendar.month_abbr[date.month]} {date.year}", 'Entrenamientos': stats['completed'], 'Tasa': stats['completion_rate']})
        months_data.reverse()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Entrenamientos Totales", self.progress_data.get('total_workouts', 0))
        with col2:
            selected_month_stats = self.get_month_stats(st.session_state.calendar_year, st.session_state.calendar_month)
            current_month_stats = self.get_month_stats(current_date.year, current_date.month)
            if st.session_state.calendar_year == current_date.year and st.session_state.calendar_month == current_date.month:
                st.metric("Este Mes", current_month_stats['completed'], f"{current_month_stats['completion_rate']:.1f}%")
            else:
                month_name = self.get_month_abbr_es(st.session_state.calendar_month)
                st.metric(f"{month_name} {st.session_state.calendar_year}", selected_month_stats['completed'], f"{selected_month_stats['completion_rate']:.1f}%")
        with col3:
            wk_info = self.get_week_info(st.session_state.current_week)
            st.metric("Nivel Actual", wk_info['level'], wk_info['level_name'])
        with col4:
            streak = self.calculate_current_streak()
            st.metric("Racha Actual", f"{streak} días", "🔥" if streak > 0 else "")
        st.subheader("💡 Consejos de Progreso")
        current_month_stats = self.get_month_stats(current_date.year, current_date.month)
            
        if current_month_stats['completion_rate'] >= 80:
            st.success("🎉 ¡Excelente! Mantienes una rutina muy consistente.")
        elif current_month_stats['completion_rate'] >= 60:
            st.info("👍 Buen progreso. Intenta ser más consistente para mejores resultados.")
        elif current_month_stats['completion_rate'] >= 40:
            st.warning("📈 Puedes mejorar. Intenta entrenar al menos 4 días por semana.")
        else:
            st.error("💪 ¡Es hora de retomar el ritmo! Cada entrenamiento cuenta.")
        st.info("""**Cómo interpretar el calendario:**\n- 🟢 Verde (100%): Entrenamiento completado\n- 🟡 Amarillo (80-99%): Casi completado\n- 🟠 Naranja (1-79%): Parcialmente completado\n- ⚪ Gris (0%): Sin entrenamientos\n- 🔵 Borde azul: Día actual\n- **Los porcentajes se calculan automáticamente** desde el Plan de Entrenamiento""")
