from datetime import datetime
import pandas as pd
import random
from typing import Dict, List, Optional

class MealScheduler:
    def __init__(self, recommender):
        """
        Inisialisasi scheduler dengan recommender system
        
        Args:
            recommender: Objek recommender system yang sudah di-load
        """
        self.recommender = recommender
        self.schedule = {}

    def generate_schedule(self, user_preferences: Dict, days: int = 7) -> Dict:
        """
        Generate jadwal makan untuk X hari kedepan
        
        Args:
            user_preferences: Preferensi pengguna (riwayat, batasan)
            days: Jumlah hari yang akan di-generate
            
        Returns:
            Dict: Jadwal makan dalam format {tanggal: jadwal_harian}
        """
        schedule = {}
        for day in range(days):
            date = datetime.now().date() + pd.DateOffset(days=day)
            daily_schedule = self._generate_daily_schedule(user_preferences)
            schedule[date] = daily_schedule
        return schedule

    def _generate_daily_schedule(self, user_preferences: Dict) -> Dict:
        """
        Generate jadwal untuk 1 hari dengan constraint nutrisi
        
        Args:
            user_preferences: Preferensi dan batasan pengguna
            
        Returns:
            Dict: Jadwal makan harian dengan 3 waktu makan
        """
        meal_types = ['Sarapan', 'Makan Siang', 'Makan Malam']
        daily_meals = {}

        # Generate meal untuk setiap waktu makan
        for meal_type in meal_types:
            try:
                recommendations = self.recommender.recommend(
                    meal_ids=user_preferences.get('history', []),
                    n=3,
                    meal_type=meal_type
                )
                selected_meal = recommendations.sample(1).iloc[0].to_dict()
                daily_meals[meal_type] = selected_meal
            except Exception as e:
                print(f"Error memilih makanan untuk {meal_type}: {str(e)}")
                daily_meals[meal_type] = {}

        # Validasi total kalori
        if 'max_calories' in user_preferences:
            total_calories = sum(
                meal.get('calories', 0) 
                for meal in daily_meals.values() 
                if isinstance(meal, dict)
            )
            
            if total_calories > user_preferences['max_calories']:
                return self._adjust_schedule(daily_meals, user_preferences)

        return daily_meals

    def _get_meal(self, meal_type: str, preferences: Dict) -> Dict:
        """
        Dapatkan satu makanan untuk waktu makan tertentu
        
        Args:
            meal_type: Jenis waktu makan
            preferences: Preferensi pengguna
            
        Returns:
            Dict: Detail makanan terpilih
        """
        recommendations = self.recommender.recommend(
            meal_ids=preferences.get('history', []),
            n=3,
            meal_type=meal_type
        )
        
        if not recommendations.empty:
            return recommendations.sample(1).iloc[0].to_dict()
        return {}

    def _adjust_schedule(self, schedule: Dict, preferences: Dict) -> Dict:
        """
        Adjust jadwal untuk memenuhi batasan kalori
        
        Args:
            schedule: Jadwal awal
            preferences: Preferensi pengguna
            
        Returns:
            Dict: Jadwal yang sudah disesuaikan
        """
        max_retries = 3
        adjusted = schedule.copy()
        
        for _ in range(max_retries):
            # Cari makanan dengan kalori tertinggi
            max_cal_meal = max(
                adjusted.items(), 
                key=lambda x: x[1].get('calories', 0)
            )
            
            # Cari pengganti yang lebih rendah kalori
            meal_type = max_cal_meal[0]
            current_id = max_cal_meal[1]['id']
            
            try:
                new_recommendations = self.recommender.recommend(
                    meal_ids=[current_id],
                    n=3,
                    meal_type=meal_type
                )
                
                if not new_recommendations.empty:
                    new_meal = new_recommendations.iloc[0].to_dict()
                    adjusted[meal_type] = new_meal
                    
                    # Hitung ulang total kalori
                    new_total = sum(
                        meal.get('calories', 0) 
                        for meal in adjusted.values()
                    )
                    
                    if new_total <= preferences['max_calories']:
                        return adjusted
                        
            except Exception as e:
                print(f"Gagal menyesuaikan jadwal: {str(e)}")
                continue
                
        return adjusted

    def print_schedule(self, schedule: Dict):
        """
        Cetak jadwal makan dalam format yang mudah dibaca
        
        Args:
            schedule: Jadwal makan yang akan dicetak
        """
        for date, meals in schedule.items():
            print(f"\n=== Jadwal {date.strftime('%A, %d %B %Y')} ===")
            for meal_type, details in meals.items():
                print(f"\n{meal_type}:")
                if details:
                    print(f"  - Menu: {details.get('name', 'Tidak tersedia')}")
                    print(f"  - Kalori: {details.get('calories', 0)} kcal")
                    print(f"  - Protein: {details.get('protein', 0)}g")
                else:
                    print("  - Tidak ada rekomendasi yang tersedia")