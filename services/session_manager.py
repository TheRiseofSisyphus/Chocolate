import json
from pathlib import Path
from datetime import datetime
from config import STORAGE_DIR, OPERATOR_PERCENT

class SessionManager:
    def __init__(self, operator_id: int):
        self.operator_id = operator_id
        self.session_file = STORAGE_DIR / f"operator_{operator_id}.json"
        self.data = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agents": [],
            "total_turnover": 0.0,
            "operator_payment": 0.0
        }
        self._load()

    def add_agent(self, agent_name: str, turnover: float, agent_percent: float):
        self.data["agents"].append({
            "name": agent_name,
            "turnover": turnover,
            "percent": agent_percent
        })
        self._update_totals()
        self._save()

    def _update_totals(self):
        self.data["total_turnover"] = sum(a["turnover"] for a in self.data["agents"])
        self.data["operator_payment"] = self.data["total_turnover"] * OPERATOR_PERCENT / 100

    def get_summary(self):
        return {
            "start_time": self.data["start_time"],
            "total_turnover": self.data["total_turnover"],
            "operator_payment": self.data["operator_payment"],
            "agents_count": len(self.data["agents"]),
            "agents": sorted(self.data["agents"], key=lambda x: x["turnover"], reverse=True)
        }

    def _load(self):
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                self.data = json.load(f)

    def _save(self):
        with open(self.session_file, 'w') as f:
            json.dump(self.data, f, indent=2)