# dashboard.py
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import pandas as pd
import json
import os
from datetime import datetime
import threading
import time

app = FastAPI(title="AfyaPlus Executive Observability Dashboard")

REQUEST_COUNT = Counter("llm_requests_total", "Total LLM requests")
LATENCY = Histogram("llm_response_latency_seconds", "Response latency")
ERROR_COUNT = Counter("llm_errors_total", "Total LLM errors")
BUDGET_USAGE = Counter("llm_budget_usage_usd", "Budget usage in USD")

class DashboardState:
    def __init__(self):
        self.last_update = None
        self.quality_matrix = None
        self.drift_status = None
        self.budget_status = None
        self.system_health = {"status": "UP", "last_check": None}
        self.exception_count = 0

state = DashboardState()

def load_quality_matrix():
    try:
        if os.path.exists("evaluation/model_comparison_summary.csv"):
            df = pd.read_csv("evaluation/model_comparison_summary.csv")
            return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading quality matrix: {e}")
    return None

def load_drift_status():
    try:
        if os.path.exists("drift/drift_alerts.json"):
            with open("drift/drift_alerts.json") as f:
                alerts = json.load(f)
            
            if os.path.exists("drift/drift_trend_table.csv"):
                trends = pd.read_csv("drift/drift_trend_table.csv")
                latest_month = trends.iloc[-1] if len(trends) > 0 else None
                
                return {
                    "alerts": alerts,
                    "current_month": int(latest_month["month"]) if latest_month is not None else 0,
                    "avg_rouge_l": float(latest_month["avg_rouge_l"]) if latest_month is not None else 0,
                    "avg_latency": float(latest_month["avg_latency_ms"]) if latest_month is not None else 0,
                    "drift_detected": len(alerts) > 0
                }
    except Exception as e:
        print(f"Error loading drift status: {e}")
    return None

def load_budget_status():
    try:
        if os.path.exists("cost/cost_simulation_full.csv"):
            df = pd.read_csv("cost/cost_simulation_full.csv")
            total_cost = df["cost_usd"].sum()
            daily_cost = df.groupby("date")["cost_usd"].sum()
            daily_avg = daily_cost.mean()
            
            daily_cap = 50.0
            monthly_cap = 1500.0
            
            return {
                "daily_spend": float(daily_cost.iloc[-1] if len(daily_cost) > 0 else 0),
                "daily_cap": daily_cap,
                "daily_percent": float(daily_cost.iloc[-1] / daily_cap * 100 if len(daily_cost) > 0 else 0),
                "monthly_spend": float(total_cost),
                "monthly_cap": monthly_cap,
                "monthly_percent": float(total_cost / monthly_cap * 100),
                "daily_avg": float(daily_avg),
                "days_remaining": 30 - len(daily_cost) if len(daily_cost) < 30 else 0,
                "projected_monthly": float(daily_avg * 30)
            }
    except Exception as e:
        print(f"Error loading budget status: {e}")
    return None

