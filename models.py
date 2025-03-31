from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
import datetime

Base = declarative_base()


class Agents(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    bank_name = Column(String(255), nullable=True)

    sessions = relationship("AgentSessions", back_populates="agent")


class Operators(Base):
    __tablename__ = 'operators'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)

    sessions = relationship("AgentSessions", back_populates="operator")


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


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    agent_session_id = Column(Integer, ForeignKey('agent_sessions.id'), nullable=False)
    deposit_id = Column(String(100), nullable=True)
    deposit_amount = Column(Numeric(18, 2), default=0)
    withdraw_id = Column(String(100), nullable=True)
    withdraw_amount = Column(Numeric(18, 2), default=0)
    commission = Column(Numeric(18, 2), default=0)

    agent_session = relationship("AgentSessions", back_populates="transactions")
