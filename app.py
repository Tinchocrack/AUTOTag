import streamlit as st
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏷️")

# --- 2. ESTILO TUNEADO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextInput>div>div>input { border-radius: 10px; border: 2px solid #2E8B57; }
    .card-res { 
        background-color: white; 
        padding: 0px; 
        border-radius: 15px; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: 0.3s;
        border: 1px solid #eee;
    }
    .card-res:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); border-color: #FF8C00; }
    .img-container { width: 100%; height: 200px; overflow: hidden; }
    .img-auto { width: 100%; height: 100%; object-fit: cover; }
    .info-container { padding: 15px; }
    .price-tag { color: #FF8C00; font-size: 24px; font-weight: bold; margin: 10px 0; }
    .btn-link { 
        background-color: #2E8B57; color: white !important; 
        text-align: center; padding: 10px; border-radius: 8px; 
        display: block; text-decoration: none; font-weight: bold;
    }
    .tag-header { background: #FF8C00; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. OBTENER DÓLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return r.json()['venta']
    except: return 1000.0

val_dolar = obtener_dolar()

# --- 4. MOTOR DE BÚSQUEDA ---
def buscar_ml(query):
    # Buscamos de forma global en Argentina (MLA) sin restringir categoría para que NO falle
    query_clean = urllib.parse.quote(query)
    url = f"https://api.mercadolibre.com/sites/MLA/search?q={query_clean}&limit=20"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get('results', [])
        
        lista = []
        for i in items:
            # Intentamos obtener una imagen de mejor calidad
            img_id = i.get('thumbnail_id', '')
            img_url = f"https://http2.mlstatic.com/D_NQ_NP_{img_id}-O.webp" if img_id else i.get('thumbnail')
            
            lista.append({
                "t": i.get('title'),
                "p": float(i.get('price')),
                "m": i.get('currency_id'),
                "l": i.get('permalink'),
                "img": img_url,
                "condicion": "Nuevo" if i.get('condition') == "new" else "Usado"
            })
        return lista
    except: return []

# --- 5. INTERFAZ ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.markdown(f"**Cotización Hoy:** 🏦 BNA Venta: `${val_dolar}`")

col_search, col_mon = st.columns([3, 1])
with col_search:
    busqueda = st.text_input("", placeholder="¿Qué auto buscamos? Ej: VW Vento 2014")
with col_mon:
    moneda_v = st.selectbox("Ver precios en:", ["Pesos (ARS)", "Dólares (USD)"])

if busqueda:
    with st.spinner('Escaneando el mercado...'):
        resultados = buscar_ml(busqueda)
        
        if resultados:
            # Creamos una grilla de 3 columnas para que parezca un catálogo
            cols = st.columns(3)
            for idx, r in enumerate(resultados):
                # Lógica de conversión
                p_final = r['p']
                if "USD" in moneda_v and r['m'] == "ARS":
                    p_final = r['p'] / val_dolar
                elif "ARS" in moneda_v and r['m'] == "USD":
                    p_final = r['p'] * val_dolar
                
                simb = "U$S" if "USD" in moneda_v else "$"
                
                # Mostrar en la columna correspondiente
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-res">
                        <div class="img-container">
                            <img src="{r['img']}" class="img-auto">
                        </div>
                        <div class="info-container">
                            <span class="tag-header">{r['condicion']}</span>
                            <h4 style="height: 50px; overflow: hidden; margin-top:10px;">{r['t']}</h4>
                            <p class="price-tag">{simb} {p_final:,.0f}</p>
                            <p style="font-size: 11px; color: gray;">Original: {r['m']} {r['p']:,.0f}</p>
                            <a href="{r['l']}" target="_blank" class="btn-link">Ver Oferta</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No se encontraron resultados. Intentá con un término más simple (ej. 'Partner' o 'Hilux')")
