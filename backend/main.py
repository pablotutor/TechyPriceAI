from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
import pandas as pd
import joblib
import os
from preprocessing import calculate_haversine_distance

# 1. Initialize the FastAPI app
app = FastAPI(
    title="Airbnb Price Predictor API",
    description="API to predict Airbnb prices in Madrid using a Stacking Ensemble model",
    version="1.0.0"
)

# 2. Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Load the Machine Learning Model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "airbnb_pricing_model.joblib")
COLUMNS_PATH = os.path.join(BASE_DIR, "models", "model_columns.joblib")

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    
try:
    model_columns = joblib.load(COLUMNS_PATH)
    print("✅ Model columns loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model columns: {e}")
    model_columns = None

# 4. Enums
class RoomTypeEnum(str, Enum):
    entire_home = "Entire home/apt"
    private_room = "Private room"
    shared_room = "Shared room"
    hotel_room = "Hotel room"
    
class NeighbourhoodEnum(str, Enum):
    barajas = "Barajas"
    carabanchel = "Carabanchel"
    centro = "Centro"
    chamartin = "Chamartín"
    chamberi = "Chamberí"
    ciudad_lineal = "Ciudad Lineal"
    fuencarral = "Fuencarral - El Pardo"
    hortaleza = "Hortaleza"
    latina = "Latina"
    moncloa = "Moncloa - Aravaca"
    moratalaz = "Moratalaz"
    puente_vallecas = "Puente de Vallecas"
    retiro = "Retiro"
    salamanca = "Salamanca"
    san_blas = "San Blas - Canillejas"
    tetuan = "Tetuán"
    usera = "Usera"
    vicalvaro = "Vicálvaro"
    villa_vallecas = "Villa de Vallecas"
    villaverde = "Villaverde"

# 5. Schema
class PropertyData(BaseModel):
    neighbourhood: NeighbourhoodEnum = Field(..., description="Madrid Neighbourhood")
    room_type: RoomTypeEnum = Field(..., description="Apartment Type")
    latitude: float = Field(..., description="Exact Latitud")
    longitude: float = Field(..., description="Exact Longitud")
    
    accommodates: int = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    beds: int = Field(..., gt=0)
    bathrooms: float = Field(..., ge=0)
    
    has_ac: int = Field(default=0)
    has_pool: int = Field(default=0)
    has_elevator: int = Field(default=0)
    has_parking: int = Field(default=0)
    
    host_is_superhost: int = Field(default=0, description="1 if Superhost, 0 otherwise")
    number_of_reviews: int = Field(default=0)
    review_scores_rating: float = Field(default=4.70)
    
    class Config:
        json_schema_extra = {
            "example": {
                "neighbourhood": "Centro",
                "room_type": "Entire home/apt",
                "distance_to_sol_km": 1.2,
                "accommodates": 4,
                "bedrooms": 2,
                "beds": 2,
                "bathrooms": 1.0,
                "has_ac": 1,
                "has_pool": 0,
                "has_elevator": 1,
                "has_parking": 0,
                "host_is_superhost": 1,
                "number_of_reviews": 10,
                "review_scores_rating": 4.7
            }
        }
        
