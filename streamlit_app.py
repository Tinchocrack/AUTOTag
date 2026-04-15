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
    except: return 1420.0

val_dolar = traer_dolar()
st.info(f"💵 Cotización Dólar: ${val_dolar}")

# --- BUSCADOR ---
query = st.text_input("Buscá tu próximo vehículo:", placeholder="Ej: Kangoo, Hilux...")

if query:
    status = st.status("Conectando con el búnker de datos...", expanded=True)
    
    # URL de búsqueda más directa (evitamos filtros raros)
    url_target = f"https://autos.mercadolibre.com.ar/{query.replace(' ', '-')}"
    
    # Parámetros para engañar al sistema de seguridad
    api_url = f"https://api.scrapingant.com/v2/general"
    params = {
        "url": url_target,
        "x-api-key": ANT_API_KEY,
        "proxy_type": "residential",
        "browser": "true",
        "js_snippet": "window.scrollTo(0, document.body.scrollHeight);" # Simulamos que bajamos la página
    }

    try:
        status.write("Saltando radares...")
        r = requests.get(api_url, params=params, timeout=60)
        
        if r.status_code == 200:
            status.write("¡Puerta abierta! Extrayendo info...")
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Selector ultra-resistente: buscamos las cajas de los productos por su estructura
            items = soup.select('ol.ui-search-layout li.ui-search-layout__item')
            
            if not items:
                # Si falló el anterior, probamos el selector de emergencia
                items = soup.find_all('div', class_='ui-search-result__wrapper')

            if items:
                status.update(label="¡Resultados obtenidos!", state="complete", expanded=False)
                cols = st.columns(3)
                
                for idx, item in enumerate(items[:12]):
                    try:
                        # Buscamos el link y el título
                        link_tag = item.find('a', class_='ui-search-link')
                        link = link_tag['href']
                        titulo = item.find('h2').text
                        
                        # Buscamos el precio
                        precio = item.find('span', class_='andes-money-amount__fraction').text
                        
                        # Buscamos la foto (limpiando links rotos)
                        img_tag = item.find('img')
                        img_url = img_tag.get('data-src') or img_tag.get('src') or ""

                        with cols[idx % 3]:
                            if img_url:
                                st.image(img_url, use_container_width=True)
                            st.markdown(f"### ${precio}")
                            st.write(f"**{titulo}**")
                            st.link_button("Ver Vehículo", link)
                            st.write("---")
                    except: continue
            else:
                st.error("ML bloqueó la visualización final. Intentá en 1 minuto.")
        else:
            st.error(f"Error de conexión (Status: {r.status_code})")
            
    except Exception as e:
        st.error(f"Se cortó la conexión: {e}")
