import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Proyecto Cloud USIL", page_icon="☁️")

st.title("🚀 Mi Aplicación con 3 Servicios Cloud")

# --- PASO CRÍTICO: TU ID DE GOOGLE DRIVE ---
# Si tu enlace es https://drive.google.com/file/d/1ABC_123/view?usp=sharing
# El ID es lo que está entre /d/ y /view
id_drive = "TU_ID_AQUI" 
url = f'https://drive.google.com/uc?id={id_drive}'

@st.cache_data
def cargar_datos():
    return pd.read_csv(url)

try:
    df = cargar_datos()
    st.success("✅ Datos cargados exitosamente desde Google Drive")
    
    # Mostrar resumen de los datos
    st.subheader("Vista Previa del Dataset")
    st.dataframe(df.head(10))
    
    # Gráfico automático
    st.subheader("Análisis Visual")
    columnas = df.select_dtypes(include=['number']).columns.tolist()
    if len(columnas) >= 2:
        fig = px.scatter(df, x=columnas[0], y=columnas[1], title=f"Relación: {columnas[0]} vs {columnas[1]}")
        st.plotly_chart(fig)
    else:
        st.write("El dataset no tiene suficientes columnas numéricas para un gráfico de dispersión.")

except Exception as e:
    st.error(f"Error al conectar con la nube: {e}")
    st.info("Asegúrate de que el archivo en Drive sea público (Cualquier persona con el enlace).")