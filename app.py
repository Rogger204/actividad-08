import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Vinos",
    page_icon="🍷",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("🍷 Análisis Químico de Vinos en la Nube")
st.info("""
    **Proyecto Cloud Computing**
    Esta aplicación integra tres servicios en la nube: GitHub (Código), Google Drive (Datos) 
    y Streamlit Cloud (Hosting). La conexión se realiza de forma segura mediante **Secrets Management**.
""")

# --- CONEXIÓN A LA NUBE (SECRETS) ---
# Intentamos obtener el ID del Secret, si no existe, usamos el tuyo por defecto
try:
    id_drive = st.secrets["DRIVE_ID"]
except:
    id_drive = "12xQDnmhf4q_76-QGomjBCvLKjcRknYsE"

url = f'https://drive.google.com/uc?id={id_drive}'

@st.cache_data
def load_wine_data():
    # El dataset de vinos de la UCI usa a veces ';' como separador
    try:
        return pd.read_csv(url, sep=';')
    except:
        return pd.read_csv(url)

try:
    df = load_wine_data()
    
    # --- MÉTRICAS EN TIEMPO REAL ---
    st.subheader("📊 Métricas del Dataset")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total de Muestras", len(df))
    with m2:
        st.metric("pH Promedio", f"{df['pH'].mean():.2f}")
    with m3:
        st.metric("% Alcohol Promedio", f"{df['alcohol'].mean():.1f}%")
    with m4:
        st.metric("Calidad Máxima", int(df['quality'].max()))

    # --- CUERPO PRINCIPAL ---
    tab1, tab2, tab3 = st.tabs(["📋 Vista de Datos", "📈 Análisis Visual", "⚙️ Configuración Cloud"])

    with tab1:
        st.write("### Exploración de Datos Crudos")
        st.dataframe(df, use_container_width=True)
        st.download_button("Descargar CSV", df.to_csv(index=False), "datos_vino.csv", "text/csv")

    with tab2:
        st.write("### Correlación Química")
        col_x = st.selectbox("Variable para Eje X", df.columns, index=10) # Alcohol por defecto
        col_y = st.selectbox("Variable para Eje Y", df.columns, index=8)  # pH por defecto
        
        fig = px.scatter(
            df, x=col_x, y=col_y, color="quality",
            title=f"Relación entre {col_x} y {col_y} según Calidad",
            template="plotly_white",
            color_continuous_scale=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.write("### Detalles del Stack Tecnológico")
        st.success("**1. Almacenamiento:** Google Drive (CSV File)")
        st.success("**2. Control de Versiones:** GitHub (Repository)")
        st.success("**3. Despliegue & Cómputo:** Streamlit Cloud (PaaS)")
        st.code(f"Dataset ID activo: {id_drive}", language="bash")

except Exception as e:
    st.error("Error de conexión: No se pudo recuperar el dataset de la nube.")
    st.write(f"Detalle técnico: {e}")
