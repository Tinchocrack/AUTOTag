import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AutoTag Pro", layout="wide", page_icon="🏎️")

# Tu clave de ScrapingAnt (0e0c3aa3df7044d6be3ab22c99fcddc7)
ANT_API_KEY = "0e0c3aa3df7044d6be3ab22c99fcddc7"

# --- 2. DISEÑO Y ESTILOS CSS PARA ESTETICIDAD ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextInput > div > div > input { border-radius: 10px; }
    .card-auto {
        background: white; border-radius: 15px; padding: 0px; margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #eee;
        transition: transform 0.3s ease;
    }
    .card-auto:hover { transform: translateY(-5px); }
    .container-info { padding: 15px; }
    .price-tag { color: #2E8B57; font-size: 26px; font-weight: bold; margin: 5px 0; }
    .title-auto { font-size: 16px; font-weight: 600; color: #333; height: 40px; overflow: hidden; margin-bottom: 10px; }
    .btn-ml {
        background: #FF8C00; color: white !important; text-align: center;
        padding: 10px; display: block; text-decoration: none; border-radius: 8px;
        font-weight: bold; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE DATOS (COTIZACIÓN DÓLAR) ---
@st.cache_data(ttl=3600)
def obtener_dolar():
    try:
        # Intentamos obtener el dólar oficial actualizado
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=5)
        return r.json()['venta']
    except: 
        return 1380.0 # Valor de respaldo según tus capturas

val_dolar = obtener_dolar()

# --- 4. ENCABEZADO Y TÍTULO ---
st.markdown('# <span style="color:#2E8B57">Auto</span><span style="color:#FF8C00">Tag</span> 🏷️', unsafe_allow_html=True)
st.write(f"📊 Cotización Dólar BNA: **${val_dolar}**")

# --- 5. BUSCADOR Y FILTROS ---
col_search, col_moneda = st.columns([3, 1])
with col_search:
    query = st.text_input("¿Qué vehículo buscás?", placeholder="Ej: Kangoo, Hilux, Vento...")
with col_moneda:
    moneda_v = st.selectbox("Mostrar precios en:", ["Dólares (USD)", "Pesos (ARS)"])

# --- 6. MOTOR DE BÚSQUEDA (EL CORAZÓN DE LA APP) ---
if query:
    status = st.status(f"Buscando '{query}' en tiempo real...", expanded=True)
    
    # URL optimizada para autos en Mercado Libre Argentina
    url_target = f"https://autos.mercadolibre.com.ar/{query.replace(' ', '-')}"
    
    # Parámetros para ScrapingAnt (Modo optimizado para evitar bloqueos)
    api_url = f"https://api.scrapingant.com/v2/general"
    params = {
        "url": url_target,
        "x-api-key": ANT_API_KEY,
        "proxy_type": "residential",
        "browser": "false" # Usamos false para evitar el error 422 y ganar velocidad de carga
    }

    try:
        status.write("Conectando con el servidor seguro...")
        r = requests.get(api_url, params=params, timeout=30)
        
        if r.status_code == 200:
            status.write("Analizando datos de mercado...")
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Selector de ítems compatible con la versión móvil/limpia
            items = soup.select('li.ui-search-layout__item')

            if items:
                status.update(label="¡Vehículos encontrados!", state="complete", expanded=False)
                
                # Grilla de resultados estética (3 columnas)
                for i in range(0, len(items[:12]), 3):
                    cols = st.columns(3)
                    for j, item in enumerate(items[i:i+3]):
                        try:
                            # Extracción de datos con limpieza de errores
                            titulo = item.find('h2').text
                            precio_str = item.find('span', class_='andes-money-amount__fraction').text.replace('.', '')
                            precio_raw = float(precio_str)
                            simbolo = item.find('span', class_='andes-money-amount__currency-symbol').text
                            link = item.find('a')['href']
                            
                            # Manejo de imágenes (ML usa src o data-src)
                            img_tag = item.find('img')
                            img_url = img_tag.get('data-src') or img_tag.get('src') or ""

                            # Lógica de conversión de moneda dinámica
                            moneda_orig = "USD" if "U$S" in simbolo else "ARS"
                            p_final = precio_raw
                            
                            if "Dólares" in moneda_v and moneda_orig == "ARS":
                                p_final = precio_raw / val_dolar
                                simb_display = "U$S"
                            elif "Pesos" in moneda_v and moneda_orig == "USD":
                                p_final = precio_raw * val_dolar
                                simb_display = "$"
                            else:
                                simb_display = "U$S" if moneda_orig == "USD" else "$"

                            # Dibujamos la tarjeta estética (HTML + CSS)
                            with cols[j]:
                                st.markdown(f"""
                                <div class="card-auto">
                                    <img src="{img_url}" style="width:100%; height:190px; object-fit:cover;">
                                    <div class="container-info">
                                        <div class="title-auto">{titulo}</div>
                                        <div class="price-tag">{simb_display} {p_final:,.0f}</div>
                                        <a href="{link}" target="_blank" class="btn-ml">VER VEHÍCULO</a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        except:
                            continue
            else:
                status.update(label="No se pudieron leer los datos", state="error")
                st.warning("Mercado Libre reforzó su seguridad momentáneamente. Intentá buscar de nuevo en unos segundos.")
        else:
            status.update(label=f"Error {r.status_code}", state="error")
            st.error("Se agotaron los créditos de la API o el servidor está saturado. Reintentá luego.")
            
    except Exception as e:
        st.error(f"Hubo un problema de conexión: {e}")
