import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏎️")

# Tu clave de ScrapingAnt
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

st.markdown('# AutoTag <span style="font-size:30px;">🏎️</span>', unsafe_allow_html=True)

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
query = st.text_input("Buscá tu próximo vehículo:", placeholder="Ej: Hilux 2018, Amarok V6...")

if query:
    status = st.status("Iniciando conexión segura...", expanded=True)
    
    # URL de búsqueda
    url_target = f"https://listado.mercadolibre.com.ar/vehiculos/{query.replace(' ', '-')}_NoIndex_True"
    
    # Parámetros de ScrapingAnt (Modo Pro)
    # Agregamos 'wait_for_selector' para asegurar que cargue la lista de autos
    api_url = f"https://api.scrapingant.com/v2/general?url={url_target}&x-api-key={ANT_API_KEY}&proxy_type=residential&browser=true&wait_for_selector=.ui-search-layout__item"

    try:
        status.write("Burlando radares de Mercado Libre...")
        r = requests.get(api_url, timeout=60) # Le damos tiempo a que el navegador virtual abra
        
        if r.status_code == 200:
            status.write("¡Puerta abierta! Procesando autos...")
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Buscamos todos los artículos de la lista
            items = soup.find_all(['li', 'div'], class_='ui-search-layout__item')
            
            if not items:
                # Intento B: si cambió la clase, buscamos por etiquetas de resultado
                items = soup.select('.ui-search-result__wrapper')

            if items:
                status.update(label="¡Resultados obtenidos!", state="complete", expanded=False)
                cols = st.columns(3)
                
                for idx, item in enumerate(items[:12]):
                    try:
                        # Extraemos datos con cuidado
                        titulo = item.find('h2').text if item.find('h2') else "Vehículo sin título"
                        precio_raw = item.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                        link = item.find('a')['href']
                        img_tag = item.find('img')
                        img_url = img_tag.get('data-src') or img_tag.get('src') or ""

                        with cols[idx % 3]:
                            st.image(img_url, use_container_width=True)
                            st.markdown(f"### ${precio_raw}")
                            st.write(f"**{titulo}**")
                            st.link_button("Ver en ML", link)
                            st.write("---")
                    except: continue
            else:
                status.update(label="Falla en la lectura", state="error")
                st.warning("ML nos dejó entrar pero no mostró los autos. Probá refrescando o con una búsqueda más corta.")
        else:
            st.error(f"El servidor de proxies está saturado (Error {r.status_code}). Reintentá en un minuto.")
            
    except Exception as e:
        st.error(f"Se cortó la conexión: {e}")
