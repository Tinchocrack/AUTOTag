import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="AutoTag - Centro de Vehículos", layout="wide", page_icon="🏷️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .card-auto {
        background: white;
        border-radius: 15px;
        padding: 0px;
        margin-bottom: 25px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    .info-area { padding: 15px; }
    .price-ars { color: #2E8B57; font-size: 22px; font-weight: bold; }
    .price-usd { color: #FF8C00; font-size: 22px; font-weight: bold; }
    .btn-detalle {
        background-color: #FF8C00;
        color: white !important;
        text-align: center;
        padding: 10px;
        display: block;
        border-radius: 0 0 15px 15px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. OBTENER DÓLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        # Usamos una fuente alternativa por si una falla
        r = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=5)
        return r.json()['venta']
    except: return 1050.0

val_dolar = obtener_dolar()

# --- 3. MOTOR DE BÚSQUEDA "REPOSTEADOR" ---
def scrapear_vehiculos(query):
    query_url = query.replace(" ", "-")
    url = f"https://vehiculos.mercadolibre.com.ar/{query_url}_NoIndex_True"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9"
    }
    
    lista = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos los bloques de cada auto
        articulos = soup.find_all('li', class_='ui-search-layout__item', limit=12)
        
        for art in articulos:
            try:
                titulo = art.find('h2').text
                link = art.find('a')['href']
                
                # Precio y Moneda
                precio_full = art.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                simbolo = art.find('span', class_='andes-money-amount__currency-symbol').text
                
                # Imagen (Buscamos la que no es lazy-load)
                img_tag = art.find('img')
                img_url = img_tag.get('data-src') or img_tag.get('src')

                lista.append({
                    "t": titulo,
                    "p": float(precio_full),
                    "s": "USD" if "U$S" in simbolo else "ARS",
                    "l": link,
                    "img": img_url
                })
            except: continue
        return lista
    except: return []

# --- 4. INTERFAZ ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.write(f"📊 **Dólar de Referencia: ${val_dolar}**")

with st.container():
    c1, c2 = st.columns([3,1])
    with c1:
        busqueda = st.text_input("Buscador de Vehículos:", placeholder="Ej: VW Amarok V6")
    with c2:
        preferencia = st.selectbox("Ver precios en:", ["Dólares (USD)", "Pesos (ARS)"])

if busqueda:
    with st.spinner(f'Analizando disponibilidad de {busqueda}...'):
        autos = scrapear_vehiculos(busqueda)
        
        if autos:
            cols = st.columns(3)
            for idx, a in enumerate(autos):
                # Conversión de moneda
                p_display = a['p']
                if preferencia == "Dólares (USD)" and a['s'] == "ARS":
                    p_display = a['p'] / val_dolar
                elif preferencia == "Pesos (ARS)" and a['s'] == "USD":
                    p_display = a['p'] * val_dolar
                
                simb = "U$S" if "Dólares" in preferencia else "$"
                clase_precio = "price-usd" if "Dólares" in preferencia else "price-ars"

                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-auto">
                        <img src="{a['img']}" style="width:100%; height:180px; object-fit:cover;">
                        <div class="info-area">
                            <h5 style="height:40px; overflow:hidden; margin:0; font-size:14px;">{a['t']}</h5>
                            <p class="{clase_precio}">{simb} {p_display:,.0f}</p>
                            <p style="font-size:11px; color:gray; margin:0;">Publicado en: {a['s']}</p>
                        </div>
                        <a href="{a['l']}" target="_blank" class="btn-detalle">VER FICHA COMPLETA</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("⚠️ No pudimos 'repostear' los resultados. Mercado Libre está protegiendo los datos.")
            st.info("Intentá buscar algo muy específico (Marca y Modelo).")
