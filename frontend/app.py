import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import json
import os
import unicodedata

# ==========================================
# 1. CONFIGURACIÓN Y MEMORIA (State Management)
# ==========================================
if "lat" not in st.session_state:
    st.session_state.lat = 40.4168
if "lon" not in st.session_state:
    st.session_state.lon = -3.7038
if "last_barrio" not in st.session_state:
    st.session_state.last_barrio = None
if "direccion_texto" not in st.session_state:
    st.session_state.direccion_texto = "Puerta del Sol, Madrid"
    
# 🚨 Variables maestras para los desplegables (Sin usar "key")
if "distrito_manual" not in st.session_state:
    st.session_state.distrito_manual = "Centro"
if "barrio_manual" not in st.session_state:
    st.session_state.barrio_manual = "Sol"
    
if "predicted_price" not in st.session_state:
    st.session_state.predicted_price = None

# Cargar GeoJSON
current_dir = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.join(current_dir, "..", "data", "neighbourhoods.geojson")
geojson_data = None
try:
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
except FileNotFoundError:
    pass

st.set_page_config(page_title="Airbnb AI Pricer", page_icon="🏠", layout="wide")
st.title("🏠 AI-Powered Airbnb Pricer (Madrid)")
st.markdown("Discover the optimal nightly price for your Airbnb using our Machine Learning model.")

API_URL = "http://127.0.0.1:8000/predict"
geolocator = Nominatim(user_agent="airbnb_pricer_madrid_app")

# ==========================================
# 2. DICCIONARIOS DE DATOS
# ==========================================
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

# ==========================================
# 3. INTERFAZ GRÁFICA (Layout)
# ==========================================
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.header("📍 Property Details")
    
    # 🚨 DESPLEGABLES INTELIGENTES (Usando index en lugar de key)
    lista_distritos = list(madrid_geography.keys())
    idx_d = lista_distritos.index(st.session_state.distrito_manual) if st.session_state.distrito_manual in lista_distritos else 0
    distrito_seleccionado = st.selectbox("1. Select District", lista_distritos, index=idx_d)
    
    lista_barrios = madrid_geography[distrito_seleccionado]
    idx_b = lista_barrios.index(st.session_state.barrio_manual) if st.session_state.barrio_manual in lista_barrios else 0
    barrio_seleccionado = st.selectbox("2. Select Neighborhood", lista_barrios, index=idx_b)
    
    # Actualizamos la memoria con lo que muestra la pantalla
    st.session_state.distrito_manual = distrito_seleccionado
    st.session_state.barrio_manual = barrio_seleccionado
    
    # LISTENER: Si el usuario cambia el barrio a mano
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
            # Pedimos detalles extra a OpenStreetMap (addressdetails=True)
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
                
                # 🚨 AÑADIMOS EL BUSCADOR BULLDOZER AQUÍ TAMBIÉN 🚨
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
                st.rerun() # Recargamos para que se actualicen los desplegables y el mapa naranja
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
    
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15, tiles="CartoDB positron")
    
    # 🚨 MAGIA UX: MAPA COMPLETO CON COLORES CORPORATIVOS (ESTILO AIRBNB)
    if geojson_data:
        distrito_actual = limpiar_texto(st.session_state.distrito_manual)
        barrio_actual = limpiar_texto(st.session_state.barrio_manual)
        barrios_del_distrito = [limpiar_texto(b) for b in madrid_geography.get(st.session_state.distrito_manual, [])]
        
        def style_function(feature):
            props = feature.get('properties', {})
            barrio_geojson = limpiar_texto(props.get('neighbourhood', ''))
            distrito_geojson = limpiar_texto(props.get('neighbourhood_group', ''))
            
            # 1. PROTAGONISTA: El barrio seleccionado (Rojo exacto de Airbnb)
            if barrio_geojson == barrio_actual:
                return {
                    "fillColor": "#FF5A5F", # Rojo Airbnb
                    "color": "#FF5A5F",     # Borde rojo
                    "weight": 3,            # Borde grueso para destacar
                    "fillOpacity": 0.7      # Bastante sólido
                }
            # 2. CONTEXTO: Otros barrios de TU distrito (Rojo suave)
            elif distrito_geojson == distrito_actual or barrio_geojson in barrios_del_distrito:
                return {
                    "fillColor": "#FF5A5F", 
                    "color": "#FF5A5F",     
                    "weight": 2,            
                    "fillOpacity": 0.15     # Muy translúcido para no robar protagonismo
                }
            # 3. EL RESTO DE MADRID: Fondo gris elegante
            else:
                return {
                    "fillColor": "#888888", # Gris oscuro (contrasta con el mapa claro)
                    "color": "#666666",     # Borde gris sutil
                    "weight": 1.5,          # Borde extra fino para que se fusionen visualmente
                    "fillOpacity": 0.15      # Opacidad media
                }

        tiene_distrito = 'neighbourhood_group' in str(geojson_data)
        hover_tooltip = folium.GeoJsonTooltip(
            fields=['neighbourhood_group', 'neighbourhood'] if tiene_distrito else ['neighbourhood'],
            aliases=['📍 District:', '🏘️ Neighbourhood:'] if tiene_distrito else ['🏘️ Barrio:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 13px; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);")
        )

        # Pintamos todo Madrid de nuevo, pero con la nueva jerarquía de colores
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
    
    # ==========================================
    # 4. LÓGICA DE CLIC EN EL MAPA (El Bulldozer)
    # ==========================================
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
                    
                    # 1. LA CALLE
                    calle = addr.get('road', addr.get('pedestrian', addr.get('square', '')))
                    numero = addr.get('house_number', '').replace(',', '')
                    if calle:
                        st.session_state.direccion_texto = f"{calle} {numero}".strip()
                    else:
                        st.session_state.direccion_texto = "Ubicación en el mapa"
                    
                    # 2. EL BUSCADOR BULLDOZER (A prueba de tildes y caos geográfico)
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
                            # Fallback si OSM sabe el distrito pero no el barrio
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
    # ==========================================
    # 5. CONEXIÓN CON EL BACKEND (Predicción)
    # ==========================================
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
                    # 🚨 GUARDAMOS EL PRECIO EN LA MEMORIA
                    st.session_state.predicted_price = result['predicted_price_euros']
                    st.success("Analysis Complete!")
                else:
                    st.error(f"Error from API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the API. Is FastAPI running?")

    # 🚨 MOSTRAMOS EL PRECIO SIEMPRE QUE HAYA UNO EN MEMORIA (Fuera del botón)
    if st.session_state.predicted_price is not None:
        st.metric(label="Suggested Nightly Price", value=f"€ {st.session_state.predicted_price:.2f}")