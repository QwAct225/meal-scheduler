from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class FeatureEngineer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.scaler = MinMaxScaler()
    
    def prepare_features(self, df):
        """Tidak perlu konversi tambahan karena data sudah dalam format list"""
        # Gabungkan text features langsung dari list
        df['combined_text'] = df.apply(
            lambda x: ' '.join(x['ingredients']) + ' ' + ' '.join(x['tags']), 
            axis=1
        )
        
        # TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(df['combined_text'])
        
        # Normalisasi fitur numerik
        num_features = self.scaler.fit_transform(
            df[['calories', 'protein', 'fat', 'carbs', 'fiber']]
        )
        
        # Gabungkan fitur
        feature_matrix = np.hstack((tfidf_matrix.toarray(), num_features))
        return feature_matrix