import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏎️")

# 🔑 TU API KEY DE SCRAPINGANT (Ya integrada)
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .card-auto {
        background: white; border-radius: 12px; padding: 0px; margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #ddd;
        transition: 0.3s;
    }
    .card-auto:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
    .container-info { padding: 15px; }
    .price { color: #FF8C00; font-size: 24px; font-weight: bold; margin: 5px 0; }
    .btn-link {
        background: #2E8B57; color: white !important; text-align: center;
        padding: 10px; display: block; text-decoration: none; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. OBTENER DÓLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=5)
        return r.json()['venta']
    except: return 1450.0

val_dolar = obtener_dolar()

# --- 4. MOTOR DE BÚSQUEDA (USA EL PROXY DE ARGENTINA) ---
def buscar_con_ant(query):
    query_clean = urllib.parse.quote(query.lower().replace(" ", "-"))
    target_url = f"https://vehiculos.mercadolibre.com.ar/{query_clean}"
    
    # Configuramos ScrapingAnt para que simule una visita desde Argentina/Brasil
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
                link = art.find('a', class_='ui-search-link')['href']
                # Limpieza de precio
                precio_raw = art.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                simbolo = art.find('span', class_='andes-money-amount__currency-symbol').text
                img = art.find('img').get('data-src') or art.find('img').get('src')
                
                lista.append({
                    "t": titulo, "p": float(precio_raw), 
                    "m": "USD" if "U$S" in simbolo else "ARS", 
                    "l": link, "img": img
                })
            except: continue
        return lista
    except: return None

# --- 5. INTERFAZ DE USUARIO ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.write(f"🏦 Cotización Dólar BNA: **${val_dolar}**")

col1, col2 = st.columns([3, 1])
with col1:
    busqueda = st.text_input("¿Qué auto o camioneta buscás?", placeholder="Ej: Amarok V6, Hilux, Vento...")
with col2:
    moneda_v = st.selectbox("Convertir precios a:", ["USD (Dólares)", "ARS (Pesos)"])

if busqueda:
    with st.spinner(f'Buscando "{busqueda}" sin bloqueos...'):
        autos = buscar_con_ant(busqueda)
        
        if autos:
            st.success(f"Encontramos {len(autos)} resultados")
            cols = st.columns(3)
            for idx, a in enumerate(autos):
                # Conversión de moneda
                p_final = a['p']
                if "USD" in moneda_v and a['m'] == "ARS": p_final = a['p'] / val_dolar
                elif "ARS" in moneda_v and a['m'] == "USD": p_final = a['p'] * val_dolar
                
                simb = "U$S" if "USD" in moneda_v else "$"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-auto">
                        <img src="{a['img']}" style="width:100%; height:180px; object-fit:cover;">
                        <div class="container-info">
                            <h5 style="height:45px; overflow:hidden; margin:0; line-height:1.2;">{a['t']}</h5>
                            <p class="price">{simb} {p_final:,.0f}</p>
                            <p style="font-size:11px; color:gray;">Original: {a['m']} {a['p']:,.0f}</p>
                            <a href="{a['l']}" target="_blank" class="btn-link">DETALLES EN ML</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No se pudieron traer resultados. ML sigue bloqueando o el término es muy raro.")
