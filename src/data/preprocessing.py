import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import csv
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CLEAN_SAVE_DIR = Path("data/processed/nutrition")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Lakukan preprocessing data"""
    try:
        logger.info("Memulai proses cleaning data...")
        
        # 1. Standardisasi nama kolom
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        df = df.rename(columns={
            'carbohydrate': 'carbs',
            'proteins': 'protein'
        })

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

def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tambahkan fitur: meal_type, ingredients, tags, fiber"""
    try:
        logger.info("Memulai proses enrichment data...")
        
        # 1. Generate meal type
        df['type'] = df.apply(
            lambda row: estimate_meal_type(row['name'], row['calories'], row['carbs']),
            axis=1
        )
        
        # 2. Extract ingredients
        df['ingredients'] = df['name'].apply(extract_ingredients)
        
        # 3. Generate tags
        df['tags'] = df.apply(
            lambda row: generate_tags(row['name'], row['calories'], row['protein'], row['fat'], row['carbs']),
            axis=1
        )
        
        # 4. Estimate fiber
        df['fiber'] = df.apply(
            lambda row: estimate_fiber(row['name'], row['carbs']),
            axis=1
        )
        
        logger.info("Enrichment data selesai!")
        return df
    except Exception as e:
        logger.error(f"Gagal enrichment data: {str(e)}")
        raise

def estimate_meal_type(name: str, calories: float, carbs: float) -> str:
    name_lower = name.lower()
    
    # Sarapan: Makanan ringan atau khas pagi hari
    breakfast_keywords = [
        'sarapan', 'bubur', 'sereal', 'roti', 'pancake', 
        'waffle', 'telur', 'oatmeal', 'yogurt', 'smoothie',
        'buah', 'jus', 'susu', 'kopi', 'teh'
    ]
    
    # Makan Siang: Makanan utama dengan kalori sedang
    lunch_keywords = [
        'nasi', 'ayam', 'daging', 'ikan', 'sup', 'soto',
        'gado-gado', 'pecel', 'rawon', 'bakso', 'mie', 'sate',
        'tumis', 'capcai', 'sayur', 'gado', 'pecel'
    ]
    
    # Makan Malam: Makanan berat atau tinggi kalori
    dinner_keywords = [
        'steak', 'rendang', 'gulai', 'kambing', 'bebek',
        'sop buntut', 'iga bakar', 'martabak', 'pasta',
        'lasagna', 'pizza', 'kari'
    ]
    
    # Kategori berdasarkan kalori
    if any(keyword in name_lower for keyword in breakfast_keywords) or calories < 300:
        return "Sarapan"
    elif any(keyword in name_lower for keyword in dinner_keywords) or calories > 600:
        return "Makan Malam"
    elif any(keyword in name_lower for keyword in lunch_keywords) or (300 <= calories <= 600 and carbs > 20):
        return "Makan Siang"
    else:
        # Default untuk makanan dengan kalori 300-600
        return "Makan Siang"

def extract_ingredients(name: str) -> List[str]:
    name_lower = name.lower()
    
    ingredient_dict = {
        # Buah-buahan
        'apel': ['apel'], 'pisang': ['pisang'], 'jeruk': ['jeruk'],
        'mangga': ['mangga'], 'anggur': ['anggur'], 'pepaya': ['pepaya'],
        'semangka': ['semangka'], 'melon': ['melon'], 'nanas': ['nanas'],
        'stroberi': ['stroberi'], 'buah': ['buah'], 'alpukat': ['alpukat'],
        
        # Protein
        'ayam': ['ayam', 'bumbu'], 'sapi': ['daging sapi', 'bumbu'], 'babi': ['babi', 'bumbu'],
        'ikan': ['ikan', 'bumbu'], 'udang': ['udang', 'bumbu'], 'telur': ['telur', 'bumbu'],
        'bebek': ['bebek', 'bumbu'], 'kambing': ['kambing', 'bumbu'], 'burung': ['burung', 'bumbu'],
        'domba': ['domba', 'bumbu'], 'angsa': ['angsa', 'bumbu'], 'belibing': ['belibing', 'bumbu'],
        'kerang': ['kerang', 'bumbu'], 'cumi': ['cumi', 'bumbu'], 'kepiting': ['kepiting', 'bumbu'],
        
        
        # Sayuran
        'sayur': ['sayuran'], 'kangkung': ['kangkung'],
        'bayam': ['bayam'], 'wortel': ['wortel'], 'brokoli': ['brokoli'],
        
        # Karbohidrat
        'nasi': ['beras'], 'mie': ['tepung terigu'],
        'roti': ['tepung terigu'], 'kentang': ['kentang'], 'jagung': ['jagung']
    }
    
    ingredients = []
    
    # Mencocokkan bahan dari nama makanan
    for keyword, items in ingredient_dict.items():
        if keyword in name_lower:
            ingredients.extend(items)
    
    # Menghapus duplikat dan mengembalikan
    return list(set(ingredients)) or ['bahan utama', 'bumbu']

