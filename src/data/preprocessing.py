import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CLEAN_SAVE_DIR = Path("data/processed/nutrition")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Lakukan preprocessing data"""
    try:
        logger.info("Memulai proses cleaning data...")
        
        # 1. Standardisasi nama kolom
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # 2. Handle missing values
        df = handle_missing_values(df)
        
        # 3. Hapus duplikat
        df = df.drop_duplicates()
        
        # 4. Konversi tipe data
        df = convert_data_types(df)
        
        # 5. Handle outliers
        df = handle_outliers(df)
        
        logger.info("Cleaning data selesai!")
        return df
    except Exception as e:
        logger.error(f"Gagal cleaning data: {str(e)}")
        raise

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values dengan berbagai strategi"""
    # Drop kolom dengan >50% missing
    threshold = len(df) * 0.5
    df = df.dropna(thresh=threshold, axis=1)
    
    # Isi nilai numerik dengan median
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    
    # Isi nilai kategorik dengan modus
    cat_cols = df.select_dtypes(exclude=np.number).columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    return df

def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Konversi tipe data kolom"""
    # Contoh: Konversi kolom tanggal jika ada
    # if 'date' in df.columns:
    #     df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Handle outliers dengan IQR method"""
    num_cols = df.select_dtypes(include=np.number).columns
    
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5*iqr
        upper_bound = q3 + 1.5*iqr
        
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    
    return df

def save_clean_data(df: pd.DataFrame) -> str:
    """Simpan data yang sudah dibersihkan"""
    try:
        CLEAN_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        save_path = CLEAN_SAVE_DIR / "nutrition_clean.parquet"
        df.to_parquet(save_path)
        logger.info(f"Data bersih disimpan di {save_path}")
        return str(save_path)
    except Exception as e:
        logger.error(f"Gagal menyimpan data bersih: {str(e)}")
        raise