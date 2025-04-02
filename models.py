from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
import datetime

Base = declarative_base()


class Agents(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)

    sessions = relationship("AgentSessions", back_populates="agent")
    phones = relationship("AgentPhones", back_populates="agent", cascade="all, delete-orphan")
    bank_accounts = relationship("AgentBankAccounts", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.full_name}')>"

class Operators(Base):
    __tablename__ = 'operators'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)

    sessions = relationship("AgentSessions", back_populates="operator")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.full_name}')>"


class AgentSessions(Base):
    __tablename__ = 'agent_sessions'

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    operator_id = Column(Integer, ForeignKey('operators.id'), nullable=False)
    session_start = Column(DateTime, default=datetime.datetime.now)
    session_end = Column(DateTime, nullable=True)
    start_balance = Column(Numeric(18, 2), default=0)
    stop_balance = Column(Numeric(18, 2), default=0)
    agent_percent = Column(Numeric(5, 2), default=0)
    agent_payment = Column(Numeric(18, 2), default=0)
    turnover = Column(Numeric(18, 2), default=0)

    agent = relationship("Agents", back_populates="sessions")
    operator = relationship("Operators", back_populates="sessions")
    transactions = relationship("Transactions", back_populates="agent_session")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.full_name}')>"


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    agent_session_id = Column(Integer, ForeignKey('agent_sessions.id'), nullable=False)
    deposit_id = Column(String(100), nullable=True)
    deposit_amount = Column(Numeric(18, 2), default=0)
    withdraw_id = Column(String(100), nullable=True)
    withdraw_amount = Column(Numeric(18, 2), default=0)
    commission = Column(Numeric(18, 2), default=0)
    transaction_type = Column(String(50), nullable=True)
    exchange_rate = Column(Numeric(18, 8), default=1)
    agent_session = relationship("AgentSessions", back_populates="transactions")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.full_name}')>"

class AgentPhones(Base):
    __tablename__ = 'agent_phones'

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    phone_number = Column(String(30), nullable=False)
    is_primary = Column(Boolean, default=False)

    agent = relationship("Agents", back_populates="phones")


class AgentBankAccounts(Base):
    __tablename__ = 'agent_bank_accounts'

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    bank_name = Column(String(255), nullable=False)
    card_number = Column(String(50), nullable=False)
    account_number = Column(String(100), nullable=True)
    iban = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    agent = relationship("Agents", back_populates="bank_accounts")