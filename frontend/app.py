import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import json
import os
import unicodedata
import base64
import pandas as pd

# ==========================================
# 0. CONFIGURACIÓN INICIAL Y ROUTER
# ==========================================
st.set_page_config(page_title="TechyPriceAI", page_icon="🏠", layout="wide")

# Inicializamos el Router en nuestra memoria
if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "landing"

# Variables de memoria de tu mapa (las de siempre)
if "lat" not in st.session_state:
    st.session_state.lat = 40.4168
if "lon" not in st.session_state:
    st.session_state.lon = -3.7038
if "last_barrio" not in st.session_state:
    st.session_state.last_barrio = None
if "direccion_texto" not in st.session_state:
    st.session_state.direccion_texto = "Puerta del Sol, Madrid"
if "distrito_manual" not in st.session_state:
    st.session_state.distrito_manual = "Centro"
if "barrio_manual" not in st.session_state:
    st.session_state.barrio_manual = "Sol"
if "predicted_price" not in st.session_state:
    st.session_state.predicted_price = None

# Carga de recursos globales (API, Mapa, GeoJSON)
import os
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")
geolocator = Nominatim(user_agent="airbnb_pricer_madrid_app")

current_dir = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.join(current_dir, "..", "data", "neighbourhoods.geojson")
geojson_data = None
try:
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
except FileNotFoundError:
    pass

madrid_geography = {
    "Centro": ["Sol", "Palacio", "Embajadores", "Cortes", "Justicia", "Universidad"],
    "Salamanca": ["Recoletos", "Goya", "Fuente del Berro", "Guindalera", "Lista", "Castellana"],
    "Ciudad Lineal": ["Ventas", "Pueblo Nuevo", "Quintana", "Concepción", "San Pascual", "San Juan Bautista", "Colina", "Atalaya", "Costillares"],
    "Retiro": ["Pacífico", "Adelfas", "Estrella", "Ibiza", "Jerónimos", "Niño Jesús"],
    "Chamberí": ["Gaztambide", "Arapiles", "Trafalgar", "Almagro", "Ríos Rosas", "Vallehermoso"],
    "Chamartín": ["El Viso", "Prosperidad", "Ciudad Jardín", "Hispanoamérica", "Nueva España", "Castilla"],
    "Tetuán": ["Bellas Vistas", "Cuatro Caminos", "Castillejos", "Almenara", "Valdeacederas", "Berruguete"],
    "Moncloa - Aravaca": ["Casa de Campo", "Argüelles", "Ciudad Universitaria", "Valdezarza", "Valdemarín", "El Plantío", "Aravaca"],
    "Latina": ["Los Cármenes", "Puerta del Ángel", "Lucero", "Aluche", "Campamento", "Cuatro Vientos", "Águilas"],
    "Carabanchel": ["Comillas", "Opañel", "San Isidro", "Vista Alegre", "Puerta Bonita", "Buenavista", "Abrantes"],
    "Usera": ["Orcasitas", "Orcasur", "San Fermín", "Almendrales", "Moscardó", "Zofío", "Pradolongo"],
    "Moratalaz": ["Pavones", "Horcajo", "Marroquina", "Media Legua", "Fontarrón", "Vinateros"],
    "Puente de Vallecas": ["Entrevías", "San Diego", "Palomeras Bajas", "Palomeras Sureste", "Portazgo", "Numancia"],
    "Villa de Vallecas": ["Casco Histórico de Vallecas", "Santa Eugenia", "Ensanche de Vallecas"],
    "Vicálvaro": ["Casco Histórico de Vicálvaro", "Valdebernardo", "Valderrivas", "El Cañaveral"],
    "San Blas - Canillejas": ["Simancas", "Hellín", "Amposta", "Arcos", "Rosas", "Rejas", "Canillejas", "Salvador"],
    "Barajas": ["Alameda de Osuna", "Aeropuerto", "Casco Histórico de Barajas", "Timón", "Corralejos"],
    "Hortaleza": ["Palomas", "Piovera", "Canillas", "Pinar del Rey", "Apóstol Santiago", "Valdefuentes"],
    "Fuencarral - El Pardo": ["El Pardo", "Fuentelarreina", "Peñagrande", "Pilar", "La Paz", "Valverde", "Mirasierra", "El Goloso"],
    "Villaverde": ["San Andrés", "San Cristóbal", "Butarque", "Los Rosales", "Los Ángeles"]
}

