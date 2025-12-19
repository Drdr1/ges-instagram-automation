from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, UserStatus
from app.utils.proxy_manager import ProxyManager
from app.config import get_settings
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])
settings = get_settings()
proxy_manager = ProxyManager(
    api_key=settings.proxy_provider_api_key,
    api_url=settings.proxy_provider_url
)

class ApprovalRequest(BaseModel):
    use_mock_proxy: bool = False  # For testing

@router.get("/pending-users")
async def get_pending_users(db: Session = Depends(get_db)):
    """Get all users waiting for approval"""
    users = db.query(User).filter(
        User.status == UserStatus.PENDING
    ).order_by(User.created_at.desc()).all()
    
    return {
        "count": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "instagram_username": u.instagram_username,
                "city": u.city,
                "applied_at": u.created_at.isoformat()
            }
            for u in users
        ]
    }

@router.post("/approve/{user_id}")
async def approve_user(
    user_id: int,
    req: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve user and purchase proxy
    
    This is the CRITICAL step that enables user onboarding
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"User status is {user.status.value}, not pending"
        )
    
    # Buy proxy for user's city
    if req.use_mock_proxy:
        # For testing
        proxy_result = await proxy_manager.get_mock_proxy_for_testing(user.city)
    else:
        # Production: buy real proxy
        proxy_result = await proxy_manager.buy_mobile_proxy(user.city)
    
    if not proxy_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to purchase proxy: {proxy_result.get('error')}"
        )
    
    # Update user with proxy info
    user.proxy_url = proxy_result["proxy_url"]
    user.proxy_provider_id = proxy_result["provider_id"]
    user.proxy_city = proxy_result["city"]
    user.status = UserStatus.APPROVED
    user.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # TODO: Send email to user: "Your account is approved! Start onboarding here..."
    
    return {
        "status": "success",
        "message": f"User approved and proxy purchased for {user.city}",
        "data": {
            "user_id": user.id,
            "instagram_username": user.instagram_username,
            "proxy_city": user.proxy_city,
            "approved_at": user.approved_at.isoformat()
        }
    }

@router.get("/users")
async def get_all_users(
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all users, optionally filtered by status"""
    query = db.query(User)
    
    if status:
        try:
            status_enum = UserStatus[status.upper()]
            query = query.filter(User.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid options: {[s.value for s in UserStatus]}"
            )
    
    users = query.order_by(User.created_at.desc()).all()
    
    return {
        "count": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "instagram_username": u.instagram_username,
                "city": u.city,
                "status": u.status.value,
                "onboarding_stage": u.onboarding_stage.value if u.onboarding_stage else None,
                "proxy_city": u.proxy_city,
                "checkpoint_count": u.checkpoint_count,
                "created_at": u.created_at.isoformat(),
                "approved_at": u.approved_at.isoformat() if u.approved_at else None,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None
            }
            for u in users
        ]
    }

@router.get("/user/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "instagram_username": user.instagram_username,
        "city": user.city,
        "status": user.status.value,
        "onboarding_stage": user.onboarding_stage.value if user.onboarding_stage else None,
        "proxy_url": user.proxy_url,  # Be careful exposing this
        "proxy_city": user.proxy_city,
        "device_id": user.device_id,
        "uuid": user.uuid,
        "checkpoint_count": user.checkpoint_count,
        "has_backup_code": user.has_backup_code,
        "created_at": user.created_at.isoformat(),
        "approved_at": user.approved_at.isoformat() if user.approved_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "last_checkpoint_at": user.last_checkpoint_at.isoformat() if user.last_checkpoint_at else None
    }
