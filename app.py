import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Wine Data", layout="wide", page_icon="🍷")

# --- FUNCIÓN DE CONEXIÓN A LA BASE DE DATOS ---
def get_engine():
    try:
        # Extraemos las credenciales de los Secrets de Streamlit
        user = st.secrets["DB_USER"]
        pas = st.secrets["DB_PASS"]
        host = st.secrets["DB_HOST"]
        port = st.secrets["DB_PORT"]
        db = st.secrets["DB_NAME"]
        
        # Construimos la cadena de conexión para PostgreSQL (Puerto 6543)
        url_conexion = f"postgresql://{user}:{pas}@{host}:{port}/{db}"
        return create_engine(url_conexion)
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

# --- CARGA DE DATOS DESDE GOOGLE DRIVE ---
@st.cache_data
def load_data():
    try:
        id_drive = st.secrets["DRIVE_ID"]
        url = f'https://drive.google.com/uc?id={id_drive}'
        # Cargamos el CSV usando ';' como separador común en datasets de vinos
        return pd.read_csv(url, sep=';')
    except Exception as e:
        st.error(f"Error al cargar datos desde Drive: {e}")
        return None

# --- LÓGICA PRINCIPAL DE LA APLICACIÓN ---
df = load_data()
engine = get_engine()

if df is not None:
    st.title("🍷 Wine Analytics & Cloud Management")
    st.markdown("---")

    # Creamos las pestañas para organizar la interfaz
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Análisis", "💾 Filtrar y Guardar", "⚙️ Gestionar Cloud DB"])

    # PESTAÑA 1: VISUALIZACIÓN Y ESTADÍSTICA
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Resumen Estadístico")
            st.write(df.describe())
        with col2:
            st.subheader("Distribución de Calidad")
            fig = px.histogram(df, x="quality", color="quality", nbins=10)
            st.plotly_chart(fig, use_container_width=True)

    # PESTAÑA 2: FILTRADO Y GUARDADO (CON CORRECCIÓN DE COLUMNAS)
    with tab2:
        st.subheader("Configuración de Sincronización")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            calidad_min = st.slider("Filtrar por calidad mínima", 3, 9, 7)
        with col_f2:
            # Opción para que el usuario elija la cantidad de registros
            cantidad = st.number_input("Cantidad de registros a guardar", min_value=1, max_value=100, value=5)

        # Aplicamos el filtro
        df_filtrado = df[df['quality'] >= calidad_min].head(cantidad)
        
        st.write(f"Vista previa de los registros a enviar ({len(df_filtrado)}):")
        st.dataframe(df_filtrado, use_container_width=True)

        if st.button("🚀 Confirmar y Guardar en Supabase"):
            if engine:
                with st.spinner("Sincronizando datos con la nube..."):
                    try:
                        # --- CORRECCIÓN CRÍTICA DE NOMBRES ---
                        df_db = df_filtrado.copy()
                        # Pasamos nombres a minúsculas y cambiamos espacios por guiones bajos
                        # Esto soluciona el error de: column "pH" does not exist
                        df_db.columns = [c.lower().replace(' ', '_') for c in df_db.columns]
                        
                        # Agregamos la columna de auditoría definida en el SQL
                        df_db['upload_at'] = datetime.datetime.now()
                        
                        # Insertamos en la tabla 'registros_vinos'
                        df_db.to_sql('registros_vinos', engine, if_exists='append', index=False)
                        
                        st.success(f"✅ ¡Guardado exitoso! {len(df_db)} registros sincronizados.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error técnico al guardar: {e}")

    # PESTAÑA 3: ADMINISTRACIÓN DE LA BASE DE DATOS
    with tab3:
        st.subheader("Contenido actual en la Nube")
        if engine:
            try:
                # Consultamos los datos actuales para confirmar el guardado
                query = text("SELECT * FROM registros_vinos ORDER BY upload_at DESC LIMIT 50")
                with engine.connect() as conn:
                    db_actual = pd.read_sql(query, conn)
                
                if not db_actual.empty:
                    st.write(f"Se encontraron {len(db_actual)} registros en la base de datos:")
                    st.dataframe(db_actual, use_container_width=True)
                    
                    st.divider()
                    st.warning("⚠️ Zona de Administración")
                    if st.button("🗑️ Eliminar TODOS los registros de la DB"):
                        with engine.begin() as conn:
                            conn.execute(text("TRUNCATE TABLE registros_vinos"))
                        st.error("Se han eliminado todos los datos de la tabla cloud.")
                        st.rerun()
                else:
                    st.info("La base de datos está vacía.")
            except Exception as e:
                st.info("La tabla aún no tiene datos o necesita ser creada con el código SQL.")

else:
    st.warning("No se pudo iniciar la aplicación. Verifica la conexión con Google Drive.")