def limpiar_texto(texto):
    if not texto: return ""
    return unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
    
def get_base64_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# ==========================================
# 1. PANTALLA DE INICIO (LANDING PAGE - ENGLISH)
# ==========================================
def pantalla_landing():
    # 1. Cargamos las imágenes
    ruta_banner = os.path.join(current_dir, "assets", "madrid_tejados.jpg")
    ruta_logo = os.path.join(current_dir, "assets", "logo.jpg")
    
    bg_base64 = get_base64_image(ruta_banner)
    logo_base64 = get_base64_image(ruta_logo)

    # 2. Inyectamos el Súper CSS (Fondo oscuro y tarjetas)
    st.markdown(f"""
        <style>
        /* La foto en blanco y negro como fondo de toda la pantalla */
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("data:image/jpeg;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Ocultar barra superior de Streamlit para más limpieza */
        header {{ visibility: hidden; }}
        
        /* Estilos de texto globales para la Landing */
        .hero-title {{ color: white; text-align: center; font-size: 4rem; font-weight: 800; margin-top: 10px; text-shadow: 2px 2px 8px rgba(0,0,0,0.6); }}
        .hero-subtitle {{ color: #E2E8F0; text-align: center; font-size: 1.3rem; margin-bottom: 50px; text-shadow: 1px 1px 4px rgba(0,0,0,0.6); letter-spacing: 1px;}}
        
        /* Las tarjetas flotantes */
        .tarjeta {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 40px 30px;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
            text-align: center;
            height: 100%;
            transition: transform 0.3s ease;
        }}
        .tarjeta:hover {{ transform: translateY(-8px); }}
        .tarjeta h2 {{ color: #1E293B !important; margin-bottom: 15px; font-weight: 700; }}
        .tarjeta p {{ color: #475569 !important; font-size: 16px; line-height: 1.6; }}
        </style>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 3. Logo (centrado y con bordes redondeados)
    if logo_base64:
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 5px;">
                <img src="data:image/jpeg;base64,{logo_base64}" style="border-radius: 20px; width: 130px; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
            </div>
        """, unsafe_allow_html=True)

    # 4. Títulos en Inglés
    st.markdown("<div class='hero-title'>TechyPriceAI</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Artificial Intelligence applied to Real Estate in Madrid</div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 5. Las dos opciones
    col_izq, col_espacio, col_der = st.columns([8, 1, 8])

    with col_izq:
        st.markdown("""
            <div class='tarjeta'>
                <h2>🏠 I am a Host</h2>
                <p>Discover the optimal nightly price for your property based on its features, location, and market trends using our Machine Learning model.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        # st.button nativo de Streamlit justo debajo de la tarjeta
        if st.button("Enter as Host", type="primary", use_container_width=True):
            st.session_state.pantalla_actual = "host"
            st.rerun()

    with col_der:
        st.markdown("""
            <div class='tarjeta'>
                <h2>🔍 I am an Investor</h2>
                <p>Explore the market for undervalued properties. Find listings where the current price is significantly below our AI's estimated market value.</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        if st.button("Enter as Investor", type="secondary", use_container_width=True):
            st.session_state.pantalla_actual = "inversor"
            st.rerun()

# ==========================================
# 2. PANTALLA DEL HOST (TU CÓDIGO INTACTO)
# ==========================================
def pantalla_host():
    if st.button("⬅️ Back to Home"):
        st.session_state.pantalla_actual = "landing"
        st.rerun()
        
    st.title("🏠 AI-Powered Airbnb Pricer (Madrid)")
    st.markdown("Discover the optimal nightly price for your Airbnb using our Machine Learning model.")
    
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.header("📍 Property Details")
        
        lista_distritos = list(madrid_geography.keys())
        idx_d = lista_distritos.index(st.session_state.distrito_manual) if st.session_state.distrito_manual in lista_distritos else 0
        distrito_seleccionado = st.selectbox("1. Select District", lista_distritos, index=idx_d)
        
        lista_barrios = madrid_geography[distrito_seleccionado]
        idx_b = lista_barrios.index(st.session_state.barrio_manual) if st.session_state.barrio_manual in lista_barrios else 0
        barrio_seleccionado = st.selectbox("2. Select Neighborhood", lista_barrios, index=idx_b)
        
        st.session_state.distrito_manual = distrito_seleccionado
        st.session_state.barrio_manual = barrio_seleccionado
        
        if barrio_seleccionado != st.session_state.last_barrio:
            st.session_state.last_barrio = barrio_seleccionado
            try:
                loc = geolocator.geocode(f"{barrio_seleccionado}, {distrito_seleccionado}, Madrid, Spain")
                if loc:
                    st.session_state.lat = loc.latitude
                    st.session_state.lon = loc.longitude
                    st.session_state.direccion_texto = f"{barrio_seleccionado}, {distrito_seleccionado}"
                    st.rerun() 
            except:
                pass 
                
        st.subheader("Exact Location")
        direccion_input = st.text_input("Type your street and number:", value=st.session_state.direccion_texto)
        
        if st.button("🔍 Search Address"):
            try:
                loc = geolocator.geocode(f"{direccion_input}, Madrid, Spain", addressdetails=True)
                if loc:
                    st.session_state.lat = loc.latitude
                    st.session_state.lon = loc.longitude
                    
                    addr = loc.raw.get('address', {})
                    calle = addr.get('road', addr.get('pedestrian', addr.get('square', '')))
                    numero = addr.get('house_number', '').replace(',', '')
                    
                    if calle:
                        st.session_state.direccion_texto = f"{calle} {numero}".strip()
                    else:
                        st.session_state.direccion_texto = direccion_input
                    
                    zonas_osm = [
                        addr.get('city_district', ''), addr.get('district', ''),
                        addr.get('borough', ''), addr.get('suburb', ''),
                        addr.get('quarter', ''), addr.get('neighbourhood', ''),
                        addr.get('village', ''), addr.get('town', '')
                    ]
                    zonas_limpias = [limpiar_texto(z) for z in zonas_osm if z]
                    
                    distrito_match = None
                    for d in madrid_geography.keys():
                        if any(limpiar_texto(d) in z or z in limpiar_texto(d) for z in zonas_limpias):
                            distrito_match = d
                            break
                            
                    if distrito_match:
                        st.session_state.distrito_manual = distrito_match
                        
                        barrio_match = None
                        for b in madrid_geography[distrito_match]:
                            if any(limpiar_texto(b) in z or z in limpiar_texto(b) for z in zonas_limpias):
                                barrio_match = b
                                break
                                
                        if barrio_match:
                            st.session_state.barrio_manual = barrio_match
                            st.session_state.last_barrio = barrio_match
                        else:
                            st.session_state.barrio_manual = madrid_geography[distrito_match][0]
                            st.session_state.last_barrio = st.session_state.barrio_manual

                    st.success("✅ Ubicación encontrada y sincronizada!")
                    st.rerun()
                else:
                    st.error("❌ No encontrada. Prueba a poner la calle y el número exacto.")
            except Exception as e:
                st.error(f"Error en el buscador: {e}")
          
        st.subheader("Physical Characteristics")
        room_type = st.selectbox("Room Type", ["Entire home/apt", "Private room", "Shared room", "Hotel room"])
        c1, c2 = st.columns(2)
        with c1:
            accommodates = st.number_input("Accommodates", min_value=1, value=4)
            bedrooms = st.number_input("Bedrooms", min_value=0, value=2)
        with c2:
            beds = st.number_input("Beds", min_value=1, value=2)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=1.0, step=0.5)

        st.subheader("✨ Amenities")
        c3, c4, c5, c6 = st.columns(4)
        has_ac = c3.checkbox("AC")
        has_pool = c4.checkbox("Pool")
        has_elevator = c5.checkbox("Elevator")
        has_parking = c6.checkbox("Parking")

        st.subheader("🚀 Host Simulator")
        host_is_superhost = st.toggle("I am a Superhost 🌟")
        review_scores_rating = st.slider("Average Review Score", 0.0, 5.0, 4.75, 0.05)
        number_of_reviews = st.number_input("Number of Reviews", 0, value=10)


    with right_col:
        st.header("🗺️ Location Map")
        
        m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=14, tiles="CartoDB positron")
        
        if geojson_data:
            distrito_actual = limpiar_texto(st.session_state.distrito_manual)
            barrio_actual = limpiar_texto(st.session_state.barrio_manual)
            barrios_del_distrito = [limpiar_texto(b) for b in madrid_geography.get(st.session_state.distrito_manual, [])]
            
            def style_function(feature):
                props = feature.get('properties', {})
                barrio_geojson = limpiar_texto(props.get('neighbourhood', ''))
                distrito_geojson = limpiar_texto(props.get('neighbourhood_group', ''))
                
                if barrio_geojson == barrio_actual:
                    return {"fillColor": "#FF5A5F", "color": "#FF5A5F", "weight": 3, "fillOpacity": 0.5}
                elif distrito_geojson == distrito_actual or barrio_geojson in barrios_del_distrito:
                    return {"fillColor": "#FF5A5F", "color": "#FF5A5F", "weight": 1.5, "fillOpacity": 0.15}
                else:
                    return {"fillColor": "#888888", "color": "#666666", "weight": 0.5, "fillOpacity": 0.3}

            tiene_distrito = 'neighbourhood_group' in str(geojson_data)
            hover_tooltip = folium.GeoJsonTooltip(
                fields=['neighbourhood_group', 'neighbourhood'] if tiene_distrito else ['neighbourhood'],
                aliases=['📍 District:', '🏘️ Neighborhood:'] if tiene_distrito else ['🏘️ Neighborhood:'],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 13px; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);")
            )

            folium.GeoJson(
                geojson_data,
                name="Mapa de Madrid",
                style_function=style_function,
                tooltip=hover_tooltip
            ).add_to(m)

        folium.Marker(
            [st.session_state.lat, st.session_state.lon], 
            popup=st.session_state.direccion_texto, 
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)
        
        map_data = st_folium(m, width=500, height=400)
        
        if map_data and map_data.get("last_clicked"):
            clic_lat = map_data["last_clicked"]["lat"]
            clic_lon = map_data["last_clicked"]["lng"]
            
            if clic_lat != st.session_state.lat or clic_lon != st.session_state.lon:
                st.session_state.lat = clic_lat
                st.session_state.lon = clic_lon
                should_rerun = False
                
                try:
                    direccion = geolocator.reverse((clic_lat, clic_lon), timeout=10)
                    if direccion:
                        addr = direccion.raw.get('address', {})
                        
                        calle = addr.get('road', addr.get('pedestrian', addr.get('square', '')))
                        numero = addr.get('house_number', '').replace(',', '')
                        if calle:
                            st.session_state.direccion_texto = f"{calle} {numero}".strip()
                        else:
                            st.session_state.direccion_texto = "Ubicación en el mapa"
                        
                        zonas_osm = [
                            addr.get('city_district', ''), addr.get('district', ''),
                            addr.get('borough', ''), addr.get('suburb', ''),
                            addr.get('quarter', ''), addr.get('neighbourhood', ''),
                            addr.get('village', ''), addr.get('town', '')
                        ]
                        zonas_limpias = [limpiar_texto(z) for z in zonas_osm if z]
                        
                        distrito_match = None
                        for d in madrid_geography.keys():
                            if any(limpiar_texto(d) in z or z in limpiar_texto(d) for z in zonas_limpias):
                                distrito_match = d
                                break
                                
                        if distrito_match:
                            st.session_state.distrito_manual = distrito_match
                            
                            barrio_match = None
                            for b in madrid_geography[distrito_match]:
                                if any(limpiar_texto(b) in z or z in limpiar_texto(b) for z in zonas_limpias):
                                    barrio_match = b
                                    break
                                    
                            if barrio_match:
                                st.session_state.barrio_manual = barrio_match
                                st.session_state.last_barrio = barrio_match
                            else:
                                st.session_state.barrio_manual = madrid_geography[distrito_match][0]
                                st.session_state.last_barrio = st.session_state.barrio_manual
                                
                    should_rerun = True
                except Exception as e:
                    print(f"🔥 Error de OSM: {e}")
                    st.session_state.direccion_texto = "Ubicación seleccionada"
                    should_rerun = True
                    
                if should_rerun:
                    st.rerun()

        st.divider()
        if st.button("🔮 Predict Optimal Price", type="primary", use_container_width=True):
            payload = {
                "neighbourhood": distrito_seleccionado, 
                "room_type": room_type,
                "latitude": float(st.session_state.lat),
                "longitude": float(st.session_state.lon),
                "accommodates": accommodates,
                "bedrooms": bedrooms,
                "beds": beds,
                "bathrooms": bathrooms,
                "has_ac": int(has_ac),
                "has_pool": int(has_pool),
                "has_elevator": int(has_elevator),
                "has_parking": int(has_parking),
                "host_is_superhost": int(host_is_superhost),
                "number_of_reviews": number_of_reviews,
                "review_scores_rating": review_scores_rating
            }
            
            with st.spinner("Calculating via Stacking Ensemble Model..."):
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.predicted_price = result['predicted_price_euros']
                        st.success("Analysis Complete!")
                    else:
                        st.error(f"Error from API: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Could not connect to the API. Is FastAPI running?")

        if st.session_state.predicted_price is not None:
            st.metric(label="Suggested Nightly Price", value=f"€ {st.session_state.predicted_price:.2f}")

