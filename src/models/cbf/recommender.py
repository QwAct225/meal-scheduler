import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os

class CBFRecommender:
    def __init__(self):
        self.model_dir = 'models/'
        self.load_models()
        
    def load_models(self):
        self.vectorizer = joblib.load(os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl'))
        self.feature_matrix = joblib.load(os.path.join(self.model_dir, 'feature_matrix.pkl'))
        self.meal_data = pd.read_csv(os.path.join(self.model_dir, 'meal_data.csv'))
        
    def recommend(self, meal_ids, n=5, meal_type=None):
        indices = self.meal_data[self.meal_data['id'].isin(meal_ids)].index
        input_features = self.feature_matrix[indices]
        
        similarities = cosine_similarity(input_features, self.feature_matrix)
        avg_similarities = similarities.mean(axis=0)
        
        # Filter by meal type
        valid_indices = np.arange(len(self.meal_data))
        if meal_type:
            mask = self.meal_data['type'] == meal_type
            valid_indices = valid_indices[mask]
            avg_similarities = avg_similarities[mask]
            
        # Get top recommendations
        top_indices = (-avg_similarities).argsort()[:n + len(meal_ids)]
        recommendations = []
        
        for idx in top_indices:
            meal_id = self.meal_data.iloc[valid_indices[idx]]['id']
            if meal_id not in meal_ids:
                recommendations.append(meal_id)
            if len(recommendations) == n:
                break
                
        return self.meal_data[self.meal_data['id'].isin(recommendations)]