import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏎️")

# Tu clave de ScrapingAnt
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

st.markdown('# AutoTag 🏎️', unsafe_allow_html=True)

# --- DOLAR ---
@st.cache_data(ttl=3600)
def traer_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=5)
        return r.json()['venta']
    except: return 1380.0

val_dolar = traer_dolar()
st.write(f"💵 Cotización Dólar: **${val_dolar}**")

# --- BUSCADOR ---
query = st.text_input("Buscá tu próximo vehículo:", placeholder="Ej: Kangoo, Hilux...")

if query:
    status = st.status("Buscando en la base de datos...", expanded=True)
    
    # URL versión mobile (más fácil de leer)
    url_target = f"https://autos.mercadolibre.com.ar/{query.replace(' ', '-')}"
    
    # Parámetros simplificados para evitar el Error 422
    api_url = f"https://api.scrapingant.com/v2/general"
    params = {
        "url": url_target,
        "x-api-key": ANT_API_KEY,
        "proxy_type": "residential",
        "browser": "false"  # Desactivamos el navegador virtual para evitar el error 422
    }

    try:
        status.write("Conectando con el servidor...")
        r = requests.get(api_url, params=params, timeout=30)
        
        if r.status_code == 200:
            status.write("Extrayendo vehículos...")
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Selector para la versión estándar de resultados
            items = soup.select('li.ui-search-layout__item')
            
            if items:
                status.update(label="¡Vehículos encontrados!", state="complete", expanded=False)
                cols = st.columns(3)
                
                for idx, item in enumerate(items[:12]):
                    try:
                        titulo = item.find('h2').text
                        precio = item.find('span', class_='andes-money-amount__fraction').text
                        link = item.find('a')['href']
                        img_tag = item.find('img')
                        img_url = img_tag.get('data-src') or img_tag.get('src') or ""

                        with cols[idx % 3]:
                            if img_url:
                                st.image(img_url, use_container_width=True)
                            st.subheader(f"$ {precio}")
                            st.caption(titulo)
                            st.link_button("Ver Info", link)
                            st.write("---")
                    except: continue
            else:
                st.warning("No se pudieron leer los datos. ML actualizó su seguridad. Intentá buscar de nuevo.")
        else:
            st.error(f"Error de servidor: {r.status_code}. Probablemente excediste el límite gratuito de hoy.")
            
    except Exception as e:
        st.error(f"Error: {e}")
