import streamlit as st
import requests
from bs4 import BeautifulSoup
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag - Buscador", layout="wide", page_icon="🏷️")

# --- 2. ESTILO TUNEADO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-auto {
        background: white; border-radius: 15px; padding: 0px; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; border: 1px solid #eee;
    }
    .price-tag { color: #FF8C00; font-size: 24px; font-weight: bold; }
    .btn-detalle {
        background: #2E8B57; color: white !important; text-align: center;
        padding: 12px; display: block; text-decoration: none; font-weight: bold;
    }
    .badge { background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try: return requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
    except: return 1450.0

val_dolar = obtener_dolar()

# --- 4. MOTOR DE BÚSQUEDA ---
def buscar_reposteado(query):
    # Formateamos la búsqueda como lo hace un navegador real
    query_formateada = query.lower().strip().replace(" ", "-")
    url = f"https://vehiculos.mercadolibre.com.ar/{query_formateada}_NoIndex_True"
    
    # Lista de User-Agents para engañar al sistema
    u_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(u_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.mercadolibre.com.ar",
        "Referer": "https://www.mercadolibre.com.ar/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscamos los items de la lista
        items = soup.find_all('li', class_='ui-search-layout__item', limit=15)
        
        resultados = []
        for i in items:
            try:
                # Título
                tit = i.find('h2').text
                # Link
                lnk = i.find('a', class_='ui-search-link')['href']
                # Precio
                pr_entero = i.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                # Moneda
                mon = "USD" if "U$S" in i.text else "ARS"
                # Imagen con manejo de Lazy Load
                img_tag = i.find('img')
                img_url = img_tag.get('data-src') or img_tag.get('src')
                # Atributos (Año, Km)
                attrs = i.find_all('li', class_='ui-search-card-attributes__attribute')
                attr_txt = " | ".join([a.text for a in attrs]) if attrs else ""

                resultados.append({"t": tit, "p": float(pr_entero), "m": mon, "l": lnk, "img": img_url, "d": attr_txt})
            except: continue
        return resultados
    except: return None

# --- 5. INTERFAZ ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.info(f"💵 Cotización Dólar BNA: **${val_dolar}**")

col1, col2 = st.columns([3,1])
with col1:
    busqueda = st.text_input("Buscá tu próximo vehículo:", placeholder="Ej: Vento TSI 2017")
with col2:
    moneda_v = st.selectbox("Mostrar precios en:", ["Dólares (USD)", "Pesos (ARS)"])

if busqueda:
    with st.spinner('Consolidando resultados en tiempo real...'):
        autos = buscar_reposteado(busqueda)
        
        if autos:
            st.success(f"Se encontraron {len(autos)} oportunidades para '{busqueda}'")
            # Mostrar en grilla de 3 columnas
            grid = st.columns(3)
            for idx, a in enumerate(autos):
                # Conversión
                p_final = a['p']
                if moneda_v == "Dólares (USD)" and a['m'] == "ARS": p_final = a['p'] / val_dolar
                elif moneda_v == "Pesos (ARS)" and a['m'] == "USD": p_final = a['p'] * val_dolar
                
                simb = "U$S" if moneda_v == "Dólares (USD)" else "$"
                
                with grid[idx % 3]:
                    st.markdown(f"""
                    <div class="card-auto">
                        <img src="{a['img']}" style="width:100%; height:180px; object-fit:cover;">
                        <div style="padding:15px;">
                            <span class="badge">{a['d']}</span>
                            <h5 style="margin:10px 0; height:45px; overflow:hidden; line-height:1.2;">{a['t']}</h5>
                            <p class="price-tag">{simb} {p_final:,.0f}</p>
                            <p style="font-size:11px; color:gray;">Publicado originalmente en {a['m']}</p>
                        </div>
                        <a href="{a['l']}" target="_blank" class="btn-detalle">VER FICHA COMPLETA</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("⚠️ No pudimos 'repostear' los resultados.")
            st.warning("Mercado Libre detectó la conexión. Intentá buscar algo más específico.")
