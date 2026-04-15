import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- 1. CONFIGURACIÓN Y ESTILO AVANZADO ---
st.set_page_config(page_title="AutoTag - Buscador Pro", layout="wide", page_icon="🏷️")

st.markdown("""
    <style>
    /* Estilo general y fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }

    /* Tarjetas de resultados con efecto Hover */
    .card-res {
        padding: 25px;
        border-radius: 15px;
        background-color: #ffffff;
        border-left: 10px solid #2E8B57;
        margin-bottom: 20px;
        transition: transform 0.3s, box-shadow 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-res:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        border-left-color: #FF8C00;
    }

    /* Botones personalizados */
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    .cotizacion-header {
        background: linear-gradient(90deg, #2E8B57 0%, #27ae60 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
        font-size: 1.2em;
    }

    .tag-brand { color: #FF8C00; font-weight: bold; }
    .auto-brand { color: #2E8B57; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE COTIZACIÓN ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return r.json()['venta']
    except: return 950.0

val_dolar = obtener_dolar()

# --- 3. INTERFAZ DE USUARIO ---
st.markdown(f'<div class="cotizacion-header">🏦 Dólar BNA Hoy: <b>${val_dolar}</b> | <span style="font-size:0.8em">Actualizado automáticamente</span></div>', unsafe_allow_html=True)

col_logo, col_desc = st.columns([1, 4])
with col_logo:
    st.markdown('# <span class="auto-brand">Auto</span><span class="tag-brand">Tag</span>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        busqueda = st.text_input("🔍 ¿Qué buscamos hoy?", placeholder="Ej: Hilux, Kangoo, Vento...")
    with c2:
        moneda = st.selectbox("Moneda", ["Dólares (USD)", "Pesos (ARS)"])
    with c3:
        st.write("") # Espaciador
        btn_buscar = st.button("🏷️ ESCANEAR")

# --- 4. LÓGICA DE BÚSQUEDA Y SCRAPING ---
def buscar_oportunidades(query):
    url = f"https://listado.mercadolibre.com.ar/{query.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    lista = []
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Buscamos los contenedores de productos
        items = soup.find_all('div', class_='poly-card__content', limit=6)
        for i in items:
            titulo = i.find('h2').text
            precio_texto = i.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
            moneda_orig = i.find('span', class_='andes-money-amount__currency-symbol').text
            link = i.find('a')['href']
            lista.append({"t": titulo, "p": float(precio_texto), "m": moneda_orig, "l": link})
        return lista
    except: return []

# --- 5. MOSTRAR RESULTADOS ---
if btn_buscar and busqueda:
    resultados = buscar_oportunidades(busqueda)
    if resultados:
        st.write(f"### 🏷️ Oportunidades encontradas para '{busqueda}':")
        for r in resultados:
            # Conversión dinámica
            p_final = r['p']
            if "Dólares" in moneda and r['m'] == "$":
                p_final = r['p'] / val_dolar
                txt_orig = f"Original: ${r['p']:,.0f} ARS"
            elif "Pesos" in moneda and r['m'] == "U$S":
                p_final = r['p'] * val_dolar
                txt_orig = f"Original: U$S {r['p']:,.0f}"
            else:
                txt_orig = "Precio directo"

            simbolo = "U$S" if "Dólares" in moneda else "$"
            
            # Mensaje de WhatsApp pre-armado
            msg_wa = urllib.parse.quote(f"Hola! Vi esta oportunidad en AutoTag y quería consultarte: {r['t']} - {r['l']}")
            
            # HTML de la Tarjeta Pro
            st.markdown(f"""
            <div class="card-res">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin:0; color:#333;">{r['t']}</h4>
                        <p style="color:gray; font-size:0.9em; margin:5px 0;">{txt_orig}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.5em; font-weight: bold; color: #FF8C00;">{simbolo} {p_final:,.0f}</span>
                    </div>
                </div>
                <div style="margin-top:15px;">
                    <a href="{r['l']}" target="_blank" style="color:#2E8B57; font-weight:bold; text-decoration:none; margin-right:20px;">VER EN ORIGEN ➔</a>
                    <a href="https://wa.me/?text={msg_wa}" target="_blank" class="btn-ws">📲 COMPARTIR / CONSULTAR</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No encontramos resultados. Probá con palabras más simples.")
