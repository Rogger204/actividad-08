import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Vinos Cloud - USIL",
    page_icon="🍷",
    layout="wide"
)

# --- ENCABEZADO ---
st.title("🍷 Dashboard de Análisis: Calidad del Vino")
st.markdown("---")

# --- CONEXIÓN SEGURA A LA NUBE ---
try:
    id_drive = st.secrets.get("DRIVE_ID", "12xQDnmhf4q_76-QGomjBCvLKjcRknYsE")
except:
    id_drive = "12xQDnmhf4q_76-QGomjBCvLKjcRknYsE"

url = f'https://drive.google.com/uc?id={id_drive}'

@st.cache_data
def load_wine_data():
    try:
        return pd.read_csv(url, sep=';')
    except:
        return pd.read_csv(url)

try:
    df = load_wine_data()
    
    # --- MÉTRICAS ---
    st.subheader("📊 Resumen de la Muestra")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Vinos", len(df))
    m2.metric("pH Promedio", f"{df['pH'].mean():.2f}")
    m3.metric("Alcohol Promedio", f"{df['alcohol'].mean():.1f}%")
    m4.metric("Calidad Máxima", int(df['quality'].max()))

    # --- PESTAÑAS ---
    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Datos", "📈 Gráficos Interactivos", "🔍 Filtros de Usuario"])

    with tab1:
        st.write("### Datos desde Google Drive")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.write("### Correlación Química")
        cols = df.select_dtypes(include=['number']).columns.tolist()
        c1, c2 = st.columns(2)
        with c1:
            col_x = st.selectbox("Variable X", cols, index=cols.index('alcohol') if 'alcohol' in cols else 0)
        with c2:
            col_y = st.selectbox("Variable Y", cols, index=cols.index('volatile acidity') if 'volatile acidity' in cols else 0)
        
        fig = px.scatter(df, x=col_x, y=col_y, color="quality", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("🔍 Explorador de Datos")
        st.write("Usa los filtros para segmentar la información del dataset.")
        
        # Filtro por rango de alcohol
        min_alc = float(df['alcohol'].min())
        max_alc = float(df['alcohol'].max())
        alc_range = st.slider("Rango de Alcohol (%)", min_alc, max_alc, (min_alc, max_alc))
        
        # Filtro por calidad
        calidades = sorted(df['quality'].unique())
        selected_qual = st.multiselect("Niveles de Calidad", calidades, default=calidades)
        
        # Aplicar filtros
        df_filtered = df[(df['alcohol'] >= alc_range[0]) & 
                         (df['alcohol'] <= alc_range[1]) & 
                         (df['quality'].isin(selected_qual))]
        
        st.write(f"Resultados encontrados: **{len(df_filtered)}**")
        st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error("Error al conectar con la nube.")
    st.write(e)
