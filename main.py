import logging
from src.data.ingestion import load_data, validate_data, save_raw_data, generate_profile_report
from src.data.preprocessing import clean_data, save_clean_data

def main():
    """Main data preprocessing pipeline"""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 1. Data Ingestion
        raw_df = load_data()
        
        # 2. Data Validation
        if not validate_data(raw_df):
            logging.warning("Validasi data menemukan masalah!")
        
        # 3. Save Raw Data
        raw_path = save_raw_data(raw_df)
        
        # 4. Generate Profile Report
        report_path = generate_profile_report(raw_df)
        
        # 5. Data Cleaning
        clean_df = clean_data(raw_df)
        
        # 6. Save Clean Data
        clean_path = save_clean_data(clean_df)
        
        logging.info(f"Preprocessing selesai! Data bersih tersedia di: {clean_path}")
    
    except Exception as e:
        logging.error(f"Preprocessing gagal: {str(e)}")
        raise

if __name__ == "__main__":
    main()