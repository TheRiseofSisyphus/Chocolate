from dataclasses import dataclass
from typing import List

@dataclass
class Transaction:
    amount: float
    transaction_id: str
    commission: float = 0

@dataclass
class BaibitTransaction:
    amount: float
    rate: float

@dataclass
class ExcelSheetData:
    sheet_name: str  # Добавляем этот атрибут
    full_name: str
    bank: str
    warm_up_purchases: int
    warm_up_rub: float
    start_balance: float
    stop_balance: float
    start_time: str
    end_time: str
    operator: str
    inflows: List[Transaction]
    outflows: List[Transaction]
    baibit: List[BaibitTransaction]
    agent_percent: float
    turnover: float = 0
    agent_payment: float = 0
    operator_payment: float = 0

    def calculate_payments(self):
        self.agent_payment = self.turnover * self.agent_percent / 100
        self.operator_payment = self.turnover * 0.005  # 0.5% для оператора