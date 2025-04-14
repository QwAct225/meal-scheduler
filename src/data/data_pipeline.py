import logging
from ingestion import load_data, save_raw_data, generate_profile_report
from preprocessing import clean_data, save_clean_data, process_nutrition_data, convertion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_data_pipeline():
    """Pipeline end-to-end: raw -> clean -> enriched"""
    try:
        logger.info("Memulai seluruh pipeline data...")
        
        # [1] Tahap Ingestion
        logger.info("\n=== TAHAP INGESTION ===")
        raw_df = load_data()
        raw_path = save_raw_data(raw_df)
        generate_profile_report(raw_df)
        
        # [2] Tahap Cleaning
        logger.info("\n=== TAHAP CLEANING ===")
        clean_df = clean_data(raw_df)
        save_clean_data(clean_df)
        
        # [3] Tahap Enrichment (Preprocessing)
        logger.info("\n=== TAHAP ENRICHMENT ===")
        process_nutrition_data(
            csv_path=raw_path,
            output_path="data/processed/nutrition/nutrition_processed.json"
        )

        # [4] Tahap Convertion
        logger.info("\n=== TAHAP KONVERSI ===")
        convert_path = convertion()
        
        logger.info("\nPipeline berhasil!")
        logger.info(f"Output akhir: {convert_path}")
        return convert_path
        
    except Exception as e:
        logger.error(f"Pipeline gagal: {str(e)}")
        raise

if __name__ == "__main__":
    run_data_pipeline()