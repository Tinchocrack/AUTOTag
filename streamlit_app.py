import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏎️")

# Tu clave de ScrapingAnt (la que me pasaste recién)
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

# --- ESTILO ---
st.markdown("""
    <style>
    .card-auto { background: white; border-radius: 12px; padding: 15px; border: 1px solid #ddd; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .price { color: #FF8C00; font-size: 24px; font-weight: bold; }
    .btn-link { background: #2E8B57; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try: return requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
    except: return 1450.0

val_dolar = obtener_dolar()

# --- MOTOR DE BÚSQUEDA ---
def buscar_con_ant(query):
    query_clean = urllib.parse.quote(query.lower().replace(" ", "-"))
    target_url = f"https://vehiculos.mercadolibre.com.ar/{query_clean}"
    
    # URL de ScrapingAnt para saltar el bloqueo
    api_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={ANT_API_KEY}&browser=false&proxy_type=residential"

    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articulos = soup.find_all('li', class_='ui-search-layout__item', limit=15)
        
        lista = []
        for art in articulos:
            try:
                titulo = art.find('h2').text
                link = art.find('a')['href']
                precio = art.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                simbolo = art.find('span', class_='andes-money-amount__currency-symbol').text
                img = art.find('img').get('data-src') or art.find('img').get('src')
                
                lista.append({
                    "t": titulo, "p": float(precio), 
                    "m": "USD" if "U$S" in simbolo else "ARS", 
                    "l": link, "img": img
                })
            except: continue
        return lista
    except: return None

# --- INTERFAZ ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.write(f"💵 Dólar Oficial: **${val_dolar}**")

col1, col2 = st.columns([3, 1])
with col1:
    busqueda = st.text_input("¿Qué auto buscamos?", placeholder="Ej: Hilux, Vento, Amarok...")
with col2:
    moneda_v = st.selectbox("Mostrar en:", ["USD (Dólares)", "ARS (Pesos)"])

if busqueda:
    with st.spinner('Consultando mercado...'):
        autos = buscar_con_ant(busqueda)
        if autos:
            cols = st.columns(3)
            for idx, a in enumerate(autos):
                p_f = a['p']
                if "USD" in moneda_v and a['m'] == "ARS": p_f = a['p'] / val_dolar
                elif "ARS" in moneda_v and a['m'] == "USD": p_f = a['p'] * val_dolar
                simb = "U$S" if "USD" in moneda_v else "$"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-auto">
                        <img src="{a['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:8px;">
                        <h5 style="margin:10px 0; height:45px; overflow:hidden;">{a['t']}</h5>
                        <p class="price">{simb} {p_f:,.0f}</p>
                        <a href="{a['l']}" target="_blank" class="btn-link">VER FICHA</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No se pudieron cargar los datos. Probá con un término más simple.")
