import pandas as pd
import numpy as np

# ==========================================
# 📊 FEATURE LISTS (CONFIGURATION)
# ==========================================
TARGET = ['price']

COLUMNS_TO_DROP = [
    'id', 'scrape_id', 'last_scraped', 'source', 'name',
    'description', 'neighborhood_overview', 'picture_url', 'host_id',
    'host_url', 'host_name', 'host_location', 'host_about', 'host_listings_count',
    'host_thumbnail_url', 'host_picture_url', 'host_neighbourhood', 
    'host_verifications', 'neighbourhood', 'calendar_updated', 
    'calendar_last_scraped', 'license', 'host_total_listings_count',
    'minimum_minimum_nights', 'maximum_minimum_nights', 
    'minimum_maximum_nights', 'maximum_maximum_nights', 
    'minimum_nights_avg_ntm', 'maximum_nights_avg_ntm', 
    'availability_eoy', 'estimated_occupancy_l365d', 'estimated_revenue_l365d',
    'bathrooms', # The original empty column
]

CATEGORICAL = [
    'neighbourhood_group_cleansed', 'neighbourhood_cleansed', 
    'property_type', 'room_type', 'host_response_time'
]

BOOLEAN = [
    'host_is_superhost', 'host_has_profile_pic', 
    'host_identity_verified', 'has_availability', 'instant_bookable'
]

REVIEWS = [
    'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness', 
    'review_scores_checkin', 'review_scores_communication', 
    'review_scores_location', 'review_scores_value', 'first_review', 
    'last_review', 'reviews_per_month'
]

# ==========================================
# PREPROCESSING FUNCTIONS
# ==========================================

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between 2 geographical points 
    using the Haversine's formula (takes into account the Earth's curvature).
    """
    # Earth Radius
    R = 6371.0

    # Grades into radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine's formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance


# ==========================================
# ⚙️ MAIN PREPROCESSING FUNCTION
# ==========================================

def clean_airbnb_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the raw Airbnb DataFrame and executes all business rules for 
    data cleaning and missing value imputation.
    Safe for both training and inference environments.
    """
    # Work on a copy to avoid altering the original DataFrame in memory
    df_clean = df.copy()

    # 0. Drop unnecessary noise columns
    df_clean = df_clean.drop(columns=COLUMNS_TO_DROP)

    # 1. Target (Price): Remove '$' and ',' symbols, then drop nulls
    if 'price' in df_clean.columns:
        if df_clean['price'].dtype == 'O': # If it's a string/object
            df_clean['price'] = df_clean['price'].str.replace(r'[\$,]', '', regex=True).astype(float)
        df_clean = df_clean.dropna(subset=['price'])

    # 2. Reviews: Create 'has_reviews' flag and fill nulls with -1
    if 'reviews_per_month' in df_clean.columns:
        df_clean['has_reviews'] = df_clean['reviews_per_month'].notna().astype(int)
    
    for col in REVIEWS:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(-1)

    # 3. Host Response Time: Fill nulls with 'Unknown'
    if 'host_response_time' in df_clean.columns:
        df_clean['host_response_time'] = df_clean['host_response_time'].fillna('Unknown')

    # 4. Host Rates: Remove '%' symbol and fill nulls with -1
    rates_cols = ['host_response_rate', 'host_acceptance_rate']
    for col in rates_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.replace('%', '', regex=False)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(-1)

    # 5. Drop "Ghost Hosts" (Missing critical host data)
    host_dropna_cols = ['host_since', 'host_has_profile_pic', 'host_identity_verified']
    host_present_columns = [c for c in host_dropna_cols if c in df_clean.columns]
    df_clean = df_clean.dropna(subset=host_present_columns)

    # 6. Booleans: Fill nulls with 'f' and map everything to 1/0
    bool_fillna_f = ['host_is_superhost', 'has_availability']
    for col in bool_fillna_f:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('f')

    # Map to Machine Learning friendly format (1 and 0)
    for col in BOOLEAN:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].map({'t': 1, 'f': 0, 'True': 1, 'False': 0, True: 1, False: 0})

    # 7. Extract numeric values from bathrooms_text
    if 'bathrooms_text' in df_clean.columns:
        # Extract the first float found in the string
        df_clean['bathrooms'] = df_clean['bathrooms_text'].str.extract(r'(\d+\.?\d*)').astype(float)
        df_clean = df_clean.drop(columns=['bathrooms_text'])

    # 8. Grouped Imputation (based on 'accommodates' capacity)
    global_imp = ["bedrooms", "bathrooms", "beds"]
    if 'accommodates' in df_clean.columns:
        for col in global_imp:
            if col in df_clean.columns:
                # Attempt 1: Group median based on how many people the listing accommodates
                df_clean[col] = df_clean[col].fillna(
                    df_clean.groupby('accommodates')[col].transform('median')
                )
                # Attempt 2: Global median fallback if the entire group was null
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                
    # ==========================================
    # 9. CATEGORICAL VARIABLES AND TEXT
    # ==========================================
        
    # Extract "Premium Features" from Amenities (Feature Engineering)
    if 'amenities' in df_clean.columns:
        # Lower case
        amenities_str = df_clean['amenities'].str.lower()
        
        # Use Regex + Binary column (1/0)
        df_clean['has_ac'] = amenities_str.str.contains(r'air conditioning|ac').astype(int)
        df_clean['has_pool'] = amenities_str.str.contains(r'pool').astype(int)
        df_clean['has_elevator'] = amenities_str.str.contains(r'elevator').astype(int)
        df_clean['has_parking'] = amenities_str.str.contains(r'parking|garage').astype(int)
        
        # Drop original column
        df_clean = df_clean.drop(columns=['amenities'])
    

    # 10. Geospatial engineering: Distance to Puerta del Sol
    if 'latitude' in df_clean.columns and 'longitude' in df_clean.columns:
        # Coordinates of Puerta del Sol (Madrid)
        SOL_LAT = 40.4168
        SOL_LON = -3.7038
        
        df_clean['distance_to_sol_km'] = calculate_haversine_distance(
            df_clean['latitude'], 
            df_clean['longitude'], 
            SOL_LAT, 
            SOL_LON
        )

    return df_clean