# TRANSLATOR
def transform_user_input(data: PropertyData) -> pd.DataFrame:
    # 1. Start with a base of zeros
    base_data = {col: 0 for col in model_columns}
    
    # 2. Map direct user inputs
    base_data['latitude'] = data.latitude
    base_data['longitude'] = data.longitude
    base_data['accommodates'] = data.accommodates
    base_data['bedrooms'] = data.bedrooms
    base_data['beds'] = data.beds
    base_data['bathrooms'] = data.bathrooms
    base_data['has_ac'] = data.has_ac
    base_data['has_pool'] = data.has_pool
    base_data['has_elevator'] = data.has_elevator
    base_data['has_parking'] = data.has_parking
    
    # 3. Simulate Default Host Capabilities
    base_data['host_is_superhost'] = data.host_is_superhost
    base_data['host_has_profile_pic'] = 1
    base_data['host_identity_verified'] = 1
    base_data['instant_bookable'] = 1
    base_data['has_availability'] = 1
    base_data['host_response_time'] = 4  # Ordinal: 4 means 'within an hour'
    base_data['host_response_rate'] = 100.0
    base_data['host_acceptance_rate'] = 100.0
    
    base_data['availability_30'] = 15
    base_data['availability_60'] = 30
    base_data['availability_90'] = 45
    base_data['availability_365'] = 180
    
    # Base Dates assuming a Host with 1 year of experience
    base_data['days_since_host_since'] = 365 
    
    # 🚨 4. THE "-1" IMPUTATION LOGIC (Mirroring Notebook behavior)
    if data.number_of_reviews == 0:
        base_data['has_reviews'] = 0
        base_data['number_of_reviews'] = 0
        base_data['reviews_per_month'] = -1
        base_data['days_since_first_review'] = -1
        base_data['days_since_last_review'] = -1
        
        # All review scores missing (-1)
        base_data['review_scores_rating'] = -1
        base_data['review_scores_accuracy'] = -1
        base_data['review_scores_cleanliness'] = -1
        base_data['review_scores_checkin'] = -1
        base_data['review_scores_communication'] = -1
        base_data['review_scores_location'] = -1
        base_data['review_scores_value'] = -1
    else:
        # Standard good scores for an active host
        base_data['has_reviews'] = 1
        base_data['number_of_reviews'] = data.number_of_reviews
        base_data['reviews_per_month'] = 1.5
        base_data['days_since_first_review'] = 180  # First review 6 months ago
        base_data['days_since_last_review'] = 15    # Last review 15 days ago
        
        base_data['review_scores_rating'] = data.review_scores_rating
        base_data['review_scores_accuracy'] = 4.8
        base_data['review_scores_cleanliness'] = 4.8
        base_data['review_scores_checkin'] = 4.9
        base_data['review_scores_communication'] = 4.9
        base_data['review_scores_location'] = 4.8
        base_data['review_scores_value'] = 4.7
    
    # 5. GEOSPATIAL FEATURE ENGINEERING
    base_data['distance_to_sol_km'] = calculate_haversine_distance(data.latitude, data.longitude, 40.4168, -3.7038)
    base_data['distance_to_bernabeu_km'] = calculate_haversine_distance(data.latitude, data.longitude, 40.4530, -3.6883)
    base_data['distance_to_metropolitano_km'] = calculate_haversine_distance(data.latitude, data.longitude, 40.4361, -3.5995)
    base_data['distance_to_atocha_km'] = calculate_haversine_distance(data.latitude, data.longitude, 40.4065, -3.6908)
    base_data['distance_to_aeropuerto_km'] = calculate_haversine_distance(data.latitude, data.longitude, 40.4839, -3.5680)
    
    # 6. MATHEMATICAL FEATURE ENGINEERING
    beds_safe = data.beds if data.beds > 0 else 1
    base_data['accommodates_per_bed'] = data.accommodates / beds_safe
    
    persons_safe = data.accommodates if data.accommodates > 0 else 1
    base_data['bathrooms_per_person'] = data.bathrooms / persons_safe
    
    base_data['occupancy_rate_30d'] = (30 - base_data['availability_30']) / 30

    # 7. ONE-HOT ENCODING (Categorical Variables)
    barrio_col = f"neighbourhood_group_cleansed_{data.neighbourhood.value}"
    if barrio_col in base_data:
        base_data[barrio_col] = 1
        
    room_col = f"room_type_{data.room_type.value}"
    if room_col in base_data:
        base_data[room_col] = 1
        
    # Return exactly matching the required model columns
    df = pd.DataFrame([base_data])
    return df[model_columns]



# 6. Create the Prediction Endpoint
@app.post("/predict")
async def predict_price(property: PropertyData):
    if model is None or model_columns is None:
        raise HTTPException(status_code=500, detail="Model or columns not loaded on server.")
    
    try:
        # Pass by the TRANSLATOR first
        df_modelo = transform_user_input(property)
        
        # Make the prediction
        prediction = model.predict(df_modelo)[0]
        
        # Return the result as JSON (Cambiado a Euros porque tu modelo predice en Euros)
        return {
            "predicted_price_euros": round(float(prediction), 2),
            "currency": "EUR"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error making prediction: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Airbnb Price Predictor API is running! 🚀"}