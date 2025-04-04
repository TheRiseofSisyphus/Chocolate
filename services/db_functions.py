# db_functions.py

from db import SessionLocal
from models import Agents, AgentSessions, Transactions, AgentBankAccounts, AgentPhones, Operators
from services.excel_processor import ExcelSheetData
from datetime import datetime, date, time

def merge_time_with_today(t: time) -> datetime:
    return datetime.combine(date.today(), t)

def create_operator(username: str):
    db = SessionLocal()
    operator = Operators(username=username)
    db.add(operator)
    db.commit()
    db.refresh(operator)
    db.close()
    return operator


def get_operator_by_username(username: str):
    db = SessionLocal()
    operator = db.query(Operators).filter_by(username=username).first()
    db.close()
    return operator


def start_session(agent_id: int, operator_id: int):
    db = SessionLocal()
    session = AgentSessions(agent_id=agent_id, operator_id=operator_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    db.close()
    return session


def get_active_session_by_operator(operator_id: int):
    db = SessionLocal()
    session = (
        db.query(AgentSessions)
        .filter_by(operator_id=operator_id, session_end=None)
        .order_by(AgentSessions.session_start.desc())
        .first()
    )
    db.close()
    return session


def save_transactions(rows: list[dict], session_id: int):
    db = SessionLocal()
    for row in rows:
        tx = Transactions(
            agent_session_id=session_id,
            deposit_id=row.get("deposit_id"),
            deposit_amount=row.get("deposit_amount", 0),
            withdraw_id=row.get("withdraw_id"),
            withdraw_amount=row.get("withdraw_amount", 0),
            commission=row.get("commission", 0),
            transaction_type=row.get("transaction_type"),
            exchange_rate=row.get("exchange_rate", 1),
        )
        db.add(tx)
    db.commit()
    db.close()


def get_agent_by_full_name(name: str):
    db = SessionLocal()
    agent = db.query(Agents).filter_by(full_name=name).first()
    db.close()
    return agent


def create_agent(full_name: str):
    db = SessionLocal()
    agent = Agents(full_name=full_name)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    db.close()
    return agent


def save_excel_data(data: ExcelSheetData):
    session = SessionLocal()
    try:
        # 🔹 1. Agent
        agent = session.query(Agents).filter_by(full_name=data.full_name).first()
        if not agent:
            agent = Agents(full_name=data.full_name)
            session.add(agent)
            session.flush()  # Чтобы получить agent.id

        # 🔹 2. Operator
        operator = session.query(Operators).filter_by(username=data.operator).first()
        if not operator:
            operator = Operators(username=data.operator)
            session.add(operator)
            session.flush()

        # 🔹 3. Session
        session_obj = AgentSessions(
            agent_id=agent.id,
            operator_id=operator.id,
            session_start=merge_time_with_today(data.start_time),
            session_end=merge_time_with_today(data.end_time),
            start_balance=data.start_balance,
            stop_balance=data.stop_balance,
            agent_percent=data.agent_percent,
            agent_payment=data.agent_payment,
            turnover=data.turnover
        )
        session.add(session_obj)
        session.flush()  # чтобы получить session_obj.id

        # 🔹 4. Transactions: inflow
        for tx in data.inflows:
            session.add(Transactions(
                agent_session_id=session_obj.id,
                deposit_id=tx.transaction_id,
                deposit_amount=tx.amount,
                transaction_type="inflow"
            ))

        # 🔹 5. Transactions: outflow
        for tx in data.outflows:
            session.add(Transactions(
                agent_session_id=session_obj.id,
                withdraw_id=tx.transaction_id,
                withdraw_amount=tx.amount,
                commission=tx.commission,
                transaction_type="outflow"
            ))

        # 🔹 6. Байбит, если есть
        for tx in data.baibit:
            session.add(Transactions(
                agent_session_id=session_obj.id,
                withdraw_amount=tx.amount,
                exchange_rate=tx.rate,
                transaction_type="baibit"
            ))

        # 🔹 7. BankAccount, если указан банк
        if data.bank:
            existing_bank = session.query(AgentBankAccounts).filter_by(agent_id=agent.id, bank_name=data.bank).first()
            if not existing_bank:
                session.add(AgentBankAccounts(
                    agent_id=agent.id,
                    bank_name=data.bank,
                    card_number="неизвестно"  # если есть
                ))

        session.commit()

    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Ошибка при сохранении Excel-данных: {e}")
    finally:
        session.close()