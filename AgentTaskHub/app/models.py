from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# --- Agent Models ---
class AgentBase(BaseModel):
    name: str = Field(..., example="MyAwesomeAgent")
    description: Optional[str] = Field(None, example="An AI assistant for automating web tasks.")

class AgentCreate(AgentBase):
    pass

class AgentInDBBase(AgentBase):
    id: str
    api_key: str
    wallet_address: str
    referral_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Agent(AgentInDBBase):
    pass

# --- Task Models ---
class TaskBase(BaseModel):
    title: str = Field(..., example="Summarize this article")
    description: str = Field(..., example="Read the article at URL and provide 5 bullet points summary.")
    amount: float = Field(..., gt=0, example=5.0) # 赏金金额
    deadline_at: Optional[datetime] = Field(None, example="2026-02-03T10:00:00Z")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    deadline_at: Optional[datetime] = None
    status: Optional[str] = None

class TaskInDBBase(TaskBase):
    id: str
    poster_id: str
    status: str
    created_at: datetime
    claimer_id: Optional[str] = None
    submission_content: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    pass

# --- Transaction Models ---
class TransactionBase(BaseModel):
    task_id: str
    from_address: str
    to_address: str
    amount: float
    fee_amount: float
    fee_recipient_address: str

class TransactionCreate(TransactionBase):
    pass

class TransactionInDBBase(TransactionBase):
    id: str
    tx_hash: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class Transaction(TransactionInDBBase):
    pass

# --- API Key Response Model (for secure return) ---
class APIKeyResponse(BaseModel):
    api_key: str
    message: str = "Please save this API key securely. It will not be shown again."

# --- Task Submission Model ---
class TaskSubmission(BaseModel):
    content: str = Field(..., example="Here is the 5 bullet points summary...")

# --- Task Approval/Rejection Model ---
class TaskReview(BaseModel):
    approved: bool
    feedback: Optional[str] = None
