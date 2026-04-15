import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏷️")

st.markdown("""
    <style>
    .card-res { padding: 20px; border-radius: 15px; background-color: white; border-left: 10px solid #2E8B57; 
                margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s; }
    .card-res:hover { transform: scale(1.01); border-left-color: #FF8C00; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 8px 15px; border-radius: 8px; 
              text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return r.json()['venta']
    except: return 980.0

val_dolar = obtener_dolar()

# --- MOTOR DE BÚSQUEDA REFORZADO ---
def buscar_oportunidades(query):
    # Limpiamos el texto para la URL
    query_clean = urllib.parse.quote(query)
    url = f"https://listado.mercadolibre.com.ar/{query_clean}"
    
    # Engañamos a ML para que crea que somos Chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9"
    }
    
    lista = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ML usa diferentes clases. Probamos con las más comunes:
        items = soup.find_all(['div', 'li'], class_=['ui-search-result__wrapper', 'poly-card', 'ui-search-layout__item'])
        
        for i in items[:10]: # Traemos los primeros 10
            try:
                # Intentamos extraer Título
                titulo = i.find(['h2', 'h3']).text.strip()
                # Intentamos extraer Precio
                precio_raw = i.find('span', class_='andes-money-amount__fraction').text.replace('.', '').replace(',', '')
                # Intentamos extraer Moneda
                moneda_orig = "U$S" if "U$S" in i.text or "USD" in i.text else "$"
                # Intentamos extraer Link
                link = i.find('a')['href']
                
                lista.append({"t": titulo, "p": float(precio_raw), "m": moneda_orig, "l": link})
            except:
                continue
        return lista
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

# --- INTERFAZ ---
st.title("AutoTag 🏷️")
st.info(f"💡 Cotización Dólar BNA: ${val_dolar}")

c1, c2 = st.columns([3, 1])
with c1:
    busqueda = st.text_input("¿Qué auto o camioneta buscás?", placeholder="Ej: Hilux 2015")
with c2:
    moneda_v = st.selectbox("Ver precios en:", ["Pesos (ARS)", "Dólares (USD)"])

if st.button("🔍 BUSCAR AHORA"):
    if busqueda:
        with st.spinner('Escaneando Mercado Libre...'):
            resultados = buscar_oportunidades(busqueda)
            if resultados:
                for r in resultados:
                    # Lógica de conversión
                    p_final = r['p']
                    if "Dólares" in moneda_v and r['m'] == "$":
                        p_final = r['p'] / val_dolar
                    elif "Pesos" in moneda_v and r['m'] == "U$S":
                        p_final = r['p'] * val_dolar
                    
                    simb = "U$S" if "Dólares" in moneda_v else "$"
                    
                    st.markdown(f"""
                    <div class="card-res">
                        <h4>{r['t']}</h4>
                        <h3 style="color:#FF8C00;">{simb} {p_final:,.0f}</h3>
                        <p style="font-size:0.8em; color:gray;">Moneda original: {r['m']}</p>
                        <a href="{r['l']}" target="_blank">Ver en ML ➔</a> | 
                        <a href="https://wa.me/?text=Mira este auto: {r['l']}" class="btn-ws">Compartir</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No hubo suerte. Intentá ser más específico (Ej: 'Ford Ranger 2012')")
