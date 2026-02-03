from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./sql_app.db" # 本地SQLite数据库文件

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AgentDB(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True) # Agent ID
    name = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    wallet_address = Column(String, unique=True)
    referral_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tasks_posted = relationship("TaskDB", foreign_keys="TaskDB.poster_id", back_populates="poster")
    tasks_claimed = relationship("TaskDB", foreign_keys="TaskDB.claimer_id", back_populates="claimer")

class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True) # Task ID (UUID)
    title = Column(String, index=True)
    description = Column(String)
    amount = Column(Float) # 赏金金额
    status = Column(String, default="open") # open, claimed, submitted, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline_at = Column(DateTime, nullable=True) # 任务截止时间

    poster_id = Column(String, ForeignKey("agents.id"))
    poster = relationship("AgentDB", back_populates="tasks_posted")

    claimer_id = Column(String, ForeignKey("agents.id"), nullable=True)
    claimer = relationship("AgentDB", back_populates="tasks_claimed")
    
    submission_content = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True) # Transaction ID (UUID)
    task_id = Column(String, ForeignKey("tasks.id"))
    task = relationship("TaskDB")
    
    from_address = Column(String)
    to_address = Column(String)
    amount = Column(Float)
    fee_amount = Column(Float) # 平台手续费
    fee_recipient_address = Column(String) # 手续费接收地址
    tx_hash = Column(String, nullable=True) # 链上交易哈希
    status = Column(String, default="pending") # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