def prepare_for_modeling(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the DataFrame cleaned and makes transformations and feature engineering in order to 
    feed the model our data in the right format.
    """
    df_model = df_clean.copy()
    
    # Listing url as index
    if 'listing_url' in df_model.columns:
        df_model = df_model.set_index('listing_url')

    # ==========================================
    # 0. Dates treatment (Dates -> Integers)
    # ==========================================
    date_cols = ['host_since', 'first_review', 'last_review']
    
    # Today's date as reference
    reference_date = pd.to_datetime('today') 
    
    for col in date_cols:
        if col in df_model.columns:
            # Force dates
            df_model[col] = pd.to_datetime(df_model[col], errors='coerce')
            
            # Calculate days of difference
            df_model[f'days_since_{col}'] = (reference_date - df_model[col]).dt.days
            
            # If null -> fillna with -1
            df_model[f'days_since_{col}'] = df_model[f'days_since_{col}'].fillna(-1).astype(int)
            
            # Drop the original column
            df_model = df_model.drop(columns=[col])

    # ==========================================
    # 1. Drop noise and non-predictive columns
    # ==========================================
    cols_to_drop = ['property_type', 'neighbourhood_cleansed'] 
    present_cols = [c for c in cols_to_drop if c in df_model.columns]
    df_model = df_model.drop(columns=present_cols)

    # ==========================================
    # 2. Ordinal Encoding: host_response_time
    # ==========================================
    response_map = {
        'Unknown': 0,
        'a few days or more': 1,
        'within a day': 2,
        'within a few hours': 3,
        'within an hour': 4
    }
    if 'host_response_time' in df_model.columns:
        df_model['host_response_time'] = df_model['host_response_time'].map(response_map).fillna(0).astype(int)

    # ==========================================
    # 3. One-Hot Encoding (Dummy Variables)
    # ==========================================
    cols_to_dummy = ['neighbourhood_group_cleansed', 'room_type']
    present_dummies = [c for c in cols_to_dummy if c in df_model.columns]
    
    if present_dummies:
        # EL TRUCO: dtype=int fuerza que salgan 0 y 1 en lugar de False y True
        df_model = pd.get_dummies(df_model, columns=present_dummies, drop_first=True, dtype=int)
        
    # ==========================================
    # 4. Feature engineering (GEOSPATIAL)
    # ==========================================
    if 'latitude' in df_clean.columns and 'longitude' in df_clean.columns:
        # Key coordinates in Madrid
        madrid_pois = {
            #'sol': (40.4168, -3.7038),          # Center
            'bernabeu': (40.4530, -3.6883),      # Real Madrid / Finance zone
            'metropolitano': (40.4361, -3.5995), # Atlético de Madrid
            'atocha': (40.4065, -3.6908),        # Train principal station (AVE)
            'aeropuerto': (40.4839, -3.5680)     # Barajas Airport
        }
        
        # Calculate distance to each apartment
        for poi_name, coords in madrid_pois.items():
            poi_lat, poi_lon = coords
            df_clean[f'distance_to_{poi_name}_km'] = calculate_haversine_distance(
                df_clean['latitude'], 
                df_clean['longitude'], 
                poi_lat, 
                poi_lon
            )
        
    # ==========================================
    # 5. Feature engineering
    # ==========================================
    # 1. Index of luxury (Bathrooms per person)
    if 'bathrooms' in df_model.columns and 'accommodates' in df_model.columns:
        df_model['bathrooms_per_person'] = df_model['bathrooms'] / df_model['accommodates'].replace(0, 1)
        
    # 2. Index of aglomeration (Accomodates per bed)
    if 'accommodates' in df_model.columns and 'beds' in df_model.columns:
        df_model['accommodates_per_bed'] = df_model['accommodates'] / df_model['beds'].replace(0, 1)
        
    # 3. Proxy of demand (Occupancy rate in 30 days)
    if 'availability_30' in df_model.columns:
        df_model['occupancy_rate_30d'] = (30 - df_model['availability_30']) / 30

    return df_model