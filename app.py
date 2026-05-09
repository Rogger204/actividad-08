import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Wine Data", layout="wide", page_icon="🍷")

# --- CONEXIÓN A DB (Tus credenciales de Supabase) ---
def get_engine():
    try:
        user, pas, host = st.secrets["DB_USER"], st.secrets["DB_PASS"], st.secrets["DB_HOST"]
        port, db = st.secrets["DB_PORT"], st.secrets["DB_NAME"]
        return create_engine(f"postgresql://{user}:{pas}@{host}:{port}/{db}")
    except Exception as e:
        st.error("Error en credenciales de base de datos.")
        return None

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    id_drive = st.secrets["DRIVE_ID"]
    url = f'https://drive.google.com/uc?id={id_drive}'
    return pd.read_csv(url, sep=';')

try:
    df = load_data()
    
    st.title("🍷 Wine Analytics & Cloud Persistence")
    st.markdown("---")

    # sidebar para filtros globales
    st.sidebar.header("Filtros de Análisis")
    calidad_sel = st.sidebar.multiselect("Seleccionar Calidad", sorted(df['quality'].unique()), default=sorted(df['quality'].unique()))
    df_filtered = df[df['quality'].isin(calidad_sel)]

    # PESTAÑAS AVANZADAS
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Análisis Estadístico", "🧪 Correlaciones", "💾 Almacenamiento Cloud"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Muestras Filtradas", len(df_filtered))
        col2.metric("Promedio Alcohol", f"{df_filtered['alcohol'].mean():.2f}%")
        col3.metric("pH Promedio", f"{df_filtered['pH'].mean():.2f}")
        
        fig_hist = px.histogram(df_filtered, x="alcohol", color="quality", title="Distribución de Alcohol por Calidad", barmode="overlay")
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab2:
        st.subheader("Análisis Descriptivo")
        st.write(df_filtered.describe())
        
        st.subheader("Boxplot de Variables")
        var_box = st.selectbox("Selecciona variable para comparar", df.columns[:-1])
        fig_box = px.box(df_filtered, x="quality", y=var_box, color="quality", title=f"Variación de {var_box} según Calidad")
        st.plotly_chart(fig_box, use_container_width=True)

    with tab3:
        st.subheader("Matriz de Correlación")
        corr = df_filtered.corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', title="Mapa de Calor de Variables Químicas")
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab4:
        st.subheader("Persistencia en PostgreSQL (Supabase)")
        st.write("Registros listos para subir:", len(df_filtered))
        st.dataframe(df_filtered.head(10))

        if st.button("💾 Sincronizar con Base de Datos"):
            engine = get_engine()
            if engine:
                with st.spinner("Subiendo datos..."):
                    try:
                        # Agregamos fecha de carga para auditoría
                        df_to_save = df_filtered.copy()
                        df_to_save['upload_at'] = datetime.datetime.now()
                        
                        # Subida a la tabla
                        df_to_save.to_sql('registros_vinos', engine, if_exists='append', index=False)
                        st.success(f"¡Se han guardado {len(df_to_save)} filas exitosamente!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al insertar: {e}")

except Exception as e:
    st.error(f"Falla crítica: {e}")
