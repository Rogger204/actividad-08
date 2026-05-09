import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Wine Data Hub - USIL", layout="wide", page_icon="🍷")

# --- CONEXIÓN A BASE DE DATOS ---
def get_engine():
    try:
        user = st.secrets["DB_USER"]
        pas = st.secrets["DB_PASS"]
        host = st.secrets["DB_HOST"]
        port = st.secrets["DB_PORT"]
        db = st.secrets["DB_NAME"]
        return create_engine(f"postgresql://{user}:{pas}@{host}:{port}/{db}")
    except Exception as e:
        st.error(f"Error en credenciales: {e}")
        return None

# --- CARGA DE DATOS (GOOGLE DRIVE) ---
@st.cache_data
def load_data():
    id_drive = st.secrets["DRIVE_ID"]
    url = f'https://drive.google.com/uc?id={id_drive}'
    return pd.read_csv(url, sep=';')

try:
    df = load_data()
    engine = get_engine()

    st.title("🍷 Wine Analytics & Cloud Management")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard e Informe", "💾 Filtrar y Guardar", "⚙️ Gestionar Base de Datos"])

    # --- PESTAÑA 1: DASHBOARD ---
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Resumen Estadístico")
            st.write(df.describe())
        with col2:
            fig = px.box(df, x="quality", y="alcohol", color="quality", title="Relación Alcohol vs Calidad")
            st.plotly_chart(fig, use_container_width=True)

    # --- PESTAÑA 2: FILTRAR Y GUARDAR ---
    with tab2:
        st.subheader("Configuración de Guardado")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            calidad_min = st.slider("Calidad mínima", 3, 9, 7)
        with col_f2:
            # Opción para elegir la cantidad de registros
            cantidad = st.number_input("Cantidad de registros a guardar", min_value=1, max_value=len(df), value=5)

        df_filtrado = df[df['quality'] >= calidad_min].head(cantidad)
        
        st.write(f"Muestra de registros a sincronizar ({len(df_filtrado)}):")
        st.dataframe(df_filtrado, use_container_width=True)

        if st.button("🚀 Confirmar y Guardar en Cloud"):
            if engine:
                with st.spinner("Sincronizando con Supabase..."):
                    try:
                        # Limpieza de nombres para SQL (espacios por guiones bajos)
                        df_db = df_filtrado.copy()
                        df_db.columns = [c.replace(' ', '_') for c in df_db.columns]
                        df_db['upload_at'] = datetime.datetime.now()
                        
                        # Guardar
                        df_db.to_sql('registros_vinos', engine, if_exists='append', index=False)
                        
                        st.success(f"✅ ¡Confirmado! Se guardaron {len(df_db)} registros exitosamente.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    # --- PESTAÑA 3: GESTIONAR DB (ELIMINAR) ---
    with tab3:
        st.subheader("Contenido actual en la Base de Datos")
        
        if engine:
            try:
                # Leer datos actuales de la DB
                query = "SELECT * FROM registros_vinos ORDER BY upload_at DESC"
                df_db_actual = pd.read_sql(query, engine)
                
                if not df_db_actual.empty:
                    st.write(f"Hay {len(df_db_actual)} registros en la nube.")
                    st.dataframe(df_db_actual, use_container_width=True)
                    
                    st.warning("⚠️ Zona de Peligro")
                    if st.button("🗑️ Eliminar TODOS los registros"):
                        with engine.connect() as conn:
                            conn.execute(text("TRUNCATE TABLE registros_vinos"))
                            conn.commit()
                        st.error("Todos los datos han sido eliminados de la base de datos.")
                        st.rerun()
                else:
                    st.info("La base de datos está vacía.")
            except Exception as e:
                st.info("La tabla aún no tiene datos o no ha sido creada.")

except Exception as e:
    st.error(f"Falla en la aplicación: {e}")
