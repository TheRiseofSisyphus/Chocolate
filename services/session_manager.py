import json
from pathlib import Path
from datetime import datetime
from config import STORAGE_DIR, OPERATOR_PERCENT

class SessionManager:
    def __init__(self, operator_id: int):
        self.operator_id = operator_id
        self.session_file = STORAGE_DIR / f"operator_{operator_id}.json"
        self.data = {
            "agents": [],
            "total_turnover": 0.0,
            "operator_payment": 0.0,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def add_agent(self, agent_name: str, turnover: float, agent_percent: float):
        """Добавляем данные агента и сразу пересчитываем итоги"""
        self.data["agents"].append({
            "name": agent_name,
            "turnover": turnover,
            "percent": agent_percent
        })
        self._update_totals()
        self._save()

    def _update_totals(self):
        """Пересчет общих сумм"""
        self.data["total_turnover"] = sum(a["turnover"] for a in self.data["agents"])
        self.data["operator_payment"] = self.data["total_turnover"] * OPERATOR_PERCENT / 100

    def get_summary(self):
        """Возвращаем готовые данные для отчета"""
        return {
            "start_time": self.data["start_time"],
            "total_turnover": self.data["total_turnover"],
            "operator_payment": self.data["operator_payment"],
            "agents_count": len(self.data["agents"]),
            "agents": self.data["agents"]  # Без сортировки для простоты
        }

    def _save(self):
        """Просто сохраняем данные в файл"""
        with open(self.session_file, 'w') as f:
            json.dump(self.data, f, indent=2)