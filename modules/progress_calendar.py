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
        """Estadísticas de un día usando el plan de la semana indicada (denominador = ejercicios planificados)."""
        if filter_week is None:
            filter_week = int(st.session_state.get('current_week', 1))

        stats = self._get_training_plan_module().get_day_completion_stats(date_str, filter_week)
        stats['is_empty_day'] = (
            not stats.get('is_rest_day')
            and stats.get('total', 0) > 0
            and stats.get('completed', 0) == 0
            and date_str not in self.progress_data.get('completed_exercises', {})
        )
        return stats
    
    def get_month_abbr_es(self, month: int) -> str:
        """Obtener abreviación del mes en español"""
        return self.MONTH_ABBR_ES.get(month, f'M{month}')

    def get_month_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Estadísticas del mes: solo días de entrenamiento planificados (≥80% = completado).

        Alineado con Estadísticas (no cuenta descansos ni diluye el % con todos los días del mes).
        """
        _, last_day = calendar.monthrange(year, month)
        training_days = 0
        completed_training = 0
        completed_dates: list[str] = []

        for day in range(1, last_day + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            if self.is_future_date(date_str):
                continue
            day_stats = self.get_day_completion_stats_accumulated(date_str)
            if day_stats.get('is_rest_day'):
                continue
            if day_stats.get('total', 0) <= 0:
                continue
            training_days += 1
            if day_stats.get('percentage', 0) >= 80:
                completed_training += 1
                completed_dates.append(date_str)

        return {
            'completed': completed_training,
            'total_days': training_days,
            'completion_rate': (completed_training / training_days * 100) if training_days > 0 else 0,
            'completed_dates': completed_dates,
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

            if day_stats.get('is_rest_day'):
                continue
            if day_stats.get('total', 0) > 0:
                total_days += 1
                total_exercises += day_stats.get('total', 0)
                completed_exercises += day_stats.get('completed', 0)
                if day_stats.get('percentage', 0) >= 80:
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
        """Semana del programa a la que pertenece una fecha (fuente canónica)."""
        return self.get_training_week_for_date(date_str)

    def get_day_completion_stats(self, date_str: str, week_number: int | None = None) -> Dict[str, Any]:
        """Estadísticas de finalización para un día según la semana del programa."""
        if week_number is None:
            week_number = self.get_training_week_for_date(date_str)

        stats = self._get_training_plan_module().get_day_completion_stats(date_str, week_number)
        stats['calendar_week'] = week_number
        stats['is_empty_day'] = (
            not stats.get('is_rest_day')
            and stats.get('total', 0) > 0
            and stats.get('completed', 0) == 0
            and date_str not in self.progress_data.get('completed_exercises', {})
        )
        return stats

    # Wrapper simple para la vista acumulativa (todas semanas) reutilizando la lógica existente
    def get_day_completion_stats_accumulated(self, date_str: str) -> Dict[str, Any]:
        """Obtener estadísticas combinadas para un día (acumulativo).

        La idea: identificar semana correspondiente y reutilizar la lógica del módulo de plan.
        """
        if self.is_future_date(date_str):
            return self.get_pending_day_stats(is_future=True)
        # Si hay ejercicios marcados ese día, mostrarlos aunque la fecha quede
        # «antes» del inicio del calendario (evita perder historial al reajustar fechas).
        if self.is_before_program_start(date_str):
            if date_str not in self.progress_data.get('completed_exercises', {}):
                return self.get_pending_day_stats()

        week_num = self.get_training_week_for_date(date_str)
        return self._get_training_plan_module().get_day_completion_stats(date_str, week_num)

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
        - Día con entrenamiento planificado y ≥80% completado suma racha.
        - Día con entrenamiento planificado incompleto ROMPE la racha.
        """
        self.reload_progress_data()
        today = datetime.date.today()
        streak = 0
        for i in range(60):
            check_date = today - datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            week_num = self.get_training_week_for_date(date_str)
            day_stats = self._get_training_plan_module().get_day_completion_stats(date_str, week_num)
            if day_stats.get('is_rest_day'):
                continue
            total = day_stats.get('total', 0)
            completed = day_stats.get('completed', 0)
            percentage = (completed / total * 100) if total > 0 else 0
            completed_day = (total > 0) and (percentage >= 80)
            if completed_day:
                streak += 1
            else:
                if i == 0:
                    continue
                break
        return streak

    def _count_recent_training_days(self, days: int = 7) -> Dict[str, int]:
        """Días de entrenamiento planificados / completados (≥80%) en la ventana reciente."""
        today = datetime.date.today()
        planned = 0
        completed = 0
        partial = 0
        for i in range(days):
            check_date = today - datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            week_num = self.get_training_week_for_date(date_str)
            day_stats = self._get_training_plan_module().get_day_completion_stats(date_str, week_num)
            if day_stats.get('is_rest_day') or day_stats.get('total', 0) <= 0:
                continue
            planned += 1
            pct = day_stats.get('percentage', 0)
            if pct >= 80:
                completed += 1
            elif pct > 0:
                partial += 1
        return {'planned': planned, 'completed': completed, 'partial': partial}

    def get_progress_tips(
        self,
        *,
        total_workouts: int,
        streak: int,
        month_stats: Dict[str, Any],
        week_number: int,
    ) -> list[Dict[str, str]]:
        """Consejos contextuales según progreso acumulado (máx. 3, distintos)."""
        tips: list[Dict[str, str]] = []
        week_info = self.get_week_info(week_number)
        level = week_info.get('level', 1)
        rate = float(month_stats.get('completion_rate') or 0)
        month_done = int(month_stats.get('completed') or 0)
        month_planned = int(month_stats.get('total_days') or 0)
        recent = self._count_recent_training_days(7)
        today_week = self.get_training_week_for_date(datetime.date.today().strftime('%Y-%m-%d'))
        auto_week = self.get_auto_detected_week()

        if self.is_maintenance_mode():
            tips.append({
                'level': 'info',
                'text': (
                    "💪 **Mantener forma:** la sesión prioriza ejercicios menos hechos. "
                    "Completa al ≥80% para ir equilibrando el catálogo."
                ),
            })

        # Consistencia del mes
        if month_planned == 0 and total_workouts == 0:
            tips.append({
                'level': 'info',
                'text': "🏁 Empieza marcando los ejercicios de **hoy** en Plan de Entrenamiento. El calendario se irá coloreando solo.",
            })
        elif rate >= 85:
            tips.append({
                'level': 'success',
                'text': f"🎉 Mes excelente: **{month_done}/{month_planned}** días de entrenamiento (≥80%). Mantén el ritmo.",
            })
        elif rate >= 60:
            tips.append({
                'level': 'info',
                'text': f"👍 Buen mes (**{rate:.0f}%**). Si cierras **1-2 días** más al ≥80%, subes al siguiente tramo de consistencia.",
            })
        elif rate >= 35:
            tips.append({
                'level': 'warning',
                'text': f"📈 Llevas **{month_done}** de **{month_planned}** días del mes. Prioriza terminar la sesión de hoy al completo.",
            })
        else:
            tips.append({
                'level': 'error',
                'text': "💪 El mes va flojo. Un día completo (≥80%) ya cambia la tendencia: ve a **Sesión de hoy**.",
            })

        # Racha
        if streak >= 10:
            tips.append({
                'level': 'success',
                'text': f"🔥 Racha de **{streak}** días de entrenamiento. No la rompas: hoy cuenta aunque sea una sesión corta pero completa.",
            })
        elif streak >= 4:
            tips.append({
                'level': 'success',
                'text': f"🔥 Llevas **{streak}** días seguidos (≥80%). En 3 más tendrás una racha sólida de una semana+.",
            })
        elif streak == 0 and total_workouts > 0:
            tips.append({
                'level': 'warning',
                'text': "⏳ Sin racha activa. Completa el próximo día de entrenamiento al ≥80% para reiniciarla.",
            })

        # Volumen acumulado
        if total_workouts >= 100:
            tips.append({
                'level': 'success',
                'text': f"🏆 **{total_workouts}** días de entrenamiento acumulados. Nivel de constancia alto: cuida técnica y recuperación.",
            })
        elif total_workouts >= 40:
            tips.append({
                'level': 'info',
                'text': f"📊 Llevas **{total_workouts}** días completos. Revisa Estadísticas para ver qué grupos van más rezagados.",
            })
        elif 1 <= total_workouts < 10:
            tips.append({
                'level': 'info',
                'text': f"🌱 Primeros **{total_workouts}** días registrados. La clave ahora es la frecuencia, no la intensidad máxima.",
            })

        # Nivel / semana del programa
        if week_number in (5, 9, 13, 17):
            tips.append({
                'level': 'info',
                'text': f"🆙 Estás en el arranque del **{week_info.get('level_name', 'nuevo nivel')}**. Revisa series/reps: sube el volumen con calma.",
            })
        elif level >= 3 and rate < 50 and total_workouts > 20:
            tips.append({
                'level': 'warning',
                'text': f"⚖️ Nivel **{week_info.get('level_name')}** con poca consistencia este mes. Mejor consolidar semanas que saltar adelante.",
            })

        if auto_week > today_week + 1:
            tips.append({
                'level': 'info',
                'text': f"🎯 Tu progreso sugiere la **Semana {auto_week}**, pero el calendario marca la **{today_week}**. Usa «Auto-detectada» solo si quieres adelantar la vista.",
            })

        # Últimos 7 días
        if recent['partial'] >= 2:
            tips.append({
                'level': 'warning',
                'text': f"🟠 En 7 días tienes **{recent['partial']}** sesiones parciales. Acabar al ≥80% pesa más que empezar muchos días al 40%.",
            })
        elif recent['planned'] >= 3 and recent['completed'] == recent['planned']:
            tips.append({
                'level': 'success',
                'text': f"✅ Últimos 7 días: **{recent['completed']}/{recent['planned']}** días de entrenamiento cerrados. Muy buena semana reciente.",
            })
        elif recent['planned'] >= 2 and recent['completed'] == 0:
            tips.append({
                'level': 'error',
                'text': "📭 En la última semana no hay ningún día ≥80%. Retoma con la sesión de hoy, aunque sea el mínimo del plan.",
            })

        # Priorizar diversidad: como máximo 3 tips
        priority = {'error': 0, 'warning': 1, 'success': 2, 'info': 3}
        tips.sort(key=lambda t: priority.get(t['level'], 9))
        seen_levels: set[str] = set()
        selected: list[Dict[str, str]] = []
        for tip in tips:
            # Evitar dos del mismo tono salvo que aún queden huecos
            if tip['level'] in seen_levels and len(selected) >= 1:
                continue
            selected.append(tip)
            seen_levels.add(tip['level'])
            if len(selected) >= 3:
                break
        if len(selected) < 2:
            for tip in tips:
                if tip not in selected:
                    selected.append(tip)
                if len(selected) >= 2:
                    break
        return selected[:3]

    def _render_progress_tips(self, tips: list[Dict[str, str]]) -> None:
        """Mostrar consejos de progreso."""
        st.subheader("💡 Consejos de Progreso")
        if not tips:
            st.info("Marca entrenamientos para recibir consejos personalizados.")
            return
        render = {
            'success': st.success,
            'info': st.info,
            'warning': st.warning,
            'error': st.error,
        }
        for tip in tips:
            render.get(tip['level'], st.info)(tip['text'])

    def render_progress_tab(self):
        """Renderizar pestaña de progreso con calendario"""
        st.header("📊 Tu Progreso de Entrenamiento")

        current_date = datetime.datetime.now()

        if 'calendar_year' not in st.session_state:
            st.session_state.calendar_year = current_date.year
        if 'calendar_month' not in st.session_state:
            st.session_state.calendar_month = current_date.month

        # --- Resumen arriba (métricas + consejos) ---
        current_week = st.session_state.get('current_week', 1)
        week_info = self.get_week_info(current_week)
        st.info(f"📅 **Semana Actual: {current_week}** - {week_info['level_name']} | {week_info['level_description']}")

        self.update_completed_workouts()
        total_workouts = int(self.progress_data.get('total_workouts', 0) or 0)
        current_month_stats = self.get_month_stats(current_date.year, current_date.month)
        selected_month_stats = self.get_month_stats(
            st.session_state.calendar_year, st.session_state.calendar_month
        )
        streak = self.calculate_current_streak()

        st.subheader("📈 Resumen")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Días entrenamiento", total_workouts)
        with col2:
            rate_help = "% de días de entrenamiento del mes (≥80%)"
            if (
                st.session_state.calendar_year == current_date.year
                and st.session_state.calendar_month == current_date.month
            ):
                st.metric(
                    "Este Mes",
                    current_month_stats['completed'],
                    f"{current_month_stats['completion_rate']:.1f}%",
                    help=rate_help,
                )
            else:
                month_name = self.get_month_abbr_es(st.session_state.calendar_month)
                st.metric(
                    f"{month_name} {st.session_state.calendar_year}",
                    selected_month_stats['completed'],
                    f"{selected_month_stats['completion_rate']:.1f}%",
                    help=rate_help,
                )
        with col3:
            st.metric("Nivel Actual", week_info['level'], week_info['level_name'])
        with col4:
            st.metric("Racha Actual", f"{streak} días", "🔥" if streak > 0 else "")

        tips = self.get_progress_tips(
            total_workouts=total_workouts,
            streak=streak,
            month_stats=current_month_stats,
            week_number=current_week,
        )
        self._render_progress_tips(tips)

        st.markdown("---")

        # --- Calendario ---
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
            self.render_calendar(st.session_state.calendar_year, st.session_state.calendar_month, view_week)
            st.caption("*Vista acumulativa: muestra progreso de todas las semanas entrenadas*")
        else:
            view_week = int(selected_view.split()[-1])
            self.render_week_calendar(view_week)
            week_view_info = self.get_week_info(view_week)
            st.caption(
                f"*Vista específica: Semana {view_week} · "
                f"{week_view_info['level_name']} ({week_view_info['level_description']})*"
            )
        if view_week is None:
            with st.expander("⚙️ Ajustes de Mes", expanded=False):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    year_options = list(range(current_date.year - 1, current_date.year + 2))
                    year_index = (
                        year_options.index(st.session_state.calendar_year)
                        if st.session_state.calendar_year in year_options
                        else 1
                    )
                    selected_year = st.selectbox(
                        "Año:", options=year_options, index=year_index, key="year_selector"
                    )
                    st.session_state.calendar_year = selected_year
                with col2:
                    month_names = [self.get_month_name_es(i) for i in range(1, 13)]
                    month_index = st.session_state.calendar_month - 1
                    selected_month_name = st.selectbox(
                        "Mes:", options=month_names, index=month_index, key="month_selector"
                    )
                    st.session_state.calendar_month = month_names.index(selected_month_name) + 1
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
                        month_abbrs = [
                            "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                            "JUL", "AGO", "SEP", "OCT", "NOV", "DIC",
                        ]
                        label = f"📅 {now.day} {month_abbrs[now.month - 1]}"
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

        with st.expander("📖 Cómo interpretar el calendario", expanded=False):
            st.markdown(
                "- 🟢 Verde (100%): Entrenamiento completado\n"
                "- 🟡 Amarillo (80-99%): Casi completado\n"
                "- 🟠 Naranja (1-79%): Parcialmente completado\n"
                "- ⚪ Gris (0%): Sin entrenamientos\n"
                "- 🔵 Borde azul: Día actual\n"
                "- Los porcentajes se calculan desde el Plan de Entrenamiento"
            )