import streamlit as st
import pandas as pd
from sqlalchemy import create_client, create_engine

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vinos DB Directa - USIL", layout="wide")

# --- CONEXIÓN DIRECTA A POSTGRES (SUPABASE) ---
def get_connection():
    user = st.secrets["DB_USER"]
    password = st.secrets["DB_PASS"]
    host = st.secrets["DB_HOST"]
    port = st.secrets["DB_PORT"]
    db = st.secrets["DB_NAME"]
    
    # Creamos el motor de conexión
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

# --- CARGA DE DATOS DESDE DRIVE ---
id_drive = st.secrets["DRIVE_ID"]
url_drive = f'https://drive.google.com/uc?id={id_drive}'

@st.cache_data
def load_data():
    return pd.read_csv(url_drive, sep=';')

try:
    df = load_data()
    st.title("🍷 Guardado Directo en PostgreSQL")

    tab1, tab2 = st.tabs(["📋 Datos Originales", "💾 Filtrar y Guardar"])

    with tab1:
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Filtrar Vinos de Calidad Superior")
        df_top = df[df['quality'] >= 7]
        st.write(f"Registros listos para guardar: {len(df_top)}")
        st.dataframe(df_top.head())

        if st.button("💾 Enviar a Base de Datos"):
            try:
                engine = get_connection()
                # 'if_exists=append' agrega los datos a la tabla existente
                # 'index=False' evita que se cree una columna extra para el índice
                df_top.head(10).to_sql('registros_vinos', engine, if_exists='append', index=False)
                st.success("¡Datos insertados correctamente usando los credenciales del Host!")
            except Exception as e:
                st.error(f"Error en la conexión: {e}")

except Exception as e:
    st.error(f"Error general: {e}")
