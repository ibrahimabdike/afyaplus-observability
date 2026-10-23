# cost_tracker.py
from dataclasses import dataclass, asdict
import json

@dataclass
class InferenceCost:
    request_id: str
    timestamp: str
    model: str
    feature: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    cost_ksh: float
    latency_ms: float
    success: bool

class CostTracker:
    def __init__(self, log_file="inference_costs.jsonl"):
        self.log_file = log_file
        self._session = []

    def record(self, record: InferenceCost):
        self._session.append(record)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def session_summary(self) -> dict:
        if not self._session:
            return {}
        return {
            "total_requests": len(self._session),
            "total_cost_usd": round(sum(r.cost_usd for r in self._session), 6),
            "avg_cost_per_req_usd": round(sum(r.cost_usd for r in self._session) / len(self._session), 8),
            "total_cost_ksh": round(sum(r.cost_ksh for r in self._session), 2),
        }