import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AutoTag - Oportunidades de Vehículos", layout="wide", page_icon="🏷️")

# --- 2. ESTILO VISUAL AUTOTAG (Naranja y Verde) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { 
        background-color: #FF8C00; color: white; border-radius: 8px; 
        font-weight: bold; height: 3.5em; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #e67e00; border: none; color: white; }
    .card-res {
        padding: 20px; border-radius: 12px; background-color: #f8f9fa;
        border-left: 8px solid #2E8B57; margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .tag-text { color: #FF8C00; font-weight: bold; font-size: 32px; font-family: 'Arial Black'; }
    .auto-text { color: #2E8B57; font-weight: bold; font-size: 32px; font-family: 'Arial Black'; }
    .precio-destacado { color: #FF8C00; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENCABEZADO ---
st.markdown('<p><span class="auto-text">Auto</span><span class="tag-text">Tag</span> 🏷️</p>', unsafe_allow_html=True)
st.write("### Tu etiqueta de confianza para encontrar oportunidades reales.")

# Inicializar sesión para favoritos
if 'favs' not in st.session_state:
    st.session_state.favs = []

# --- 4. PANEL DE BÚSQUEDA ---
col_busq, col_pres = st.columns([2, 1])
with col_busq:
    busqueda = st.text_input("¿Qué buscás hoy?", placeholder="Ej: Toyota Hilux 2017...")
with col_pres:
    presupuesto = st.number_input("Presupuesto Máx (USD)", value=15000)

with st.expander("⚙️ Filtros Personalizados"):
    f1, f2 = st.columns(2)
    tipo_v = f1.selectbox("Categoría", ["Auto", "Utilitario / Pyme", "Camión"])
    ubicacion = f2.text_input("Ubicación preferida", "Argentina")

# --- 5. LÓGICA DE BÚSQUEDA ---
def buscar_en_ml(termino):
    url = f"https://listado.mercadolibre.com.ar/{termino.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    lista = []
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('div', class_='poly-card__content', limit=5)
        for i in items:
            t = i.find('h2').text
            p = i.find('span', class_='andes-money-amount__fraction').text
            l = i.find('a')['href']
            lista.append({"t": t, "p": p, "l": l})
        return lista
    except: return []

# --- 6. ACCIÓN Y RESULTADOS ---
if st.button("🏷️ ETIQUETAR OPORTUNIDADES"):
    if busqueda:
        with st.spinner('AutoTag está escaneando el mercado por vos...'):
            resultados = buscar_en_ml(busqueda)
            if resultados:
                st.session_state.res_busqueda = resultados
            else:
                st.error("No encontramos resultados exactos. Intentá variar la búsqueda.")
    else:
        st.warning("Por favor, escribí qué vehículo buscás.")

if 'res_busqueda' in st.session_state:
    st.write("---")
    for r in st.session_state.res_busqueda:
        st.markdown(f"""
        <div class="card-res">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 18px; font-weight: bold; color: #333;">{r['t']}</span><br>
                    <a href="{r['l']}" target="_blank" style="color: #2E8B57; font-weight: bold; text-decoration: none;">Ver Oferta Original ➔</a>
                </div>
                <span class="precio-destacado">$ {r['p']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"❤️ Guardar en mi Garaje", key=r['l']):
            if r not in st.session_state.favs:
                st.session_state.favs.append(r)
                st.toast(f"Guardado: {r['t'][:20]}...")

# --- 7. BARRA LATERAL (GARAJE) ---
st.sidebar.markdown('<p><span class="auto-text" style="font-size:20px">Auto</span><span class="tag-text" style="font-size:20px">Tag</span></p>', unsafe_allow_html=True)
st.sidebar.header("⭐ Mis Favoritos")
if st.session_state.favs:
    for f in st.session_state.favs:
        st.sidebar.info(f"**{f['t']}**\n$ {f['p']}")
    if st.sidebar.button("Limpiar todo"):
        st.session_state.favs = []
        st.rerun()
else:
    st.sidebar.write("Tu garaje está vacío.")
