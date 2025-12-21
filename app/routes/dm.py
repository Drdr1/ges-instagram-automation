from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models import User, UserStatus
from app.instagram.dm_handler import DMHandler

router = APIRouter(prefix="/api/dm", tags=["dm"])
dm_handler = DMHandler()

class SendDMRequest(BaseModel):
    user_id: int
    recipient_username: str
    message: str

class BulkDMRequest(BaseModel):
    user_id: int
    recipients: List[str]
    message: str
    delay_seconds: int = 30  # Delay between DMs

class GetInboxRequest(BaseModel):
    user_id: int
    limit: int = 20

class GetThreadRequest(BaseModel):
    user_id: int
    thread_id: str
    limit: int = 50

@router.post("/send")
async def send_dm(req: SendDMRequest, db: Session = Depends(get_db)):
    """
    Send a DM to a single user
    
    Example:
    POST /api/dm/send
    {
        "user_id": 1,
        "recipient_username": "target_user",
        "message": "Hey! Check out our club tonight! "
    }
    """
    # Get user
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="User must complete onboarding first"
        )
    
    # Send DM
    result = dm_handler.send_dm(
        username=user.instagram_username,
        proxy_url=user.proxy_url,
        recipient_username=req.recipient_username,
        message=req.message
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/send-bulk")
async def send_bulk_dms(req: BulkDMRequest, db: Session = Depends(get_db)):
    """
    Send DMs to multiple users
    
    Example:
    POST /api/dm/send-bulk
    {
        "user_id": 1,
        "recipients": ["user1", "user2", "user3"],
        "message": " Tonight at Club XYZ! Free entry before 11pm!",
        "delay_seconds": 30
    }
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="User must complete onboarding first"
        )
    
    # Send bulk DMs
    result = dm_handler.send_bulk_dms(
        username=user.instagram_username,
        proxy_url=user.proxy_url,
        recipients=req.recipients,
        message=req.message,
        delay_seconds=req.delay_seconds
    )
    
    return result

@router.post("/inbox")
async def get_inbox(req: GetInboxRequest, db: Session = Depends(get_db)):
    """
    Get user's DM inbox
    
    Example:
    POST /api/dm/inbox
    {
        "user_id": 1,
        "limit": 20
    }
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="User must complete onboarding first"
        )
    
    result = dm_handler.get_inbox(
        username=user.instagram_username,
        proxy_url=user.proxy_url,
        limit=req.limit
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/thread")
async def get_thread_messages(req: GetThreadRequest, db: Session = Depends(get_db)):
    """
    Get messages from a specific thread
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="User must complete onboarding first"
        )
    
    result = dm_handler.get_thread_messages(
        username=user.instagram_username,
        proxy_url=user.proxy_url,
        thread_id=req.thread_id,
        limit=req.limit
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result
