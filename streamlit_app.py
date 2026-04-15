import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏷️")

# Tu API Key (Sigue siendo la misma)
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

st.markdown("# AutoTag 🏎️")

# 2. DOLAR
@st.cache_data(ttl=3600)
def traer_dolar():
    try:
        return requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
    except: return 1410.0

dolar_val = traer_dolar()
st.write(f"💵 Dólar BNA: **${dolar_val}**")

# 3. BUSCADOR
query = st.text_input("Buscá un vehículo:", placeholder="Ej: Hilux 2016, Vento TSI...")

if query:
    status = st.status("Iniciando motor de búsqueda...", expanded=True)
    
    # Formateamos la URL de ML
    url_target = f"https://vehiculos.mercadolibre.com.ar/{query.replace(' ', '-')}"
    
    # 💡 CAMBIO CLAVE: Activamos 'browser=true' para que cargue el contenido dinámico
    api_url = f"https://api.scrapingant.com/v2/general?url={url_target}&x-api-key={ANT_API_KEY}&proxy_type=residential&browser=true"

    try:
        status.write("Saltando bloqueos de seguridad...")
        r = requests.get(api_url, timeout=45)
        
        if r.status_code == 200:
            status.write("Procesando datos recibidos...")
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Buscamos las tarjetas (ML cambia las clases seguido, usamos un selector más amplio)
            items = soup.select('li.ui-search-layout__item')
            
            if not items:
                st.warning("Mercado Libre no devolvió resultados legibles. Intentá con una marca más conocida.")
            else:
                status.update(label="¡Resultados listos!", state="complete", expanded=False)
                
                cols = st.columns(3)
                for idx, item in enumerate(items[:12]): # Limitamos a 12 para que cargue rápido
                    try:
                        titulo = item.find('h2').text
                        # Buscamos el precio con un selector flexible
                        precio = item.find('span', class_='andes-money-amount__fraction').text
                        link = item.find('a')['href']
                        
                        # Manejo de imágenes (ML usa src o data-src)
                        img_tag = item.find('img')
                        img_url = img_tag.get('data-src') or img_tag.get('src') or ""

                        with cols[idx % 3]:
                            st.image(img_url, use_container_width=True)
                            st.subheader(f"$ {precio}")
                            st.caption(titulo)
                            st.link_button("Ver Vehículo", link)
                            st.write("---")
                    except: continue
        else:
            st.error(f"Error de ScrapingAnt: {r.status_code}")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