def update_dashboard_state():
    state.quality_matrix = load_quality_matrix()
    state.drift_status = load_drift_status()
    state.budget_status = load_budget_status()
    state.system_health["last_check"] = datetime.utcnow().isoformat()
    state.last_update = datetime.utcnow().isoformat()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    update_dashboard_state()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AfyaPlus Executive Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }
            body { background: #f8fafc; margin: 0; padding: 20px; }
            h1 { color: #0f172a; font-size: 28px; }
            h2 { color: #1e293b; font-size: 20px; margin-top: 0; }
            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 1400px; margin: 0 auto; }
            .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
            .full-width { grid-column: 1 / -1; }
            .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }
            .status-up { background: #dcfce7; color: #166534; }
            .status-down { background: #fee2e2; color: #991b1b; }
            .drift-detected { background: #fef3c7; color: #92400e; }
            .progress-bar { background: #e2e8f0; border-radius: 8px; height: 20px; overflow: hidden; margin: 8px 0; }
            .progress-fill { height: 100%; border-radius: 8px; transition: width 0.3s; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; color: white; font-size: 12px; font-weight: 600; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }
            .metric { background: #f1f5f9; padding: 10px; border-radius: 8px; text-align: center; }
            .metric-value { font-size: 24px; font-weight: 700; color: #0f172a; }
            .metric-label { font-size: 12px; color: #64748b; margin-top: 4px; }
            table { width: 100%; border-collapse: collapse; font-size: 14px; }
            th { text-align: left; padding: 8px; background: #f1f5f9; color: #475569; font-weight: 600; }
            td { padding: 8px; border-bottom: 1px solid #e2e8f0; }
            .pass { color: #16a34a; font-weight: 600; }
            .fail { color: #dc2626; font-weight: 600; }
            .last-updated { text-align: right; color: #94a3b8; font-size: 12px; margin-top: 20px; }
            .refresh { animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        </style>
    </head>
    <body>
        <h1>🏥 AfyaPlus Executive Observability Dashboard</h1>
        <div class="grid">
    """
    
    health = state.system_health
    status_class = "status-up" if health.get("status") == "UP" else "status-down"
    html += f"""
            <div class="card">
                <h2>🟢 System Health</h2>
                <div>
                    <span class="status-badge {status_class}">{health.get('status', 'UNKNOWN')}</span>
                    <span style="margin-left: 12px; color: #64748b;">Last check: {health.get('last_check', 'N/A')[:19]}</span>
                </div>
                <div class="metrics-grid" style="margin-top: 12px;">
                    <div class="metric">
                        <div class="metric-value">{state.exception_count}</div>
                        <div class="metric-label">Exceptions (24h)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">0</div>
                        <div class="metric-label">Pending Queue</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">100%</div>
                        <div class="metric-label">Uptime</div>
                    </div>
                </div>
            </div>
    """
    
    quality = state.quality_matrix
    if quality:
        html += """
            <div class="card">
                <h2> Feature Quality Matrix</h2>
                <table>
                    <tr>
                        <th>Model</th>
                        <th>ROUGE-L</th>
                        <th>Judge</th>
                        <th>Correctness</th>
                        <th>Groundedness</th>
                        <th>Status</th>
                    </tr>
        """
        for row in quality:
            status = "" if row.get("avg_rouge_l", 0) > 0.25 else ""
            html += f"""
                    <tr>
                        <td><strong>{row.get('model', 'Unknown')}</strong></td>
                        <td>{row.get('avg_rouge_l', 0):.3f}</td>
                        <td>{row.get('avg_judge', 0):.2f}</td>
                        <td>{row.get('avg_correctness', 0):.2f}</td>
                        <td>{row.get('avg_groundedness', 0):.2f}</td>
                        <td>{status}</td>
                    </tr>
            """
        html += "</table></div>"
    
    budget = state.budget_status
    if budget:
        daily_color = "#22c55e" if budget["daily_percent"] < 80 else "#f59e0b" if budget["daily_percent"] < 95 else "#dc2626"
        monthly_color = "#22c55e" if budget["monthly_percent"] < 80 else "#f59e0b" if budget["monthly_percent"] < 95 else "#dc2626"
        
        html += f"""
            <div class="card">
                <h2>💰 Budget Capital Utilisation</h2>
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>Daily: ${budget['daily_spend']:.2f} / ${budget['daily_cap']:.2f}</span>
                        <span>{budget['daily_percent']:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(100, budget['daily_percent'])}%; background: {daily_color};">
                            {budget['daily_percent']:.1f}%
                        </div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>Monthly: ${budget['monthly_spend']:.2f} / ${budget['monthly_cap']:.2f}</span>
                        <span>{budget['monthly_percent']:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(100, budget['monthly_percent'])}%; background: {monthly_color};">
                            {budget['monthly_percent']:.1f}%
                        </div>
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 12px; color: #64748b;">
                    Daily avg: ${budget['daily_avg']:.2f} | Projected: ${budget['projected_monthly']:.2f}
                </div>
            </div>
        """
    
    drift = state.drift_status
    if drift:
        alert_badge = " Drift Detected" if drift.get("drift_detected") else " No Drift"
        alert_class = "drift-detected" if drift.get("drift_detected") else "status-up"
        
        html += f"""
            <div class="card">
                <h2> Drift Vector Status</h2>
                <div>
                    <span class="status-badge {alert_class}">{alert_badge}</span>
                    <span style="margin-left: 12px; color: #64748b;">Month {drift.get('current_month', 0)}</span>
                </div>
                <div class="metrics-grid" style="margin-top: 12px;">
                    <div class="metric">
                        <div class="metric-value">{drift.get('avg_rouge_l', 0):.3f}</div>
                        <div class="metric-label">ROUGE-L</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{drift.get('avg_latency', 0):.0f}ms</div>
                        <div class="metric-label">Latency</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{len(drift.get('alerts', []))}</div>
                        <div class="metric-label">Active Alerts</div>
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 12px; color: #64748b;">
                    Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
                </div>
            </div>
        """
    
    html += """
        </div>
        <div class="last-updated refresh">Dashboard auto-refreshes every 30 seconds</div>
        <script>
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    
    return html

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/health")
async def health_check():
    return {
        "status": state.system_health.get("status", "UP"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/quality")
async def get_quality():
    update_dashboard_state()
    return state.quality_matrix or {"error": "No quality data available"}

@app.get("/api/drift")
async def get_drift():
    update_dashboard_state()
    return state.drift_status or {"error": "No drift data available"}

@app.get("/api/budget")
async def get_budget():
    update_dashboard_state()
    return state.budget_status or {"error": "No budget data available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)