# Function to generate tags based on name and nutrition information
def generate_tags(name: str, calories: float, protein: float, fat: float, carbs: float) -> List[str]:
    name_lower = name.lower()
    tags = []

    snack_keywords = ['kue', 'biskuit', 'keripik', 'kerupuk', 'camilan']
    if any(keyword in name_lower for keyword in snack_keywords):
        tags.append('camilan')
    
    # Method of cooking
    cooking_methods = {
        'goreng': 'goreng', 
        'bakar': 'bakar', 
        'rebus': 'rebus', 
        'kukus': 'kukus',
        'panggang': 'panggang', 
        'tumis': 'tumis',
        'kuah': 'berkuah'
    }
    
    for method, tag in cooking_methods.items():
        if method in name_lower:
            tags.append(tag)
    
    # Flavor profile
    if 'pedas' in name_lower or 'rica' in name_lower or 'balado' in name_lower:
        tags.append('pedas')
    if 'manis' in name_lower:
        tags.append('manis')
    if 'asin' in name_lower:
        tags.append('asin')
    if 'asam' in name_lower:
        tags.append('asam')
    
    # Categories based on main ingredients
    if any(ingredient in name_lower for ingredient in ['ayam', 'sapi', 'kambing', 'daging']):
        tags.append('daging')
    if any(ingredient in name_lower for ingredient in ['ikan', 'udang', 'cumi', 'kerang', 'kepiting', 'seafood']):
        tags.append('seafood')
    if any(ingredient in name_lower for ingredient in ['tahu', 'tempe', 'kacang', 'kedelai']):
        tags.append('nabati')
    if any(ingredient in name_lower for ingredient in ['sayur', 'kangkung', 'bayam', 'wortel', 'brokoli']):
        tags.append('sayuran')
    
    # Nutrition-based tags
    if protein >= 15:
        tags.append('protein tinggi')
    if fat < 5:
        tags.append('rendah lemak')
    elif fat > 15:
        tags.append('tinggi lemak')
    if carbs < 10:
        tags.append('rendah karbo')
    elif carbs > 30:
        tags.append('tinggi karbo')
    if calories < 200:
        tags.append('rendah kalori')
    elif calories > 400:
        tags.append('tinggi kalori')
    
    # Add cultural indicators if possible
    cultural_indicators = {
        'padang': 'padang',
        'jawa': 'jawa',
        'sunda': 'sunda',
        'bali': 'bali',
        'aceh': 'aceh',
        'manado': 'manado',
        'minang': 'minang'
    }
    
    for indicator, tag in cultural_indicators.items():
        if indicator in name_lower:
            tags.append(tag)
            tags.append('tradisional')
            break
    
    # Add 'tradisional' tag for common Indonesian dishes
    traditional_dishes = ['nasi goreng', 'soto', 'rendang', 'sate', 'gado-gado', 'pecel', 'rawon', 
                         'bakso', 'mie goreng', 'gudeg', 'opor', 'ketoprak', 'pempek']
    if any(dish in name_lower for dish in traditional_dishes):
        if 'tradisional' not in tags:
            tags.append('tradisional')
    
    return tags

# Estimate fiber content based on ingredients and other nutrients
def estimate_fiber(name: str, carbs: float) -> float:
    name_lower = name.lower()
    
    # High fiber foods
    high_fiber_indicators = ['sayur', 'kacang', 'biji', 'buah', 'sereal', 'oat', 'brokoli', 
                            'kangkung', 'bayam', 'wortel', 'apel', 'pisang', 'pepaya']
    
    base_fiber = carbs * 0.05  # Base estimate: 5% of carbs
    
    # Adjust based on food name indicators
    if any(indicator in name_lower for indicator in high_fiber_indicators):
        fiber = base_fiber * 2  # Double for high fiber foods
    else:
        fiber = base_fiber
    
    # Cap to reasonable values
    fiber = min(max(fiber, 0.5), carbs * 0.4)  # Fiber shouldn't exceed 40% of carbs
    
    return round(fiber, 1)

# Main processing function
def process_nutrition_data(csv_path: str, output_path: str = None):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Check if required columns exist
        required_columns = ['id', 'calories', 'proteins', 'fat', 'carbohydrate', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return
        
        # Process each row
        processed_data = []
        
        for _, row in df.iterrows():
            # Handle potential NaN values
            calories = float(row['calories']) if not pd.isna(row['calories']) else 0.0
            proteins = float(row['proteins']) if not pd.isna(row['proteins']) else 0.0
            fat = float(row['fat']) if not pd.isna(row['fat']) else 0.0
            carbs = float(row['carbohydrate']) if not pd.isna(row['carbohydrate']) else 0.0
            name = str(row['name']) if not pd.isna(row['name']) else "Unknown Food"
            
            # Generate enriched data
            meal_type = estimate_meal_type(name, calories, carbs)
            ingredients = extract_ingredients(name)
            tags = generate_tags(name, calories, proteins, fat, carbs)
            fiber = estimate_fiber(name, carbs)
            
            # Create structured entry
            entry = {
                "id": int(row['id']),
                "name": name,
                "type": meal_type,
                "calories": calories,
                "protein": proteins,
                "fat": fat,
                "carbs": carbs,
                "fiber": fiber,
                "ingredients": ingredients,
                "tags": tags
            }
            
            processed_data.append(entry)
        
        # Save to JSON file if output path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            print(f"Processed data saved to {output_path}")
        
        # Return sample of processed data (first 5 entries)
        return processed_data[:5]
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return None

def convertion():
    """Buat file khusus untuk CBF dari data processed"""
    try:
        # Baca data processed sebagai JSON
        with open('data/processed/nutrition/nutrition_processed.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Konversi ke DataFrame
        df = pd.DataFrame(data)
        
        # Konversi list ke string JSON yang valid
        df['ingredients'] = df['ingredients'].apply(lambda x: json.dumps(x, ensure_ascii=False))
        df['tags'] = df['tags'].apply(lambda x: json.dumps(x, ensure_ascii=False))
        
        # Simpan dengan format CSV yang benar
        cbf_path = "data/processed/nutrition/nutrition_convertion.csv"
        df.to_csv(
            cbf_path,
            index=False,
            quoting=csv.QUOTE_ALL,
            escapechar='\\',
            encoding='utf-8'
        )
        
        logger.info(f"File CBF-ready dibuat: {cbf_path}")
        return cbf_path
        
    except Exception as e:
        logger.error(f"Gagal membuat data CBF: {str(e)}")
        raise