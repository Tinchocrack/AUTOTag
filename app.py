import streamlit as st
import requests
from bs4 import BeautifulSoup
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag - Tu Centro de Vehículos", layout="wide", page_icon="🏷️")

# --- 2. ESTILO ---
st.markdown("""
    <style>
    .card-auto {
        background: white; border-radius: 12px; padding: 0px; margin-bottom: 20px;
        border: 1px solid #e1e4e8; overflow: hidden; transition: 0.3s;
    }
    .card-auto:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .price-tag { font-size: 22px; font-weight: bold; color: #FF8C00; }
    .btn-detalle {
        background: #2E8B57; color: white !important; text-align: center;
        padding: 10px; display: block; text-decoration: none; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        return requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
    except: return 1410.0 # Valor de backup según tu captura

val_dolar = obtener_dolar()

# --- 4. MOTOR DE BÚSQUEDA REFORZADO ---
def buscar_reposteado(query):
    # ML a veces bloquea palabras simples, usamos la estructura de vehículos directa
    query_url = query.lower().replace(" ", "-")
    url = f"https://vehiculos.mercadolibre.com.ar/{query_url}"
    
    # Lista de identidades falsas para rotar
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com.ar/"
    }
    
    try:
        # Usamos una sesión para mantener cookies y parecer más humanos
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='ui-search-layout__item', limit=15)
        
        resultados = []
        for i in items:
            try:
                titulo = i.find('h2').text
                link = i.find('a', class_='ui-search-link')['href']
                precio = i.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                moneda = "USD" if "U$S" in i.text else "ARS"
                img = i.find('img').get('data-src') or i.find('img').get('src')
                
                # Extraer año y km si existen
                atributos = i.find_all('li', class_='ui-search-card-attributes__attribute')
                detalles = " | ".join([a.text for a in atributos]) if atributos else ""

                resultados.append({"t": titulo, "p": float(precio), "m": moneda, "l": link, "img": img, "d": detalles})
            except: continue
        return resultados
    except: return None

# --- 5. INTERFAZ ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.caption(f"Cotización Dólar: ${val_dolar}")

c1, c2 = st.columns([3,1])
with c1:
    busqueda = st.text_input("Buscador de Vehículos:", placeholder="Ej: Toyota Hilux 2016")
with c2:
    moneda_v = st.selectbox("Convertir a:", ["USD", "ARS"])

if busqueda:
    with st.spinner('Consolidando publicaciones...'):
        autos = buscar_reposteado(busqueda)
        
        if autos:
            cols = st.columns(3)
            for idx, a in enumerate(autos):
                p_final = a['p']
                if moneda_v == "USD" and a['m'] == "ARS": p_final = a['p'] / val_dolar
                elif moneda_v == "ARS" and a['m'] == "USD": p_final = a['p'] * val_dolar
                
                simb = "U$S" if moneda_v == "USD" else "$"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-auto">
                        <img src="{a['img']}" style="width:100%; height:180px; object-fit:cover;">
                        <div style="padding:15px;">
                            <h5 style="margin:0; height:40px; overflow:hidden;">{a['t']}</h5>
                            <p style="color:gray; font-size:12px; margin:5px 0;">{a['d']}</p>
                            <p class="price-tag">{simb} {p_final:,.0f}</p>
                            <a href="{a['l']}" target="_blank" class="btn-detalle">VER DETALLES</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Seguimos con bloqueos de seguridad de la fuente.")
            st.info("Para solucionar esto en serio, necesitamos usar un 'Proxy Argentino'. ¿Querés que te explique cómo configurar uno gratuito?")
