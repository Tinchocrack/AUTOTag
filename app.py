import streamlit as st
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏷️")

# --- 2. ESTILO ---
st.markdown("""
    <style>
    .card-res { background: white; padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #ddd; }
    .price { color: #FF8C00; font-size: 24px; font-weight: bold; }
    .btn-link { background: #2E8B57; color: white !important; padding: 8px; border-radius: 5px; text-decoration: none; display: block; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DOLAR ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=5)
        return r.json()['venta']
    except: return 1000.0

val_dolar = obtener_dolar()

# --- 4. MOTOR DE BÚSQUEDA (MODO SURVIVOR) ---
def buscar_ml_v3(query):
    # Cambiamos la URL a una que ML suele dejar pasar más fácil
    query_clean = query.replace(" ", "%20")
    # Agregamos parámetros que simulan una búsqueda real de usuario
    url = f"https://api.mercadolibre.com/sites/MLA/search?q={query_clean}&sort=relevance&limit=12"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            return []
    except:
        return []

# --- 5. INTERFAZ ---
st.title("AutoTag 🏷️")
st.write(f"💵 Dólar Oficial: **${val_dolar}**")

busqueda = st.text_input("Ingresá marca y modelo:", placeholder="Ej: Toyota Hilux")
moneda_v = st.selectbox("Convertir a:", ["Pesos (ARS)", "Dólares (USD)"])

if busqueda:
    with st.spinner('Escaneando...'):
        res = buscar_ml_v3(busqueda)
        if res:
            cols = st.columns(3)
            for idx, i in enumerate(res):
                # Datos básicos
                titulo = i.get('title')
                precio_orig = float(i.get('price'))
                moneda_orig = i.get('currency_id')
                link = i.get('permalink')
                img = i.get('thumbnail').replace("-I.jpg", "-O.jpg") # Intenta mejorar calidad

                # Conversión
                p_final = precio_orig
                if "USD" in moneda_v and moneda_orig == "ARS":
                    p_final = precio_orig / val_dolar
                elif "ARS" in moneda_v and moneda_orig == "USD":
                    p_final = precio_orig * val_dolar
                
                simb = "U$S" if "USD" in moneda_v else "$"

                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card-res">
                        <img src="{img}" style="width:100%; height:150px; object-fit:cover; border-radius:8px;">
                        <h4 style="height:45px; overflow:hidden; font-size:14px;">{titulo}</h4>
                        <p class="price">{simb} {p_final:,.0f}</p>
                        <p style="font-size:10px; color:gray;">Original: {moneda_orig} {precio_orig:,.0f}</p>
                        <a href="{link}" target="_blank" class="btn-link">Ver Vehículo</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # SI FALLA TODO, MOSTRAMOS UN BOTÓN DIRECTO
            st.error("⚠️ Mercado Libre bloqueó la conexión automática.")
            st.info("No te preocupes, podés ver los resultados haciendo clic acá abajo:")
            url_manual = f"https://listado.mercadolibre.com.ar/{busqueda.replace(' ', '-')}"
            st.markdown(f'<a href="{url_manual}" target="_blank" style="background:#FF8C00; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">🔍 ABRIR BÚSQUEDA EN MERCADO LIBRE</a>', unsafe_allow_html=True)
