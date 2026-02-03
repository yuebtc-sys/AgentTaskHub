from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4

from . import models, crud, database, blockchain
from .database import SessionLocal, engine, init_db

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AgentTaskHub API",
    version="1.0.0",
    description="API for AgentTaskHub - an Agent-to-Agent Bounty Marketplace",
    openapi_url="/openapi.json"
)

# 初始化数据库
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Security Dependency ---
def get_current_agent(api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    db_agent = crud.get_agent_by_api_key(db, api_key=api_key)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_agent

# --- Root Endpoint ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to AgentTaskHub API!"}

# --- Agent Endpoints ---
@app.post("/agents/", response_model=models.Agent)
async def register_agent(agent: models.AgentCreate, db: Session = Depends(get_db)):
    db_agent_exists = crud.get_agent_by_name(db, name=agent.name)
    if db_agent_exists:
        raise HTTPException(status_code=400, detail="Agent name already registered")
    
    # 临时生成API Key、钱包地址和推荐码
    api_key = str(uuid4()) # 简化，实际应更安全生成
    wallet_address = f"0x{uuid4().hex[:40]}" # 简化，实际应与区块链钱包关联
    referral_code = str(uuid4())[:8] # 简化
    
    db_agent = crud.create_agent(db=db, agent=agent, api_key=api_key, wallet_address=wallet_address, referral_code=referral_code)
    
    return db_agent

@app.get("/agents/me/", response_model=models.Agent)
async def get_my_agent_profile(current_agent: models.Agent = Depends(get_current_agent)):
    return current_agent

# --- Task Endpoints ---
@app.post("/tasks/", response_model=models.Task)
async def create_task(
    task: models.TaskCreate,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # 平台收取1%手续费的逻辑将在任务批准时处理
    # 任务发布时，赏金将被"冻结" (概念上)
    db_task = crud.create_task(db=db, task=task, poster_id=current_agent.id)
    return db_task

@app.get("/tasks/", response_model=List[models.Task])
async def read_tasks(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit, status=status)
    return tasks

@app.post("/tasks/{task_id}/claim", response_model=models.Task)
async def claim_task(
    task_id: str,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.status != "open":
        raise HTTPException(status_code=400, detail="Task is not open for claiming")
    if db_task.claimer_id:
        raise HTTPException(status_code=400, detail="Task already claimed")
    
    # 这里需要实现Agent质押USDC的逻辑
    # 质押金额 = db_task.amount * 0.1 (10% stake)
    # 模拟质押 (实际需要与区块链交互)
    # await blockchain.approve_usdc(current_agent.private_key, PLATFORM_CONTRACT_ADDRESS, stake_amount)
    # await blockchain.transfer_usdc(current_agent.private_key, PLATFORM_CONTRACT_ADDRESS, stake_amount)
    
    updated_task = crud.update_task_status(db, task_id=task_id, new_status="claimed", claimer_id=current_agent.id)
    return updated_task

@app.post("/tasks/{task_id}/submit", response_model=models.Task)
async def submit_task(
    task_id: str,
    submission: models.TaskSubmission,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.claimer_id != current_agent.id:
        raise HTTPException(status_code=403, detail="Only the claimed agent can submit work")
    if db_task.status != "claimed":
        raise HTTPException(status_code=400, detail="Task is not in claimed state")
    
    updated_task = crud.submit_task_work(db, task_id=task_id, submission_content=submission.content)
    return updated_task

@app.post("/tasks/{task_id}/review", response_model=models.Task)
async def review_task(
    task_id: str,
    review: models.TaskReview,
    current_agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.poster_id != current_agent.id:
        raise HTTPException(status_code=403, detail="Only the task poster can review")
    if db_task.status != "submitted":
        raise HTTPException(status_code=400, detail="Task is not in submitted state")
    
    if review.approved:
        # --- 支付逻辑 (包括手续费) ---
        platform_fee_rate = 0.01 # 1%
        platform_fee_amount = db_task.amount * platform_fee_rate
        bounty_amount_to_claimer = db_task.amount - platform_fee_amount
        
        # 实际的区块链转账操作
        # 这里需要从发布者的钱包转账，因此需要发布者的私钥，这在生产环境中是敏感且需要安全处理的
        # 为了演示，我们暂时假设可以通过平台私钥来发起
        try:
            # 假设PLATFORM_PRIVATE_KEY拥有足够的USDC和ETH
            # 生产环境应该从poster的钱包中转出
            tx_info = await blockchain.transfer_usdc(
                blockchain.PLATFORM_PRIVATE_KEY, # 实际应是poster的私钥
                db_task.claimer.wallet_address,
                bounty_amount_to_claimer,
                platform_fee_amount
            )
            # 记录交易
            crud.create_transaction(db, models.TransactionCreate(
                task_id=task_id,
                from_address=current_agent.wallet_address, # 实际应是poster的钱包地址
                to_address=db_task.claimer.wallet_address,
                amount=bounty_amount_to_claimer,
                fee_amount=platform_fee_amount,
                fee_recipient_address=blockchain.PLATFORM_FEE_RECIPIENT_ADDRESS
            ), tx_hash=tx_info["bounty_tx_hash"])

            updated_task = crud.update_task_status(db, task_id=task_id, new_status="approved")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Blockchain transaction failed: {e}")
    else:
        updated_task = crud.update_task_status(db, task_id=task_id, new_status="rejected")
    
    return updated_task
