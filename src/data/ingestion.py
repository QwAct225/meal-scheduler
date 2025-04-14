import pandas as pd
from ydata_profiling import ProfileReport
import os
from pathlib import Path
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path configuration
RAW_DATA_PATH = r"C:/Users/MacBook/OneDrive/Dokumen/VS_Code/meal-scheduler/data/nutrition.csv"
RAW_SAVE_DIR = Path("data/raw/nutrition")
PROFILE_REPORT_DIR = Path("reports")

def load_data() -> pd.DataFrame:
    """Load raw data from specified path"""
    try:
        logger.info(f"Memuat data dari {RAW_DATA_PATH}")
        df = pd.read_csv(RAW_DATA_PATH)
        logger.info(f"Data dimuat! Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Gagal memuat data: {str(e)}")
        raise

def validate_data(df: pd.DataFrame) -> bool:
    """Lakukan validasi dasar data"""
    validation_passed = True
    
    # Check missing values
    missing_values = df.isna().sum()
    if missing_values.any():
        logger.warning("Missing values ditemukan:")
        logger.warning(missing_values[missing_values > 0])
        validation_passed = False
    
    # Check duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        logger.warning(f"{dup_count} duplikat ditemukan!")
        validation_passed = False
    
    return validation_passed

def save_raw_data(df: pd.DataFrame) -> str:
    """Simpan data mentah ke folder terstruktur"""
    try:
        RAW_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        save_path = RAW_SAVE_DIR / "nutrition_raw.csv"
        df.to_csv(save_path, index=False)
        logger.info(f"Data mentah disimpan di {save_path}")
        return str(save_path)
    except Exception as e:
        logger.error(f"Gagal menyimpan data mentah: {str(e)}")
        raise

def generate_profile_report(df: pd.DataFrame) -> str:
    """Generate data profiling report"""
    try:
        PROFILE_REPORT_DIR.mkdir(exist_ok=True)
        report_path = PROFILE_REPORT_DIR / "nutrition_profile.html"
        
        profile = ProfileReport(  # Gunakan dari ydata_profiling
            df,
            title="Nutrition Data Profiling",
            explorative=True
        )
        profile.to_file(report_path)
        logger.info(f"Profiling report generated: {report_path}")
        return str(report_path)
    except Exception as e:
        logger.error(f"Gagal membuat profiling report: {str(e)}")
        raise