import os
import re
import zipfile
import io
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. LOAD SECRETS
load_dotenv(dotenv_path="../.env")
DB_URL = os.getenv("DATABASE_URL")

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
ZIP_FILE_PATH = DATA_DIR / "UVIndex_Data.zip"

# Updated Mapping including the cities found in your ZIP
CITY_TO_STATE = {
    "Melbourne": "VIC",
    "Sydney": "NSW",
    "Brisbane": "QLD",
    "Perth": "WA",
    "Adelaide": "SA",
    "Hobart": "TAS",
    "Canberra": "ACT",
    "Darwin": "NT",
    "Newcastle": "NSW",
    "Townsville": "QLD",
    "Alice-springs": "NT",
    "Kingston": "TAS"
}

def extract_city_info_from_zip(zf, file_name):
    """Extracts city name from zip entry name and coordinates from CSV content."""
    # Ignore hidden Mac metadata files starting with ._ or inside __MACOSX
    if "__MACOSX" in file_name or os.path.basename(file_name).startswith("._"):
        return None, None, None

    stem = Path(file_name).stem
    match = re.search(r"uv-(.*)-\d{4}", stem)
    if not match:
        return None, None, None
    
    city_name = match.group(1).capitalize()
    
    try:
        with zf.open(file_name) as f:
            df_coords = pd.read_csv(f, nrows=1)
            df_coords.columns = [c.replace('\ufeff', '').strip() for c in df_coords.columns]
            
            lat = float(df_coords['Lat'].iloc[0])
            lon = float(df_coords['Lon'].iloc[0])
            return city_name, lat, lon
    except Exception:
        # Silently skip files that aren't valid CSVs (like the Mac metadata files)
        return None, None, None

def load_cities():
    if not DB_URL:
        print("Error: DATABASE_URL not found in .env file.")
        return

    if not ZIP_FILE_PATH.exists():
        print(f"Error: ZIP file not found at {ZIP_FILE_PATH}")
        return

    engine = create_engine(DB_URL)
    print("Starting City Discovery and Loading...")
    
    processed_cities = set()

    with engine.connect() as conn:
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zf:
            # Filter for CSV files within the ZIP
            csv_files = [name for name in zf.namelist() if name.endswith('.csv') and 'uv-' in name]
            
            for file_name in csv_files:
                city_name, lat, lon = extract_city_info_from_zip(zf, file_name)
                
                if city_name and city_name not in processed_cities:
                    state_code = CITY_TO_STATE.get(city_name)
                    
                    if not state_code:
                        print(f"Skipping {city_name}: No state mapping found.")
                        continue

                    state_res = conn.execute(
                        text("SELECT state_id FROM STATE WHERE state_code = :code"),
                        {"code": state_code}
                    ).fetchone()

                    if state_res:
                        state_id = state_res[0]
                        conn.execute(text("""
                            INSERT INTO CITY (city_name, latitude, longitude, state_id)
                            VALUES (:name, :lat, :lon, :s_id)
                            ON CONFLICT (city_name) DO UPDATE SET 
                                latitude = EXCLUDED.latitude, 
                                longitude = EXCLUDED.longitude
                        """), {"name": city_name, "lat": lat, "lon": lon, "s_id": state_id})
                        
                        print(f"Loaded: {city_name} ({state_code})")
                        processed_cities.add(city_name)
        
        conn.commit()
    print("City loading complete.")

if __name__ == "__main__":
    load_cities()