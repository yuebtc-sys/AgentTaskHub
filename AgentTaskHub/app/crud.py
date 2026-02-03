from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from uuid import uuid4

from . import models, database

# --- Agent CRUD ---
def get_agent(db: Session, agent_id: str):
    return db.query(database.AgentDB).filter(database.AgentDB.id == agent_id).first()

def get_agent_by_name(db: Session, name: str):
    return db.query(database.AgentDB).filter(database.AgentDB.name == name).first()

def get_agent_by_api_key(db: Session, api_key: str):
    return db.query(database.AgentDB).filter(database.AgentDB.api_key == api_key).first()

def create_agent(db: Session, agent: models.AgentCreate, api_key: str, wallet_address: str, referral_code: str):
    db_agent = database.AgentDB(
        id=str(uuid4()), # 生成唯一Agent ID
        name=agent.name,
        api_key=api_key,
        wallet_address=wallet_address,
        referral_code=referral_code,
        created_at=datetime.utcnow()
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

# --- Task CRUD ---
def get_task(db: Session, task_id: str):
    return db.query(database.TaskDB).filter(database.TaskDB.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(database.TaskDB)
    if status:
        query = query.filter(database.TaskDB.status == status)
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task: models.TaskCreate, poster_id: str):
    db_task = database.TaskDB(
        id=str(uuid4()),
        title=task.title,
        description=task.description,
        amount=task.amount,
        status="open",
        created_at=datetime.utcnow(),
        deadline_at=task.deadline_at,
        poster_id=poster_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: str, new_status: str, claimer_id: Optional[str] = None):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = new_status
        if new_status == "claimed" and claimer_id:
            db_task.claimer_id = claimer_id
        elif new_status == "submitted":
            db_task.submission_content = None # 假设提交内容会单独处理或在这里更新
        elif new_status == "approved":
            db_task.approved_at = datetime.utcnow()
        elif new_status == "rejected":
            db_task.rejected_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    return db_task

def submit_task_work(db: Session, task_id: str, submission_content: str):
    db_task = get_task(db, task_id)
    if db_task and db_task.status == "claimed": # 只有被认领的任务才能提交工作
        db_task.submission_content = submission_content
        db_task.status = "submitted"
        db.commit()
        db.refresh(db_task)
    return db_task

# --- Transaction CRUD (Simplified for initial version) ---
def create_transaction(db: Session, transaction: models.TransactionCreate, tx_hash: Optional[str] = None):
    db_transaction = database.TransactionDB(
        id=str(uuid4()),
        task_id=transaction.task_id,
        from_address=transaction.from_address,
        to_address=transaction.to_address,
        amount=transaction.amount,
        fee_amount=transaction.fee_amount,
        fee_recipient_address=transaction.fee_recipient_address,
        tx_hash=tx_hash,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction_status(db: Session, transaction_id: str, new_status: str, tx_hash: Optional[str] = None):
    db_transaction = db.query(database.TransactionDB).filter(database.TransactionDB.id == transaction_id).first()
    if db_transaction:
        db_transaction.status = new_status
        if tx_hash:
            db_transaction.tx_hash = tx_hash
        db.commit()
        db.refresh(db_transaction)
    return db_transaction
