import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide")

# Tu clave de ScrapingAnt
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

st.title("AutoTag 🏷️")

# --- DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=5)
        return r.json()['venta']
    except:
        return 1450.0

dolar = obtener_dolar()
st.write(f"Dólar: ${dolar}")

# --- BUSCADOR ---
query = st.text_input("Buscá un auto (ej: Vento):")

if query:
    with st.spinner('Buscando...'):
        # Preparamos la URL de Mercado Libre
        url_ml = f"https://vehiculos.mercadolibre.com.ar/{query.replace(' ', '-')}"
        
        # Le pedimos a ScrapingAnt que entre por nosotros
        api_ant = f"https://api.scrapingant.com/v2/general?url={url_ml}&x-api-key={ANT_API_KEY}&proxy_type=residential"
        
        try:
            res = requests.get(api_ant, timeout=20)
            soup = BeautifulSoup(res.text, 'html.parser')
            articulos = soup.find_all('li', class_='ui-search-layout__item', limit=6)
            
            if not articulos:
                st.warning("No se encontraron resultados en esta búsqueda.")
            
            cols = st.columns(3)
            for idx, art in enumerate(articulos):
                try:
                    titulo = art.find('h2').text
                    precio = art.find('span', class_='andes-money-amount__fraction').text
                    link = art.find('a')['href']
                    img = art.find('img').get('data-src') or art.find('img').get('src')
                    
                    with cols[idx % 3]:
                        st.image(img)
                        st.subheader(f"$ {precio}")
                        st.write(titulo)
                        st.markdown(f"[Ver en Mercado Libre]({link})")
                except:
                    continue
        except Exception as e:
            st.error(f"Error de conexión: {e}")
