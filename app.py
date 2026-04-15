import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="AutoTag - Buscador Inteligente", layout="wide", page_icon="🏷️")

st.markdown("""
    <style>
    .stButton>button { background-color: #FF8C00; color: white; border-radius: 8px; font-weight: bold; }
    .card-res { padding: 20px; border-radius: 12px; background-color: #f8f9fa; border-left: 8px solid #2E8B57; margin-bottom: 15px; }
    .precio-tag { color: #FF8C00; font-size: 22px; font-weight: bold; }
    .cotizacion-box { background-color: #2E8B57; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIÓN PARA TRAER EL DÓLAR (API Libre) ---
@st.cache_data(ttl=3600) # Guarda el valor por 1 hora para que la página sea rápida
def obtener_dolar():
    try:
        # Usamos la API de DolarApi que es muy confiable en Argentina
        response = requests.get("https://dolarapi.com/v1/dolares/oficial")
        data = response.json()
        return data['venta'] # Traemos el valor de venta del Banco Nación
    except:
        return 900.0 # Valor de respaldo por si falla la conexión

val_dolar = obtener_dolar()

# --- 3. ENCABEZADO Y COTIZACIÓN ---
st.markdown(f'<div class="cotizacion-box">🏦 Dólar Banco Nación (Venta): <b>${val_dolar}</b></div>', unsafe_allow_html=True)
st.title("AutoTag 🏷️")

# --- 4. PANEL DE CONTROL ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    busqueda = st.text_input("¿Qué buscás?", placeholder="Ej: Hilux 2018...")
with col2:
    moneda_mostrar = st.radio("Mostrar precios en:", ["ARS (Pesos)", "USD (Dólares)"])
with col3:
    presupuesto = st.number_input("Presupuesto Máx (en la moneda elegida)", value=15000)

# --- 5. LÓGICA DE BÚSQUEDA ---
def buscar_ml(termino):
    url = f"https://listado.mercadolibre.com.ar/{termino.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    lista = []
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('div', class_='poly-card__content', limit=5)
        for i in items:
            t = i.find('h2').text
            # El precio en ML a veces viene con símbolos que hay que limpiar
            p_raw = i.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
            # ML usa una clase para identificar si es U$S o $
            simbolo = i.find('span', class_='andes-money-amount__currency-symbol').text
            
            p_float = float(p_raw)
            lista.append({"t": t, "p": p_float, "s": simbolo, "l": i.find('a')['href']})
        return lista
    except: return []

# --- 6. RESULTADOS ---
if st.button("🏷️ ETIQUETAR OPORTUNIDADES"):
    res = buscar_ml(busqueda)
    if res:
        for r in res:
            # LÓGICA DE CONVERSIÓN
            precio_final = r['p']
            texto_conversion = ""

            if moneda_mostrar == "ARS (Pesos)":
                if r['s'] == "U$S": # Si el original es USD, pasamos a Pesos
                    precio_final = r['p'] * val_dolar
                    texto_conversion = f"(Original: U$S {r['p']})"
                simbolo_final = "$"
            else: # Si el usuario quiere ver Dólares
                if r['s'] == "$": # Si el original es Pesos, pasamos a Dólares
                    precio_final = r['p'] / val_dolar
                    texto_conversion = f"(Original: $ {r['p']})"
                simbolo_final = "U$S"

            st.markdown(f"""
            <div class="card-res">
                <div style="display: flex; justify-content: space-between;">
                    <b>{r['t']}</b>
                    <span class="precio-tag">{simbolo_final} {precio_final:,.2f}</span>
                </div>
                <p style="font-size: 0.8em; color: gray;">{texto_conversion}</p>
                <a href="{r['l']}" target="_blank">Ver publicación ➔</a>
            </div>
            """, unsafe_allow_html=True)
