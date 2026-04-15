import streamlit as st
import requests
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏷️")

# --- ESTILO TUNEADO ---
st.markdown("""
    <style>
    .card-res { padding: 15px; border-radius: 12px; background-color: white; border: 1px solid #eee; 
                margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; }
    .card-res:hover { border-color: #FF8C00; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .img-auto { width: 150px; height: 100px; object-fit: cover; border-radius: 8px; margin-right: 20px; }
    .price-tag { color: #FF8C00; font-size: 20px; font-weight: bold; }
    .btn-ml { background-color: #2E8B57; color: white !important; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return r.json()['venta']
    except: return 1000.0

val_dolar = obtener_dolar()

# --- MOTOR API MERCADO LIBRE ---
def buscar_api_ml(query):
    # ML Site ID para Argentina es MLA
    query_clean = urllib.parse.quote(query)
    url = f"https://api.mercadolibre.com/sites/MLA/search?q={query_clean}&category=MLA1743" # Filtra solo Vehículos
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        results = data.get('results', [])
        
        lista = []
        for r in results[:15]: # Traemos los mejores 15
            lista.append({
                "t": r['title'],
                "p": float(r['price']),
                "m": r['currency_id'], # ARS o USD
                "l": r['permalink'],
                "img": r['thumbnail']
            })
        return lista
    except:
        return []

# --- INTERFAZ ---
st.markdown(f'# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.write(f"💵 **Dólar BNA: ${val_dolar}**")

c1, c2 = st.columns([3, 1])
with c1:
    busqueda = st.text_input("¿Qué buscamos?", placeholder="Ej: Hilux 2018")
with c2:
    moneda_v = st.selectbox("Mostrar en:", ["ARS (Pesos)", "USD (Dólares)"])

if busqueda:
    with st.spinner('Buscando ofertas...'):
        resultados = buscar_api_ml(busqueda)
        if resultados:
            for r in resultados:
                # Conversión
                p_final = r['p']
                if "USD" in moneda_v and r['m'] == "ARS":
                    p_final = r['p'] / val_dolar
                elif "ARS" in moneda_v and r['m'] == "USD":
                    p_final = r['p'] * val_dolar
                
                simb = "U$S" if "USD" in moneda_v else "$"
                
                # HTML con Imagen Real
                st.markdown(f"""
                <div class="card-res">
                    <img src="{r['img']}" class="img-auto">
                    <div style="flex-grow: 1;">
                        <h4 style="margin:0;">{r['t']}</h4>
                        <span class="price-tag">{simb} {p_final:,.0f}</span><br>
                        <span style="font-size:0.8em; color:gray;">Publicado en: {r['m']}</span>
                    </div>
                    <div>
                        <a href="{r['l']}" target="_blank" class="btn-ml">VER AHORA</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("No se encontraron resultados. Intentá con otras palabras.")
