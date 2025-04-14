import argparse
from src.models import CBFTrainer, CBFRecommender
from src.utils.scheduler import MealScheduler
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Meal Recommendation System')
    parser.add_argument('--train', action='store_true', help='Retrain model')
    parser.add_argument('--recommend', nargs='+', type=int, help='Get recommendations')
    parser.add_argument('--schedule', action='store_true', help='Generate schedule')
    
    args = parser.parse_args()
    
    if args.train:
        print("Training model...")
        trainer = CBFTrainer('data/processed/nutrition/nutrition_convertion.csv')
        trainer.train()
    
    if args.recommend:
        recommender = CBFRecommender()
        recommendations = recommender.recommend(args.recommend)
        print("\nRecommendations:")
        print(recommendations[['id', 'name', 'type', 'calories']])
    
    if args.schedule:
        scheduler = MealScheduler(CBFRecommender())
        user_prefs = {
            'history': [45, 120, 300],
            'max_calories': 2000
        }
        schedule = scheduler.generate_schedule(user_prefs, days=7)
        pd.DataFrame(schedule).to_html('reports/meal_schedule.html')
        print("Schedule generated!")

if __name__ == "__main__":
    main()