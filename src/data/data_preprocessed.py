import pandas as pd
import numpy as np
import re
import json
from typing import List, Dict, Any
import os

# Function to estimate the meal type based on food name and nutritional content
def estimate_meal_type(name: str, calories: float, carbs: float) -> str:
    name_lower = name.lower()
    
    # Breakfast indicators
    breakfast_keywords = ['sarapan', 'bubur', 'sereal', 'roti', 'pancake', 'waffle', 'telur dadar']
    
    # Lunch/Dinner indicators
    main_meal_keywords = ['nasi', 'mie', 'pasta', 'ayam', 'daging', 'ikan', 'sup', 'soto', 'gulai']
    
    # Snack indicators
    snack_keywords = ['kue', 'biskuit', 'keripik', 'kerupuk', 'camilan', 'gorengan', 'kacang']
    
    # Check keywords
    if any(keyword in name_lower for keyword in breakfast_keywords):
        return "Sarapan"
    elif any(keyword in name_lower for keyword in snack_keywords) or calories < 150:
        return "Camilan"
    elif any(keyword in name_lower for keyword in main_meal_keywords):
        # Higher carbs often indicates more substantial meals
        if carbs > 30:
            return "Makan Utama"  # Can be used for lunch or dinner
        else:
            return "Makan Ringan"
    else:
        # Default based on calories
        if calories < 250:
            return "Sarapan"
        else:
            return "Makan Utama"

# Function to extract potential ingredients from food name
def extract_ingredients(name: str) -> List[str]:
    name_lower = name.lower()
    
    # Common Indonesian food ingredients dictionary
    ingredient_dict = {
        'nasi': ['beras'],
        'goreng': ['minyak'],
        'bakar': ['bumbu'],
        'ayam': ['ayam'],
        'ikan': ['ikan'],
        'telur': ['telur'],
        'tahu': ['tahu', 'kedelai'],
        'tempe': ['tempe', 'kedelai'],
        'udang': ['udang', 'seafood'],
        'sapi': ['daging sapi'],
        'kambing': ['daging kambing'],
        'sayur': ['sayuran'],
        'kacang': ['kacang'],
        'pedas': ['cabai', 'lada'],
        'manis': ['gula'],
        'asin': ['garam'],
        'santan': ['santan', 'kelapa'],
        'bawang': ['bawang'],
        'mie': ['tepung'],
        'roti': ['tepung', 'ragi'],
        'keju': ['keju', 'susu'],
        'susu': ['susu'],
        'buah': ['buah'],
        'sayuran': ['sayuran'],
        'kangkung': ['kangkung', 'sayuran'],
        'bayam': ['bayam', 'sayuran'],
        'wortel': ['wortel', 'sayuran'],
        'kentang': ['kentang'],
        'jagung': ['jagung'],
        'kecap': ['kecap'],
        'terasi': ['terasi', 'udang'],
        'seafood': ['seafood'],
    }
    
    ingredients = []
    
    # Extract ingredients based on keywords in name
    for keyword, related_ingredients in ingredient_dict.items():
        if keyword in name_lower:
            for ingredient in related_ingredients:
                if ingredient not in ingredients:
                    ingredients.append(ingredient)
    
    # Add default ingredients if none are detected
    if not ingredients:
        ingredients = ['bahan utama', 'bumbu']
    
    return ingredients

# Function to generate tags based on name and nutrition information
def generate_tags(name: str, calories: float, protein: float, fat: float, carbs: float) -> List[str]:
    name_lower = name.lower()
    tags = []
    
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

# Example usage
if __name__ == "__main__":
    # Update path to your actual data location
    input_csv = "C:/Users/MacBook/OneDrive/Dokumen/VS_Code/meal-scheduler/data/raw/nutrition/nutrition_raw.csv"
    output_json = "C:/Users/MacBook/OneDrive/Dokumen/VS_Code/meal-scheduler/data/processed/nutrition/nutrition_processed.csv"
    
    sample_data = process_nutrition_data(input_csv, output_json)
    
    # Print sample of processed data
    if sample_data:
        print("Sample of processed data:")
        for item in sample_data:
            print(json.dumps(item, ensure_ascii=False, indent=2))