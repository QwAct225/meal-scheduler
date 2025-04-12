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
├── reports/
│   └── nutrition_profile.html
├── src/
│   ├── data/
│   │   ├── ingestion.py
│   └── └── preprocessing.py
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
    pip install -r requirements.txt
    ```