import os
import re
import zipfile
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
DB_URL = os.getenv("DATABASE_URL")
BASE_DIR = Path(__file__).resolve().parent.parent
ZIP_FILE_PATH = BASE_DIR / "Data" / "UVIndex_Data.zip"

def get_city_lookup_map(engine):
    """Fetches cities and creates a normalized lookup map."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT city_name FROM CITY"))
        # Normalized (key) -> Official (value)
        return {re.sub(r'[^a-z0-9]', '', row[0].lower()): row[0] for row in result}

def extract_city_year(file_name, lookup_map):
    if "__MACOSX" in file_name or os.path.basename(file_name).startswith("._"):
        return None, None
    
    stem = Path(file_name).stem
    match = re.search(r"uv-(.*)-(\d{4})", stem)
    
    if match:
        raw_name = match.group(1).lower()
        year = int(match.group(2))
        clean_name = re.sub(r'[^a-z0-9]', '', raw_name)
        
        if clean_name in lookup_map:
            return lookup_map[clean_name], year
    return None, None

def normalise_columns(df):
    df.columns = [str(c).replace('\ufeff', '').strip() for c in df.columns]
    if "timestamp" in df.columns and "Date-Time" not in df.columns:
        df = df.rename(columns={"timestamp": "Date-Time"})
    return df

def load_and_aggregate_uv():
    if not DB_URL or not ZIP_FILE_PATH.exists():
        print("Setup error.")
        return

    engine = create_engine(DB_URL)
    lookup_map = get_city_lookup_map(engine)
    all_raw_data = []

    print("Step 0: Extracting and validating raw data...")
    with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zf:
        csv_files = [n for n in zf.namelist() if n.endswith('.csv') and 'uv-' in n]
        
        for file_name in csv_files:
            city, year = extract_city_year(file_name, lookup_map)
            if not city: continue

            try:
                with zf.open(file_name) as f:
                    df = pd.read_csv(f)
                    df = normalise_columns(df)
                    df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
                    df["UV_Index"] = pd.to_numeric(df["UV_Index"], errors="coerce")
                    df = df.dropna(subset=["Date-Time", "UV_Index"])
                    
                    if not df.empty:
                        df["city"] = city
                        df["year"] = year
                        df["date"] = df["Date-Time"].dt.date
                        all_raw_data.append(df[["city", "year", "date", "UV_Index"]])
            except Exception:
                continue

    if not all_raw_data:
        print("No usable data found.")
        return

    uv_raw = pd.concat(all_raw_data, ignore_index=True)

    # Step 1: Daily Peak
    daily = uv_raw.groupby(["city", "year", "date"], as_index=False).agg(daily_peak_uv=("UV_Index", "max"))

    # Step 2: City-Year Stats
    city_year = daily.groupby(["city", "year"], as_index=False).agg(
        uv_low=("daily_peak_uv", "min"),
        uv_high=("daily_peak_uv", "max"),
        uv_median=("daily_peak_uv", "median"),
    )

    # Step 3: National Australia-Year Stats
    australia_year = city_year.groupby("year", as_index=False).agg(
        australian_uv_low=("uv_low", "median"),
        australian_uv_high=("uv_high", "median"),
        australian_uv_median=("uv_median", "median"),
    ).sort_values("year")
    
    australia_year = australia_year.round(4)

    print("Updating UV_INDEX_STAT table...")
    with engine.connect() as conn:
        for _, row in australia_year.iterrows():
            conn.execute(text("""
                INSERT INTO UV_INDEX_STAT (year, australian_uv_low, australian_uv_high, australian_uv_median)
                VALUES (:yr, :lo, :hi, :med)
                ON CONFLICT (year) DO UPDATE SET
                    australian_uv_low = EXCLUDED.australian_uv_low,
                    australian_uv_high = EXCLUDED.australian_uv_high,
                    australian_uv_median = EXCLUDED.australian_uv_median
            """), {"yr": int(row['year']), "lo": row['australian_uv_low'], "hi": row['australian_uv_high'], "med": row['australian_uv_median']})
        conn.commit()
    print(f"Success: {len(australia_year)} national records updated.")

if __name__ == "__main__":
    load_and_aggregate_uv()