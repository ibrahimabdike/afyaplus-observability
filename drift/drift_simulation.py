# drift_simulation.py
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

FEATURES = {
    "triage_advisor": {
        "base_rouge_l": 0.42,
        "rouge_volatility": 0.05,
        "base_latency_ms": 800,
        "latency_volatility": 100,
        "base_tokens": 250,
        "token_volatility": 50
    },
    "clinical_protocols": {
        "base_rouge_l": 0.45,
        "rouge_volatility": 0.04,
        "base_latency_ms": 900,
        "latency_volatility": 120,
        "base_tokens": 300,
        "token_volatility": 60
    },
    "safety_protocols": {
        "base_rouge_l": 0.38,
        "rouge_volatility": 0.06,
        "base_latency_ms": 750,
        "latency_volatility": 90,
        "base_tokens": 220,
        "token_volatility": 45
    }
}

def simulate_month(month_idx, n_samples=200):
    data = []
    
    drift_rouge = 0.0
    drift_latency = 0.0
    drift_tokens = 0.0
    
    if month_idx >= 1:
        drift_rouge = -0.05
        drift_latency = 200
        drift_tokens = 50
    
    if month_idx >= 2:
        drift_rouge -= 0.07
        drift_latency += 150
        drift_tokens += 40
    
    feature_list = list(FEATURES.keys())
    
    for i in range(n_samples):
        feature = random.choice(feature_list)
        params = FEATURES[feature]
        
        rouge_l = params["base_rouge_l"] + drift_rouge + np.random.normal(0, params["rouge_volatility"])
        rouge_l = max(0.1, min(0.9, rouge_l))
        
        latency_ms = params["base_latency_ms"] + drift_latency + np.random.normal(0, params["latency_volatility"])
        latency_ms = max(200, latency_ms)
        
        token_count = params["base_tokens"] + drift_tokens + np.random.normal(0, params["token_volatility"])
        token_count = max(50, int(token_count))
        
        data.append({
            "feature": feature,
            "rouge_l": round(rouge_l, 4),
            "latency_ms": round(latency_ms, 1),
            "token_count": token_count,
            "input_length": random.randint(10, 30),
            "timestamp": (datetime(2026, 6 + month_idx, 1) + 
                         timedelta(days=random.randint(0, 30), 
                                  hours=random.randint(0, 23))).isoformat()
        })
    
    return pd.DataFrame(data)

def generate_drift_datasets():
    for month in range(3):
        df = simulate_month(month)
        df.to_csv(f"production_month_{month+1}.csv", index=False)
        print(f"Month {month+1}: {len(df)} records generated")
    
    reference = simulate_month(-1, n_samples=300)
    reference.to_csv("reference_dataset.csv", index=False)
    print("Reference dataset generated")

if __name__ == "__main__":
    generate_drift_datasets()