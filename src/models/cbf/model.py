import pandas as pd
import joblib
import os
import json
from .feature_engineering import FeatureEngineer

class CBFTrainer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.model_dir = 'models/'
        self.feature_engineer = FeatureEngineer()
        os.makedirs(self.model_dir, exist_ok=True)
        
    def train(self):
        # Baca data dengan format yang benar
        df = pd.read_csv(
            self.data_path,
            converters={
                'ingredients': lambda x: json.loads(x.replace("'", '"')),
                'tags': lambda x: json.loads(x.replace("'", '"'))
            }
        )
        
        # Pastikan tipe data sudah benar
        assert isinstance(df['ingredients'].iloc[0], list), "Ingredients harus list"
        assert isinstance(df['tags'].iloc[0], list), "Tags harus list"
        
        # Proses feature engineering
        feature_matrix = self.feature_engineer.prepare_features(df)
        
        # Simpan model
        joblib.dump(self.feature_engineer.vectorizer, os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
        joblib.dump(self.feature_engineer.scaler, os.path.join(self.model_dir, 'scaler.pkl'))
        joblib.dump(feature_matrix, os.path.join(self.model_dir, 'feature_matrix.pkl'))
        df.to_csv(os.path.join(self.model_dir, 'meal_data.csv'), index=False)
        
        print("Model training completed!")