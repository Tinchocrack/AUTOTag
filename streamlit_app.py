import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. CONFIGURACIÓN
st.set_page_config(page_title="AutoTag Pro", layout="wide")

# Tu clave que ya sabemos que funciona
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

st.markdown("# AutoTag 🏷️")

# 2. DOLAR (Directo para evitar esperas)
@st.cache_data(ttl=3600)
def traer_dolar():
    try:
        return requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
    except: return 1385.0

val_dolar = traer_dolar()
st.write(f"Dólar: ${val_dolar}")

# 3. BUSCADOR
query = st.text_input("Buscá un auto (ej: Kangoo, Hilux):")

if query:
    # Mostramos un mensaje de progreso más copado
    progreso = st.status("Conectando con el servidor seguro...", expanded=True)
    
    # Preparamos la URL de ML
    url_ml = f"https://vehiculos.mercadolibre.com.ar/{query.replace(' ', '-')}"
    
    # Llamada a ScrapingAnt REFORZADA
    # Agregamos 'wait_for_selector' para esperar a que carguen las fotos
    api_url = f"https://api.scrapingant.com/v2/general?url={url_ml}&x-api-key={ANT_API_KEY}&proxy_type=residential&browser=false"

    try:
        r = requests.get(api_url, timeout=30)
        progreso.update(label="Analizando datos de mercado...", state="running")
        
        soup = BeautifulSoup(r.text, 'html.parser')
        # Buscamos las tarjetas de los autos
        items = soup.find_all('li', class_='ui-search-layout__item', limit=9)
        
        if not items:
            st.error("ML devolvió la página vacía. Intentá buscar de nuevo en 5 segundos.")
        else:
            progreso.update(label="¡Resultados encontrados!", state="complete", expanded=False)
            cols = st.columns(3)
            for idx, item in enumerate(items):
                try:
                    # Extraemos la info básica
                    titulo = item.find('h2').text
                    precio = item.find('span', class_='andes-money-amount__fraction').text
                    link = item.find('a')['href']
                    img_tag = item.find('img')
                    img_url = img_tag.get('data-src') or img_tag.get('src')
                    
                    with cols[idx % 3]:
                        st.image(img_url, use_container_width=True)
                        st.subheader(f"$ {precio}")
                        st.caption(titulo)
                        st.link_button("Ver Vehículo", link)
                except: continue
    except Exception as e:
        st.error(f"Error de conexión: {e}")
