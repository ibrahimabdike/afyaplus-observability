# drift_pipeline.py
import pandas as pd
import json
from datetime import datetime
from evidently import Report
from evidently.presets import DataDriftPreset
from evidently.metrics import ValueDrift, DriftedColumnsCount

def run_drift_report(month_num, reference_df, current_df):
    report = Report([
        DriftedColumnsCount(),
        DataDriftPreset()
    ])
    
    result = report.run(
        reference_data=reference_df,
        current_data=current_df,
    )
    
    filename = f"drift_report_month_{month_num}.html"
    result.save_html(filename)
    print(f"Saved: {filename}")
    return result

def extract_drift_metrics(result):
    metrics = []
    raw = result.dict()
    
    for metric in raw["metrics"]:
        if metric["config"]["type"] == "evidently:metric_v2:ValueDrift":
            column = metric["config"]["column"]
            p_value = metric["value"]
            metrics.append({
                "column": column,
                "p_value": p_value,
                "drift_detected": p_value < 0.05,
                "drift_score": metric.get("drift_score", 0)
            })
    
    return pd.DataFrame(metrics)

def compute_monthly_means(df):
    return {
        "avg_rouge_l": df["rouge_l"].mean() if "rouge_l" in df.columns else 0,
        "avg_latency_ms": df["latency_ms"].mean() if "latency_ms" in df.columns else 0,
        "avg_token_count": df["token_count"].mean() if "token_count" in df.columns else 0,
        "avg_input_length": df["input_length"].mean() if "input_length" in df.columns else 0,
        "count": len(df)
    }

def run_full_drift_pipeline():
    reference_df = pd.read_csv("reference_dataset.csv")
    monthly_trends = []
    drift_alerts = []
    
    for month in range(1, 4):
        current_df = pd.read_csv(f"production_month_{month}.csv")
        result = run_drift_report(month, reference_df, current_df)
        
        drift_metrics = extract_drift_metrics(result)
        drift_metrics["month"] = month
        drift_metrics.to_csv(f"drift_metrics_month_{month}.csv", index=False)
        
        means = compute_monthly_means(current_df)
        means["month"] = month
        monthly_trends.append(means)
        
        for _, row in drift_metrics.iterrows():
            if row["drift_detected"]:
                drift_alerts.append({
                    "month": month,
                    "column": row["column"],
                    "p_value": row["p_value"],
                    "drift_score": row["drift_score"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"ALERT: Month {month} - {row['column']} drifted (p={row['p_value']:.4f})")
    
    trend_df = pd.DataFrame(monthly_trends)
    trend_df.to_csv("drift_trend_table.csv", index=False)
    print("\nDrift Trend Table:")
    print(trend_df.to_string())
    
    with open("drift_alerts.json", "w") as f:
        json.dump(drift_alerts, f, indent=2)
    print(f"\n{len(drift_alerts)} drift alerts logged.")
    
    return drift_alerts, trend_df

if __name__ == "__main__":
    alerts, trends = run_full_drift_pipeline()