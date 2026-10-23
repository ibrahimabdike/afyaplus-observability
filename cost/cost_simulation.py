# cost_simulation.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from cost_tracker import CostTracker, InferenceCost
from cost_model import calculate_cost, USD_TO_KSH

FEATURES = {
    "triage_advisor": {
        "daily_requests": 8000,
        "avg_prompt_toks": 300,
        "avg_completion_toks": 180,
        "min_quality_score": 0.30
    },
    "clinical_protocols": {
        "daily_requests": 15000,
        "avg_prompt_toks": 350,
        "avg_completion_toks": 220,
        "min_quality_score": 0.35
    },
    "safety_protocols": {
        "daily_requests": 5000,
        "avg_prompt_toks": 250,
        "avg_completion_toks": 140,
        "min_quality_score": 0.28
    }
}

def simulate_30day_costs():
    tracker = CostTracker("cost_simulation.jsonl")
    records = []
    start_date = datetime(2026, 6, 1)
    
    for day in range(30):
        for feature_name, config in FEATURES.items():
            daily_total = config["daily_requests"]
            mini_requests = int(daily_total * 0.75)
            o_requests = daily_total - mini_requests
            
            for model_name, count in [("gpt-4o-mini", mini_requests), ("gpt-4o", o_requests)]:
                for _ in range(min(100, count)):
                    prompt_toks = max(50, int(np.random.normal(
                        config["avg_prompt_toks"], 
                        config["avg_prompt_toks"] * 0.15
                    )))
                    
                    completion_toks = max(20, int(np.random.normal(
                        config["avg_completion_toks"],
                        config["avg_completion_toks"] * 0.15
                    )))
                    
                    cost = calculate_cost(model_name, prompt_toks, completion_toks)
                    
                    quality_base = 0.42 if "4o" in model_name else 0.38
                    quality_noise = np.random.normal(0, 0.04)
                    quality = min(0.9, max(0.1, quality_base + quality_noise))
                    
                    records.append({
                        "date": (start_date + timedelta(days=day)).isoformat()[:10],
                        "feature": feature_name,
                        "model": model_name,
                        "prompt_tokens": prompt_toks,
                        "completion_tokens": completion_toks,
                        "total_tokens": prompt_toks + completion_toks,
                        "cost_usd": cost,
                        "cost_ksh": cost * USD_TO_KSH,
                        "rouge_l_estimate": round(quality, 4),
                        "quality_pass": quality >= config["min_quality_score"]
                    })
    
    return pd.DataFrame(records)

def analyze_cost_data(df):
    projection = df.groupby(["feature", "model"]).agg(
        total_cost_usd=("cost_usd", "sum"),
        total_requests=("feature", "count"),
        avg_cost_per_req=("cost_usd", "mean"),
        avg_tokens_per_req=("total_tokens", "mean")
    ).round(4)
    projection.to_csv("30day_cost_projection.csv")
    print("30-Day Cost Projection:")
    print(projection)
    
    cost_comparison = df.groupby("model").agg(
        avg_cost_per_req=("cost_usd", "mean"),
        avg_prompt_tokens=("prompt_tokens", "mean"),
        avg_completion_tokens=("completion_tokens", "mean"),
        total_cost=("cost_usd", "sum"),
        total_requests=("cost_usd", "count")
    ).round(4)
    cost_comparison.to_csv("cost_per_request_comparison.csv")
    print("\nModel Cost Comparison:")
    print(cost_comparison)
    
    quality_analysis = df[df["quality_pass"]].groupby(["feature", "model"]).agg(
        avg_quality=("rouge_l_estimate", "mean"),
        avg_cost=("cost_usd", "mean"),
        request_count=("cost_usd", "count")
    ).reset_index()
    
    savings_analysis = []
    for feature in quality_analysis["feature"].unique():
        feature_data = quality_analysis[quality_analysis["feature"] == feature]
        cleared = feature_data[feature_data["avg_quality"] >= FEATURES[feature]["min_quality_score"]]
        
        if len(cleared) > 0:
            best_quality = cleared.loc[cleared["avg_quality"].idxmax()]
            low_cost = cleared.loc[cleared["avg_cost"].idxmin()]
            
            savings_analysis.append({
                "feature": feature,
                "best_quality_model": best_quality["model"],
                "best_quality_cost": best_quality["avg_cost"],
                "best_value_model": low_cost["model"],
                "best_value_cost": low_cost["avg_cost"],
                "potential_savings": best_quality["avg_cost"] - low_cost["avg_cost"],
                "monthly_savings_usd": (best_quality["avg_cost"] - low_cost["avg_cost"]) * 
                                       FEATURES[feature]["daily_requests"] * 30
            })
    
    savings_df = pd.DataFrame(savings_analysis)
    savings_df.to_csv("structural_savings_analysis.csv", index=False)
    print("\nStructural Savings Analysis:")
    print(savings_df.to_string())
    
    return projection, cost_comparison, savings_df

if __name__ == "__main__":
    df = simulate_30day_costs()
    df.to_csv("cost_simulation_full.csv", index=False)
    print(f"Generated {len(df)} cost records")
    
    projection, comparison, savings = analyze_cost_data(df)
    
    print("\n" + "="*60)
    print("TOTAL 30-DAY COST SUMMARY")
    print("="*60)
    total_cost = df["cost_usd"].sum()
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Total Requests: {len(df)}")
    print(f"Average Cost/Request: ${(total_cost/len(df)):.6f}")
    print(f"Total Savings Opportunity: ${savings['monthly_savings_usd'].sum():.2f}")