# ==========================================
# 3. PANTALLA DEL INVERSOR (BUSCA CHOLLOS)
# ==========================================
def pantalla_inversor():
    if st.button("⬅️ Back to Home"):
        st.session_state.pantalla_actual = "landing"
        st.rerun()
        
    st.title("🔍 Investor Dashboard: Undervalued Properties")
    st.markdown("Find active listings currently priced below their AI-predicted market value. Maximize your ROI.")
    st.divider()

    # 1. RUTA AL ARCHIVO DE CHOLLOS
    ruta_chollos = os.path.join(current_dir, "..", "data", "chollos_madrid.csv")

    # Si el archivo no existe, mostramos un aviso y paramos la ejecución de esta pantalla
    if not os.path.exists(ruta_chollos):
        st.warning("⚠️ Data file not found.")
        st.info(f"Por favor, asegúrate de generar el archivo **chollos_madrid.csv** y guardarlo en la carpeta `data/`.")
        return

    # 2. CARGAMOS LOS DATOS (Con caché para que sea instantáneo)
    @st.cache_data
    def cargar_chollos():
        df = pd.read_csv(ruta_chollos)
        
        # Aseguramos que existan las columnas clave (si no están, las calculamos si es posible)
        if 'residual' not in df.columns and 'price' in df.columns and 'predicted_price' in df.columns:
            df['residual'] = df['predicted_price'] - df['price']
            
        # Filtramos para quedarnos SOLO con los chollos (donde el modelo dice que vale MÁS de lo que cuesta)
        df_chollos = df[df['residual'] > 0].copy()
        
        # Calculamos el % de descuento
        if len(df_chollos) > 0:
            df_chollos['discount_pct'] = (df_chollos['residual'] / df_chollos['predicted_price']) * 100
            
        # Ordenamos de mayor a menor chollo
        return df_chollos.sort_values(by='residual', ascending=False)

    df = cargar_chollos()

    if df.empty:
        st.warning("No se encontraron propiedades infravaloradas en el dataset actual.")
        return

    # 3. PANELES DE FILTROS INTERACTIVOS
    st.subheader("⚙️ Filter Opportunities")
    c_filt1, c_filt2 = st.columns(2)
    
    with c_filt1:
        max_residual = int(df['residual'].max()) if not df.empty else 100
        min_discount = st.slider("Minimum Savings (€/night)", min_value=0, max_value=max_residual, value=20)
        
    with c_filt2:
        # Detectamos cómo se llama tu columna de distritos (suele ser neighbourhood_group_cleansed o similar)
        col_distrito = 'neighbourhood_group_cleansed' if 'neighbourhood_group_cleansed' in df.columns else ('neighbourhood_group' if 'neighbourhood_group' in df.columns else None)
        
        if col_distrito:
            distritos_disponibles = sorted(df[col_distrito].dropna().unique())
            distritos_seleccionados = st.multiselect("Filter by District", options=distritos_disponibles)
        else:
            distritos_seleccionados = []

    # Aplicamos los filtros al DataFrame
    df_filtrado = df[df['residual'] >= min_discount]
    if distritos_seleccionados and col_distrito:
        df_filtrado = df_filtrado[df_filtrado[col_distrito].isin(distritos_seleccionados)]

    # 4. MÉTRICAS CLAVE (KPIs)
    st.write("<br>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Opportunities Found", len(df_filtrado))
    if len(df_filtrado) > 0:
        m2.metric("Avg. Savings / Night", f"€ {df_filtrado['residual'].mean():.2f}")
        m3.metric("Max Discount", f"{df_filtrado['discount_pct'].max():.1f} %")

    # 5. MAPA DE CALOR INTERACTIVO
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("📍 Heatmap of Bargains")
    
    # Usamos un mapa oscuro para el inversor, da un toque más analítico
    m_inv = folium.Map(location=[40.4168, -3.7038], zoom_start=12, tiles="CartoDB dark_matter")

    for _, row in df_filtrado.head(200).iterrows():
        color_punto = "#00FF00" if row.get('discount_pct', 0) > 40 else "#FF9900"
        
        # 🚨 NUEVO: Añadimos el botón clickeable hacia Airbnb
        url_airbnb = row.get('listing_url', '#')
        html_popup = f"""
        <div style="font-family: Arial; min-width: 160px; padding: 5px;">
            <b>Market Price:</b> €{row.get('price', 0)}<br>
            <b>AI Value:</b> €{row.get('predicted_price', 0):.2f}<br>
            <span style="color: green;"><b>Savings:</b> €{row.get('residual', 0):.2f}</span><br><br>
            <a href="{url_airbnb}" target="_blank" style="background-color: #FF5A5F; color: white; padding: 8px 10px; text-decoration: none; border-radius: 5px; display: block; text-align: center; font-weight: bold;">🔗 View on Airbnb</a>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            color=color_punto,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(html_popup, max_width=300)
        ).add_to(m_inv)

    st_folium(m_inv, width="100%", height=500, key="inversor_map")

    # 6. TABLA DE DATOS CRUDOS
    st.subheader("📋 Detailed Listings")
    
    # 🚨 NUEVO: Añadimos el link a las columnas que se muestran
    cols_to_show = [c for c in ['listing_url', 'latitude', 'longitude', 'price', 'predicted_price', 'residual', 'discount_pct'] if c in df_filtrado.columns]
    
    if col_distrito:
        cols_to_show.insert(1, col_distrito) # Lo ponemos después del link
        
    # 🚨 NUEVO: Usamos column_config para decirle a Streamlit que renderice la URL como un enlace clickeable
    st.dataframe(
        df_filtrado[cols_to_show].style.background_gradient(subset=['residual'], cmap='Greens'),
        use_container_width=True,
        hide_index=True,
        column_config={
            "listing_url": st.column_config.LinkColumn("Airbnb Link", display_text="Open Listing 🔗")
        }
    )

# ==========================================
# 4. MOTOR DE ENRUTAMIENTO 
# ==========================================
if st.session_state.pantalla_actual == "landing":
    pantalla_landing()
elif st.session_state.pantalla_actual == "host":
    pantalla_host()
elif st.session_state.pantalla_actual == "inversor":
    pantalla_inversor()