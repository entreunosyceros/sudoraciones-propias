"""
Sudoraciones Propias - Aplicación Principal
Sistema de entrenamiento modularizado por pestañas con mapeo calendario
"""
import os
import sys
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parent
os.chdir(_APP_ROOT)
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))
os.environ.setdefault('SUDORACIONES_APP_ROOT', str(_APP_ROOT))

import streamlit as st

# Configuración inicial de Streamlit
st.set_page_config(
    page_title="💪 Sudoraciones Propias",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos
from modules.base_trainer import BaseTrainer
from modules.training_plan import TrainingPlanModule
from modules.progress_calendar import ProgressModule
from modules.statistics import StatisticsModule
from modules.info import InfoModule
from modules.exercise_library import ExerciseLibraryModule
from modules.nutrition import NutritionModule

# CSS personalizado para mejorar el diseño 
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .exercise-card {
        background: white;
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .rest-day {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: #2d3436;
    }
</style>
""", unsafe_allow_html=True)

# Script JavaScript para traducir la interfaz de Streamlit al español
st.markdown("""
<script>
// Diccionario de traducciones inglés -> español
const translations = {
    // Menú principal y tres puntos
    'Deploy': 'Implementar',
    'Share': 'Compartir',
    'Settings': 'Configuración',
    'Rerun': 'Ejecutar de nuevo',
    'Stop': 'Detener',
    'Clear cache': 'Limpiar caché',
    'Record a screencast': 'Grabar pantalla',
    'About': 'Acerca de',
    'View fullscreen': 'Ver pantalla completa',
    'Report a bug': 'Reportar error',
    'Get help': 'Obtener ayuda',
    'Made with Streamlit': 'Hecho con Streamlit',
    
    // Elementos de interfaz
    'Running': 'Ejecutándose',
    'Please wait...': 'Por favor espera...',
    'Connecting': 'Conectando',
    'Connection error': 'Error de conexión',
    'Download': 'Descargar',
    'Full screen': 'Pantalla completa',
    'Running...': 'Ejecutándose...'
};

// Función para traducir elementos
function translateElements() {
    // Traducir elementos con atributo title
    document.querySelectorAll('[title]').forEach(element => {
        const title = element.getAttribute('title');
        if (translations[title]) {
            element.setAttribute('title', translations[title]);
        }
    });
    
    // Traducir texto de elementos específicos
    document.querySelectorAll('button, span, div').forEach(element => {
        const text = element.textContent?.trim();
        if (text && translations[text]) {
            element.textContent = translations[text];
        }
    });
    
    // Traducir placeholder de inputs
    document.querySelectorAll('input[placeholder]').forEach(element => {
        const placeholder = element.getAttribute('placeholder');
        if (translations[placeholder]) {
            element.setAttribute('placeholder', translations[placeholder]);
        }
    });
}

// Ejecutar traducción cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', translateElements);

// Observar cambios en el DOM para traducir elementos dinámicos
const observer = new MutationObserver(() => {
    translateElements();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Traducir elementos existentes
translateElements();
</script>
""", unsafe_allow_html=True)


class ModernHeavyDutyTrainer:
    """Aplicación principal coordinadora con mapeo calendario"""
    
    def __init__(self):
        """Inicializar la aplicación modular"""
        # Crear instancias de todos los módulos
        self.base_trainer = BaseTrainer()
        self.training_module = TrainingPlanModule()
        self.progress_module = ProgressModule()
        self.statistics_module = StatisticsModule()
        self.info_module = InfoModule()
        self.exercise_library_module = ExerciseLibraryModule()
        self.nutrition_module = NutritionModule()
        
        # Sincronizar datos entre módulos
        self._sync_modules()
    
    def _sync_modules(self):
        """Sincronizar configuración y datos entre módulos"""
        config = self.base_trainer.config
        progress_data = self.base_trainer.progress_data
        
        # Sincronizar configuración
        self.training_module.config = config
        self.training_module.progress_data = progress_data
        
        self.progress_module.config = config
        self.progress_module.progress_data = progress_data
        
        self.statistics_module.config = config
        self.statistics_module.progress_data = progress_data
        
        self.info_module.config = config
        self.info_module.progress_data = progress_data
        
        self.exercise_library_module.config = config
        self.exercise_library_module.progress_data = progress_data
        
        self.nutrition_module.config = config
        self.nutrition_module.progress_data = progress_data
        
        # Forzar actualización de entrenamientos completados
        self.training_module.update_completed_workouts()
    
    def reset_all_progress(self):
        """Reiniciar todo el progreso del usuario"""
        import datetime
        
        # Crear datos de progreso vacíos con mapeo calendario
        current_month = datetime.datetime.now().strftime('%Y-%m')
        fresh_progress_data = {
            'total_workouts': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'monthly_data': {
                current_month: {}
            },
            'completed_exercises': {},
            'exercise_weeks': {},
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Actualizar datos en memoria
        self.base_trainer.progress_data = fresh_progress_data
        self.progress_data = fresh_progress_data
        
        # Reinicializar mapeo calendario
        self.base_trainer.initialize_calendar_mapping()
        
        # Sincronizar con todos los módulos
        self._sync_modules()
        
        # Guardar al archivo
        self.base_trainer.save_progress_data()
        
        # Resetear semana actual
        st.session_state.current_week = 1
        
        # Limpiar todos los estados de ejercicios marcados en session_state
        exercise_keys_to_remove = []
        for key in st.session_state.keys():
            if isinstance(key, str) and (key.startswith('exercise_state_') or key.startswith('exercise_completed_')):
                exercise_keys_to_remove.append(key)
        
        for key in exercise_keys_to_remove:
            del st.session_state[key]
        
        # Limpiar también estados de avance de semana
        week_keys_to_remove = []
        for key in st.session_state.keys():
            if isinstance(key, str) and key.startswith('week_') and ('_advanced' in key or '_celebrated' in key):
                week_keys_to_remove.append(key)
        
        for key in week_keys_to_remove:
            del st.session_state[key]
        
        # Limpiar también estados relacionados con configuración calendario
        if 'show_date_config' in st.session_state:
            del st.session_state['show_date_config']
        
        # Resetear working_week también
        if 'working_week' in st.session_state:
            st.session_state.working_week = 1
        
        # Mostrar confirmación sin globos (versión profesional)
        st.success("✅ Progreso reiniciado completamente. Comenzando desde la Semana 1.")
    
    
    def render_header(self):
        """Renderizar cabecera principal"""
        total_exercises = self.base_trainer.get_total_exercises_count()
        st.markdown(f"""
        <div class="main-header">
            <h1>💪 Sudoraciones Propias</h1>
            <h3>Sistema de entrenamiento con mapeo calendario real + {total_exercises} ejercicios especializados</h3>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderizar barra lateral con opciones completas incluyendo mapeo calendario"""
        with st.sidebar:
            st.markdown("## ⚙️ Configuración")
            
            # Mostrar información de la semana actual sin selector redundante
            current_week = st.session_state.get('current_week', 1)
            week_info = self.base_trainer.get_week_info(current_week)
            
            st.info(f"""
            **Semana actual del programa:** {current_week}/20
            **Nivel:** {week_info['level_name']}
            **Descripción:** {week_info['level_description']}
            **Semana en ciclo:** {week_info['week_in_cycle']}/4
            """)
            
            st.markdown("---")
            
            self.base_trainer.render_equipment_settings()
            
            st.markdown("---")
            
            # Opciones de vista
            st.markdown("### 📊 Opciones de Vista")
            show_videos = st.checkbox("🎥 Mostrar videos", value=True)
            show_instructions = st.checkbox("📝 Mostrar instrucciones", value=True)
            show_tips = st.checkbox("💡 Mostrar consejos", value=True)
            
            st.markdown("---")
            
            # Información del programa
            total_exercises = self.base_trainer.get_total_exercises_count()
            st.markdown("### ℹ️ Información")
            st.info(f"""
            **Semana actual:** {current_week}/20
            **Total ejercicios:** {total_exercises} (distribuidos en 8 grupos musculares)
            **Días por semana:** 3-4
            **Días de descanso:** 3-4
            """)
            
            # Configuración de fecha de inicio del programa
            st.markdown("### 📅 Configuración Calendario")
            
            # Mostrar fecha de inicio actual en formato DD/MM/YYYY
            start_date_display = self.base_trainer.get_program_start_date_display()
            if start_date_display:
                st.caption(f"**Fecha inicio programa:** {start_date_display}")
            else:
                st.caption("**Fecha inicio programa:** No configurada")
            
            # Permitir cambiar la fecha de inicio
            if st.button("🔧 Cambiar Fecha de Inicio", help="Recalcula el mapeo entre semanas de entrenamiento y calendario"):
                st.session_state.show_date_config = True
            
            if st.session_state.get('show_date_config', False):
                import datetime
                
                # Obtener fecha actual o fecha guardada
                start_date_internal = self.base_trainer.progress_data.get('program_start_date', 'No configurada')
                if start_date_internal != 'No configurada':
                    try:
                        default_date = datetime.datetime.strptime(start_date_internal, '%Y-%m-%d').date()
                    except:
                        default_date = datetime.date.today()
                else:
                    # Por defecto, el lunes de esta semana
                    today = datetime.date.today()
                    default_date = today - datetime.timedelta(days=today.weekday())
                
                # Obtener fecha actual para mostrar como placeholder
                current_display = self.base_trainer.get_program_start_date_display()
                
                # Solo un campo de texto para fecha en formato DD/MM/YYYY
                date_text = st.text_input(
                    "Fecha de inicio del programa (DD/MM/YYYY):",
                    value=current_display if current_display else "",
                    placeholder="ej: 01/08/2025",
                    help="Esta será la fecha exacta de inicio del programa (no se ajustará al lunes)"
                )
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("✅ Guardar", key="save_start_date"):
                        if date_text.strip():
                            success = self.base_trainer.set_program_start_date(date_text.strip())
                            if success:
                                st.success("✅ Fecha actualizada correctamente")
                                st.session_state.show_date_config = False
                                st.rerun()
                        else:
                            st.error("Por favor, ingrese una fecha válida en formato DD/MM/YYYY")
                
                with col_cancel:
                    if st.button("❌ Cancelar", key="cancel_start_date"):
                        st.session_state.show_date_config = False
                        st.rerun()
                
                st.caption("⚠️ **Nota:** Cambiar la fecha recalculará el mapeo de todas las semanas")
            
            # Mostrar información de la semana calendario actual
            current_week_dates = self.base_trainer.get_week_dates_formatted(current_week)
            if current_week_dates and 'start_date' in current_week_dates:
                st.caption(f"**Semana {current_week}:** {current_week_dates['start_date']} a {current_week_dates['end_date']}")
            
            # Estadísticas rápidas
            if self.base_trainer.progress_data.get('total_workouts', 0) > 0:
                st.markdown("### 📈 Estadísticas")
                st.metric("Entrenamientos totales", self.base_trainer.progress_data['total_workouts'])
            
            # Información de arquitectura modular
            st.markdown("---")
            st.markdown("### 🏗️ Arquitectura")
            st.markdown("""
            **Sistema Modular:**
            - 🎯 Plan de Entrenamiento con fechas reales
            - 📊 Progreso y Calendario sincronizado
            - 📈 Estadísticas acumulativas
            - ℹ️ Información del Programa
            - 🔧 Core del Sistema + Mapeo Calendario
            """)
            
            # Sección de reinicio de progreso
            st.markdown("---")
            st.markdown("### 🔄 Gestión de Progreso")
            
            # Mostrar información del progreso actual
            total_workouts = self.base_trainer.progress_data.get('total_workouts', 0)
            if total_workouts > 0:
                st.info(f"📊 **Progreso actual:** {total_workouts} entrenamientos completados")
            
            # Botón de reinicio con confirmación
            if st.button("🗑️ Reiniciar Todo el Progreso", type="secondary", use_container_width=True):
                if 'confirm_reset' not in st.session_state:
                    st.session_state.confirm_reset = False
                st.session_state.confirm_reset = True
            
            # Confirmación de reinicio
            if st.session_state.get('confirm_reset', False):
                st.warning("⚠️ **¿Estás seguro?** Esta acción eliminará:")
                st.markdown("""
                - ✅ Todos los ejercicios completados
                - 📅 Todo el historial del calendario
                - 📊 Todas las estadísticas y rachas
                - 🏆 El progreso de las 20 semanas
                - 📅 El mapeo calendario (se reiniciará)
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Sí, Reiniciar", type="primary", use_container_width=True):
                        self.reset_all_progress()
                        st.session_state.confirm_reset = False
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", use_container_width=True):
                        st.session_state.confirm_reset = False
                        st.rerun()
            
            return show_videos, show_instructions, show_tips
    
    def render_tabs(self):
        """Renderizar pestañas principales"""
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🏋️ Plan de Entrenamiento", 
            "📊 Progreso", 
            "📈 Estadísticas",
            "📚 Biblioteca de Ejercicios",
            "🍎 Nutrición",
            "ℹ️ Información"
        ])
        
        return tab1, tab2, tab3, tab4, tab5, tab6
    
    def run(self):
        """Ejecutar la aplicación principal"""
        try:
            # Ancla superior para scroll
            st.markdown("<div id='top-anchor'></div>", unsafe_allow_html=True)
            # Renderizar cabecera
            self.render_header()
            
            # Sincronizar datos antes de renderizar
            self._sync_modules()
            
            # Renderizar barra lateral y obtener configuraciones
            show_videos, show_instructions, show_tips = self.render_sidebar()
            
            # Renderizar pestañas principales
            tab1, tab2, tab3, tab4, tab5, tab6 = self.render_tabs()
            
            with tab1:
                # Pestaña de Plan de Entrenamiento con fechas calendario
                
                # Selector de semana
                self.training_module.render_week_selector()
                
                # Plan de entrenamiento
                self.training_module.render_training_plan(show_videos, show_instructions, show_tips)
            
            with tab2:
                # Pestaña de Progreso y Calendario con mapeo real
                self.progress_module.render_progress_tab()
            
            with tab3:
                # Pestaña de Estadísticas acumulativas
                self.statistics_module.render_statistics_tab()
            
            with tab4:
                # Pestaña de Biblioteca de Ejercicios
                self.exercise_library_module.render_library_tab()
            
            with tab5:
                # Pestaña de Nutrición
                self.nutrition_module.render_nutrition_tab()
            
            with tab6:
                # Pestaña de Información
                self.info_module.render_info_tab()
            
            # Sincronizar datos después de renderizar (por si hubo cambios)
            self._sync_modules()
            
            # Pie de página
            st.markdown("---")
            st.markdown(
                "💪 **Sudoraciones Propias v1.4.0** - Sistema de Entrenamiento con Mapeo Calendario  \n"
                "🚀 Desarrollado con ☕ Python & Streamlit  \n"
                "📅 **Nuevo**: Semanas de entrenamiento sincronizadas con fechas reales  \n"
                "**Creado por entreunosyceros**",
                unsafe_allow_html=False
            )

            # Botón al final para volver arriba (sin JS, enlace ancla)
            st.markdown(
                """
<style>
#top-anchor{position:absolute;top:0;left:0;}
a.back-top-bottom{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff!important;padding:14px 26px;border-radius:40px;font-weight:600;text-decoration:none;margin-top:10px;box-shadow:0 4px 10px rgba(0,0,0,.25);transition:.25s;}
a.back-top-bottom:hover{transform:translateY(-3px);box-shadow:0 6px 16px rgba(0,0,0,.35);}
</style>
<div style='text-align:center;margin:40px 0 10px;'>
    <a href='#top-anchor' class='back-top-bottom' title='Volver arriba'>⬆️ Volver arriba</a>
</div>
                """,
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"❌ Error en la aplicación: {str(e)}")
            st.exception(e)


# Ejecutar la aplicación
if __name__ == "__main__":
    try:
        app = ModernHeavyDutyTrainer()
        app.run()
    except Exception as e:
        st.error(f"❌ Error crítico al inicializar la aplicación: {str(e)}")
        st.exception(e)
