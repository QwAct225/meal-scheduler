# meal-scheduler

## Project Structure
```
meal-scheduler
├── data/
│   ├── raw/
│   │   └── nutrition/
│   │       └── nutrition_raw.csv
│   └── processed/
│       └── nutrition/
│           └── nutrition_clean.parquet
│           └── nutrition_processed.json
│           └── nutrition_convertion.csv
│
├── models/
│   └── feature_nnatrix.pkl
│   └── meal_data.csv
│   └── scaler.pkl
│   └── tfidf_vectorizer.pkl
│
├── reports/
│   └── nutrition_profile.html
│   └── meal_schedule.html
│
├── src/
│   ├── data/
│   │   ├── data_pipeline.py
│   │   ├── ingestion.py
│   │   └── preprocessing.py
│   ├── models/
│   │   └── cbf/
│   │       ├── feature_engineering.py
│   │       ├── model.py
│   │       └── recommender.py
│   └── utils/
│       └── scheduler.py
│
└── .gitignore
└── main.py   
└── README.md
└── requirements.txt
```

## Getting Started

1. **Clone the repository**

    ```bash
    git clone https://github.com/QwAct225/meal-scheduler.git
    cd meal-scheduler
    ```

2. **Prerequisites**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install --user -r requirements.txt
    ```

4. **Training Model CBF**

    ```bash
    python main.py --train          # Train Model
    python main.py --recommend 1    # Recommend Food By ID (CBF)
    python main.py --schedule       # Scheduling Food
    ```

