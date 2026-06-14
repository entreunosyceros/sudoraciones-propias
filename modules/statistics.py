"""
Módulo de Estadísticas
Contiene toda la lógica de la pestaña de estadísticas
"""
import pandas as pd
import plotly.express as px
import streamlit as st
import datetime
from .base_trainer import BaseTrainer


class StatisticsModule(BaseTrainer):
    """Módulo para gestionar las estadísticas"""
    
    # Diccionario de traducción de grupos musculares
    MUSCLE_GROUP_TRANSLATIONS = {
        'pecho': 'Pecho',
        'espalda': 'Espalda', 
        'hombros': 'Hombros',
        'brazos': 'Brazos',
        'piernas': 'Piernas',
        'gemelos': 'Gemelos',
        'abs': 'Abdominales',
        'abdominales': 'Abdominales',
        'cardio': 'Cardio'
    }
    
    def translate_muscle_group(self, group_name):
        """Traduce el nombre del grupo muscular al español"""
        return self.MUSCLE_GROUP_TRANSLATIONS.get(group_name.lower(), group_name.title())
    
    def filter_dates_from_program_start(self, completed_exercises):
        """Filtrar ejercicios solo desde la fecha de inicio del programa"""
        if not self.progress_data.get('program_start_date') or self.progress_data['program_start_date'] is None:
            return completed_exercises
        
        try:
            start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d')
            filtered_exercises = {}
            
            for date_str, exercises in completed_exercises.items():
                try:
                    exercise_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    # Solo incluir ejercicios desde la fecha de inicio del programa
                    if exercise_date >= start_date:
                        filtered_exercises[date_str] = exercises
                except ValueError:
                    # Si hay error al parsear fecha, incluir por compatibilidad
                    filtered_exercises[date_str] = exercises
            
            return filtered_exercises
        except ValueError:
            # Si hay error al parsear fecha de inicio, devolver todos
            return completed_exercises
    
    def _calculate_total_workouts_from_start(self) -> int:
        """Calcular total REAL de días de ENTRENAMIENTO completados (≥80%) ignorando días de descanso.

        Antes se contaban también días de descanso porque `completed_workouts` los incluye.
        Alineamos ahora con la lógica de la pestaña Progreso.
        """
        if 'completed_exercises' not in self.progress_data:
            return 0

        start_date = None
        if self.progress_data.get('program_start_date'):
            try:
                start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d').date()
            except ValueError:
                start_date = None

        total_training_days = 0
        for date_str in self.progress_data['completed_exercises'].keys():
            try:
                d = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue
            if start_date and d < start_date:
                continue
            stats = self._get_training_day_stats(date_str)
            if stats['is_rest_day']:
                continue
            if stats['percentage'] >= 80 and stats['total'] > 0:
                total_training_days += 1
        return total_training_days
    
    def _calculate_current_streak_from_start(self) -> int:
        """Calcular racha actual ignorando días de descanso (solo días de entrenamiento ≥80%)."""
        if 'completed_exercises' not in self.progress_data:
            return 0
        today = datetime.date.today()
        streak = 0
        for i in range(90):  # margen amplio
            check_date = today - datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            stats = self._get_training_day_stats(date_str)
            if stats['is_rest_day']:
                continue  # no afecta
            if stats['total'] == 0:  # día sin ejercicios planificados/registrados: rompe (salvo hoy incompleto)
                if i == 0:
                    continue
                break
            if stats['percentage'] >= 80:
                streak += 1
            else:
                if i == 0:
                    continue  # no rompe si hoy va incompleto
                break
        return streak
    
    def _calculate_longest_streak_from_start(self) -> int:
        """Calcular la racha más larga solo contando días de entrenamiento completos (≥80%), descansos ignorados."""
        if 'completed_exercises' not in self.progress_data:
            return 0
        # Reunir todas las fechas relevantes desde inicio
        dates = []
        start_date = None
        if self.progress_data.get('program_start_date'):
            try:
                start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d').date()
            except ValueError:
                start_date = None
        for date_str in self.progress_data['completed_exercises'].keys():
            try:
                d = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue
            if start_date and d < start_date:
                continue
            dates.append(d)
        if not dates:
            return 0
        dates_sorted = sorted(set(dates))
        # Iterar día a día desde inicio hasta hoy evaluando continuidad (descansos no cuentan ni rompen)
        today = datetime.date.today()
        if dates_sorted[-1] < today:
            # Añadir días vacíos posteriores para evaluar rachas cerradas
            pass
        max_streak = 0
        current_streak = 0
        # Construir set para acceso rápido
        date_set = set(dates_sorted)
        # Iterar sobre rango completo
        full_start = dates_sorted[0]
        full_end = today
        delta_days = (full_end - full_start).days
        for i in range(delta_days + 1):
            day = full_start + datetime.timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            stats = self._get_training_day_stats(date_str)
            if stats['is_rest_day']:
                # descanso: no suma ni rompe
                continue
            if stats['total'] == 0:
                # día planificado sin ejercicios -> rompe racha actual
                current_streak = 0
                continue
            if stats['percentage'] >= 80:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
            else:
                current_streak = 0
        return max_streak

    # ------------------------------------------------------------------
    # HELPERS ACTUALIZADOS PARA NUEVA LÓGICA
    # ------------------------------------------------------------------
    def _get_training_day_stats(self, date_str: str) -> dict:
        """Obtener stats de un día usando la semana correcta.
        Usa exercise_weeks si existe; si no, intenta mapeo calendario.
        """
        week_number = self.progress_data.get('exercise_weeks', {}).get(date_str)
        if not week_number:
            week_number = self.get_calendar_week_for_date(date_str)
        try:
            return self.get_day_completion_stats_internal(date_str, week_number)
        except Exception:
            return {'completed': 0, 'total': 0, 'percentage': 0, 'is_rest_day': True}
    
    def _calculate_total_exercises_from_start(self) -> int:
        """Calcular total de ejercicios completados desde la fecha de inicio"""
        if 'completed_exercises' not in self.progress_data:
            return 0
        
        # Filtrar ejercicios desde la fecha de inicio del programa
        filtered_exercises = self.filter_dates_from_program_start(self.progress_data['completed_exercises'])
        
        total_exercises = 0
        for date_str, exercises in filtered_exercises.items():
            for exercise_id, completed in exercises.items():
                if completed:
                    total_exercises += 1
        
        return total_exercises
    
    def _calculate_weeks_elapsed_from_start(self) -> float:
        """Calcular las semanas transcurridas desde la fecha de inicio del programa"""
        if 'program_start_date' not in self.progress_data:
            return 1.0  # Fallback: al menos 1 semana
        
        try:
            start_date = datetime.datetime.strptime(self.progress_data['program_start_date'], '%Y-%m-%d').date()
            current_date = datetime.datetime.now().date()
            
            # Calcular diferencia en días y convertir a semanas
            days_elapsed = (current_date - start_date).days
            weeks_elapsed = max(days_elapsed / 7.0, 1.0)  # Mínimo 1 semana
            
            return weeks_elapsed
        except ValueError:
            return 1.0  # Fallback

    def render_statistics_tab(self):
        """Renderizar pestaña de estadísticas"""
        st.header("📈 Estadísticas Detalladas")
        
        # Asegurar datos frescos
        self.reload_progress_data()
        
        # Mostrar información sobre el período de cálculo
        start_date_display = self.get_program_start_date_display()
        if start_date_display:
            st.info(f"📅 **Estadísticas calculadas desde:** {start_date_display} (fecha de inicio del programa)")
        else:
            st.warning("⚠️ No se ha configurado fecha de inicio del programa. Las estadísticas incluyen todos los datos.")
        
        # Mostrar estadísticas principales acumulativas
        st.subheader("📊 Estadísticas Principales Acumulativas")

        # Calcular estadísticas reales (nueva lógica alineada con pestaña Progreso)
        total_workouts_real = self._calculate_total_workouts_from_start()  # solo días entrenamiento ≥80%
        current_streak_real = self._calculate_current_streak_from_start()  # ignora descansos
        longest_streak_real = self._calculate_longest_streak_from_start()  # ignora descansos
        total_exercises_completed_real = self._calculate_total_exercises_from_start()
        current_week_real = self.get_auto_detected_week()  # Usar semana auto-detectada

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏋️ Días Entrenamiento Completos", total_workouts_real)
        with col2:
            st.metric("🔥 Racha Actual", f"{current_streak_real} días")
        with col3:
            st.metric("🏆 Racha Máxima", f"{longest_streak_real} días")
        with col4:
            st.metric("📅 Semana Actual", f"{current_week_real}/20")

        col5, col6 = st.columns(2)
        with col5:
            st.metric("✅ Ejercicios Completados", total_exercises_completed_real)
        with col6:
            weeks_elapsed = self._calculate_weeks_elapsed_from_start()
            if weeks_elapsed > 0:
                avg_per_week = total_workouts_real / weeks_elapsed
                st.metric("📈 Promedio/Semana", f"{avg_per_week:.1f}")
            else:
                st.metric("📈 Promedio/Semana", "0.0")

        st.markdown("---")
        
        # Indicadores semanales de coherencia
        st.subheader("🎯 Coherencia Semanal")
        st.caption(
            "Cruza entrenamiento, nutrición y peso para evaluar si avanzas hacia tu objetivo. "
            "Todos los valores energéticos son estimaciones."
        )
        current_week_real = self.get_auto_detected_week()
        summary = self.get_weekly_coherence_summary(current_week_real)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if summary['training_planned']:
                st.metric("Entrenamientos", f"{summary['training_completed']}/{summary['training_planned']}")
            else:
                st.metric("Entrenamientos", "—")
        with c2:
            avg_cal = summary['avg_calories']
            st.metric("Calorías medias", f"{avg_cal:.0f} kcal" if avg_cal else "—")
        with c3:
            avg_bal = summary['avg_balance']
            if avg_bal is not None:
                sign = "+" if avg_bal > 0 else ""
                st.metric("Balance medio est.", f"{sign}{avg_bal:.0f} kcal/d")
            else:
                st.metric("Balance medio est.", "—")
        with c4:
            if summary['weight_start'] and summary['weight_end']:
                st.metric("Peso", f"{summary['weight_start']:.1f}→{summary['weight_end']:.1f} kg")
            elif summary['weight_end']:
                st.metric("Peso", f"{summary['weight_end']:.1f} kg")
            else:
                st.metric("Peso", "—")

        st.info(f"**Semana {summary['week_number']} — Tendencia:** {summary['trend']}")
        st.caption("Más detalle en 🍎 Nutrición → Indicadores Semanales")

        st.markdown("---")
        
        # Análisis de completado vs disponible por grupo
        exercise_counts = {}
        completed_counts = {}
        
        # Contar ejercicios disponibles por grupo
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            exercise_counts[muscle_group] = len(exercises)
            completed_counts[muscle_group] = 0
        
        # Contar ejercicios completados por grupo (evitando duplicados)
        # SOLO desde la fecha de inicio del programa
        if 'completed_exercises' in self.progress_data:
            # Filtrar solo ejercicios desde la fecha de inicio del programa
            filtered_exercises = self.filter_dates_from_program_start(self.progress_data['completed_exercises'])
            
            # Crear diccionario para contar exercise_id únicos por grupo
            unique_completions_by_group = {}
            
            for date_str, exercises in filtered_exercises.items():
                for exercise_id, completed in exercises.items():
                    if completed:
                        parts = exercise_id.split('_')
                        if len(parts) >= 2:
                            muscle_group = parts[0]
                            if muscle_group in completed_counts:
                                # Crear clave única: exercise_id + fecha
                                unique_key = f"{exercise_id}_{date_str}"
                                if muscle_group not in unique_completions_by_group:
                                    unique_completions_by_group[muscle_group] = set()
                                unique_completions_by_group[muscle_group].add(unique_key)
            
            # Contar completions únicos por grupo
            for muscle_group in completed_counts.keys():
                if muscle_group in unique_completions_by_group:
                    completed_counts[muscle_group] = len(unique_completions_by_group[muscle_group])
        
        if exercise_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparación completados vs disponibles
                comparison_data = []
                for group in exercise_counts.keys():
                    total_available = exercise_counts[group] * 20  # Aproximado para 20 semanas
                    completed = completed_counts[group]
                    completion_rate = (completed / total_available * 100) if total_available > 0 else 0
                    
                    comparison_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Completados': completed,
                        'Disponibles (20 sem)': total_available,
                        'Tasa Completado (%)': round(completion_rate, 1)
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                
                fig_comparison = px.bar(df_comparison, x='Grupo', y=['Completados', 'Disponibles (20 sem)'],
                                      title='Ejercicios Completados vs Disponibles por Grupo',
                                      barmode='group',
                                      color_discrete_map={'Completados': '#2ecc71', 'Disponibles (20 sem)': '#ecf0f1'})
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            with col2:
                # Ranking de grupos más y menos entrenados
                if completed_counts and sum(completed_counts.values()) > 0:
                    sorted_groups = sorted(completed_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    st.markdown("#### 🏆 **Grupos Más Entrenados**")
                    for i, (group, count) in enumerate(sorted_groups[:3]):
                        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                        st.markdown(f"{medal} **{self.translate_muscle_group(group)}**: {count} veces completado")
                    
                    st.markdown("#### 📉 **Grupos Menos Entrenados**")
                    for i, (group, count) in enumerate(reversed(sorted_groups[-3:])):
                        warning = "⚠️" if count < max(completed_counts.values()) * 0.5 else "📝"
                        st.markdown(f"{warning} **{self.translate_muscle_group(group)}**: {count} veces completado")
                else:
                    st.info("🏋️ ¡Comienza a entrenar para ver tus estadísticas!")
        
        st.markdown("---")
        
        # Análisis de progreso temporal
        st.subheader("📊 Análisis de Progreso Temporal")
        
        if 'completed_workouts' in self.progress_data:
            # Preparar datos de progreso mensual (solo días entrenamiento ≥80%)
            monthly_counter = {}
            for date_str in self.progress_data.get('completed_exercises', {}).keys():
                stats = self._get_training_day_stats(date_str)
                if stats['is_rest_day'] or stats['total'] == 0:
                    continue
                if stats['percentage'] >= 80:
                    month_key = date_str[:7]
                    monthly_counter[month_key] = monthly_counter.get(month_key, 0) + 1
            monthly_data = []
            for month_key, count in monthly_counter.items():
                year, month = month_key.split('-')
                monthly_data.append({
                    'Mes': f"{month}/{year}",
                    'Entrenamientos': count,
                    'Año': int(year),
                    'Mes_Num': int(month)
                })
            if monthly_data:
                df_monthly = pd.DataFrame(monthly_data).sort_values(['Año', 'Mes_Num'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de líneas de progreso mensual
                    fig_line = px.line(df_monthly, x='Mes', y='Entrenamientos',
                                     title='Progreso de Entrenamientos por Mes',
                                     markers=True)
                    fig_line.update_traces(line=dict(color='#e74c3c', width=3))
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with col2:
                    # Gráfico de barras de entrenamientos por mes
                    fig_monthly_bar = px.bar(df_monthly, x='Mes', y='Entrenamientos',
                                           title='Entrenamientos Completados por Mes',
                                           color='Entrenamientos',
                                           color_continuous_scale='blues')
                    st.plotly_chart(fig_monthly_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Análisis detallado de entrenamientos por grupo
        st.subheader("💪 Análisis de Rendimiento por Grupo")
        
        # Calcular estadísticas avanzadas por grupo
        # SOLO desde la fecha de inicio del programa
        muscle_group_detailed = {}
        
        if 'completed_exercises' in self.progress_data:
            # Filtrar solo ejercicios desde la fecha de inicio del programa
            filtered_exercises = self.filter_dates_from_program_start(self.progress_data['completed_exercises'])
            
            for date_str, exercises in filtered_exercises.items():
                for exercise_id, completed in exercises.items():
                    if completed:
                        parts = exercise_id.split('_')
                        if len(parts) >= 2:
                            muscle_group = parts[0]
                            if muscle_group not in muscle_group_detailed:
                                muscle_group_detailed[muscle_group] = {
                                    'total_completados': 0,
                                    'dias_entrenados': set(),
                                    'ejercicios_unicos': set()
                                }
                            muscle_group_detailed[muscle_group]['total_completados'] += 1
                            muscle_group_detailed[muscle_group]['dias_entrenados'].add(date_str)
                            muscle_group_detailed[muscle_group]['ejercicios_unicos'].add(exercise_id)
        
        if muscle_group_detailed:
            col1, col2 = st.columns(2)
            
            with col1:
                # Frecuencia de entrenamiento por grupo (días únicos)
                frequency_data = []
                for group, stats in muscle_group_detailed.items():
                    frequency_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Días Entrenados': len(stats['dias_entrenados']),
                        'Ejercicios Únicos': len(stats['ejercicios_unicos']),
                        'Total Completados': stats['total_completados']
                    })
                
                df_frequency = pd.DataFrame(frequency_data)
                df_frequency = df_frequency.sort_values('Días Entrenados', ascending=True)
                
                fig_frequency = px.bar(df_frequency, x='Días Entrenados', y='Grupo',
                                     title='Frecuencia de Entrenamiento (Días Únicos)',
                                     orientation='h',
                                     color='Días Entrenados',
                                     color_continuous_scale='greens',
                                     text='Días Entrenados')
                fig_frequency.update_traces(textposition='outside')
                st.plotly_chart(fig_frequency, use_container_width=True)
            
            with col2:
                # Intensidad promedio por grupo (completados por día)
                intensity_data = []
                for group, stats in muscle_group_detailed.items():
                    dias_entrenados = len(stats['dias_entrenados'])
                    intensity = stats['total_completados'] / dias_entrenados if dias_entrenados > 0 else 0
                    intensity_data.append({
                        'Grupo': self.translate_muscle_group(group),
                        'Intensidad Promedio': round(intensity, 2),
                        'Total Completados': stats['total_completados']
                    })
                
                df_intensity = pd.DataFrame(intensity_data)
                df_intensity = df_intensity.sort_values('Intensidad Promedio', ascending=False)
                
                fig_intensity = px.scatter(df_intensity, x='Intensidad Promedio', y='Grupo',
                                         size='Total Completados',
                                         title='Intensidad Promedio por Grupo (Ejercicios/Día)',
                                         color='Intensidad Promedio',
                                         color_continuous_scale='oranges')
                st.plotly_chart(fig_intensity, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla de ejercicios completa
        st.subheader("📋 Lista Completa de Ejercicios")
        current_week = st.session_state.get('current_week', 1)
        st.caption(f"Series y repeticiones mostradas según la **Semana {current_week}** del programa (progresión automática).")
        
        all_exercises = []
        for muscle_group, exercises in self.config.get('exercises', {}).items():
            for exercise in exercises:
                # Usar la nueva función mejorada para contar completados
                completed_count = self.get_exercise_completion_count(muscle_group, exercise['name'])
                display_sets, display_reps = self.get_exercise_progression(exercise, current_week)
                
                all_exercises.append({
                    'Grupo': self.translate_muscle_group(muscle_group),
                    'Ejercicio': exercise['name'],
                    'Series': display_sets,
                    'Repeticiones': display_reps,
                    'Video': '✅' if exercise.get('youtube_url') else '❌',
                    'Veces Completado': completed_count
                })
        
        if all_exercises:
            df_all = pd.DataFrame(all_exercises)
            
            # Opciones de filtrado
            col1, col2 = st.columns(2)
            with col1:
                selected_groups = st.multiselect(
                    "Filtrar por grupo muscular:",
                    options=df_all['Grupo'].unique(),
                    default=df_all['Grupo'].unique()
                )
            
            with col2:
                show_only_with_video = st.checkbox("Solo mostrar ejercicios con video", value=False)
            
            # Aplicar filtros
            df_filtered = df_all[df_all['Grupo'].isin(selected_groups)]
            if show_only_with_video:
                df_filtered = df_filtered[df_filtered['Video'] == '✅']
            
            # Ordenar por veces completado (descendente)
            df_filtered = df_filtered.sort_values('Veces Completado', ascending=False)
            
            st.dataframe(df_filtered, use_container_width=True)
            
            # Estadísticas resumen de la tabla
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ejercicios", len(df_filtered))
            with col2:
                st.metric("Con Video", len(df_filtered[df_filtered['Video'] == '✅']))
            with col3:
                st.metric("Sin Video", len(df_filtered[df_filtered['Video'] == '❌']))
            with col4:
                total_completions = df_filtered['Veces Completado'].sum()
                st.metric("Total Completados", total_completions)
        
        st.markdown("---")
        
        # Recomendaciones basadas en datos
        st.subheader("🎯 Recomendaciones Personalizadas")
        
        recommendations = []
        
        # Análisis de grupos menos entrenados
        if muscle_group_detailed:
            # Obtener conteos simples para las recomendaciones
            simple_counts = {group: stats['total_completados'] for group, stats in muscle_group_detailed.items()}
            min_trained = min(simple_counts.values())
            max_trained = max(simple_counts.values())
            
            for group, count in simple_counts.items():
                if count == min_trained and min_trained < max_trained * 0.7:
                    recommendations.append(f"💡 **{self.translate_muscle_group(group)}**: Grupo menos entrenado. Considera aumentar la frecuencia.")
        elif completed_counts and sum(completed_counts.values()) > 0:
            # Usar los datos de la primera sección como respaldo
            min_trained = min(completed_counts.values())
            max_trained = max(completed_counts.values())
            
            for group, count in completed_counts.items():
                if count == min_trained and min_trained < max_trained * 0.7:
                    recommendations.append(f"💡 **{self.translate_muscle_group(group)}**: Grupo menos entrenado. Considera aumentar la frecuencia.")
        
        # Análisis de consistencia
        if 'completed_workouts' in self.progress_data:
            total_months = len(self.progress_data['completed_workouts'])
            if total_months > 1:
                monthly_avg = sum(len(dates) for dates in self.progress_data['completed_workouts'].values()) / total_months
                if monthly_avg < 8:
                    recommendations.append(f"📈 **Consistencia**: Promedio de {monthly_avg:.1f} entrenamientos/mes. Meta recomendada: 12+ entrenamientos/mes.")
        
        # Análisis de videos
        total_exercises = sum(len(exercises) for exercises in self.config.get('exercises', {}).values())
        exercises_with_video = sum(1 for muscle_group, exercises in self.config.get('exercises', {}).items() 
                                 for exercise in exercises if exercise.get('youtube_url'))
        
        if exercises_with_video < total_exercises * 0.8:
            recommendations.append(f"🎥 **Videos**: Solo {exercises_with_video}/{total_exercises} ejercicios tienen video. Agregar más videos mejorará la técnica.")
        
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("🎉 ¡Excelente! Tu entrenamiento está bien balanceado y consistente.")
        
        # Datos técnicos
        with st.expander("🔧 Información Técnica"):
            st.markdown("### Datos del Sistema")
            st.json({
                "Total ejercicios configurados": sum(len(exercises) for exercises in self.config.get('exercises', {}).values()),
                "Grupos musculares": len(self.config.get('exercises', {})),
                "Semanas de progreso disponibles": 20,
                "Ejercicios con video": exercises_with_video,
                "Datos de progreso guardados": len(self.progress_data.get('completed_exercises', {})),
                "Entrenamientos totales": self.progress_data.get('total_workouts', 0)
            })
