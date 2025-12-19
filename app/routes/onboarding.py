from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User, UserStatus, OnboardingStage, LoginAttempt
from app.instagram.login_handler import LoginHandler
from datetime import datetime

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
login_handler = LoginHandler()

# Pydantic schemas
class ApplicationRequest(BaseModel):
    email: EmailStr
    instagram_username: str
    city: str

class LoginRequest(BaseModel):
    user_id: int
    password: str

class TwoFactorRequest(BaseModel):
    user_id: int
    code: str

class ChallengeRequest(BaseModel):
    user_id: int
    code: str
    method: str = "1"  # 1=SMS, 0=email

# Routes
@router.post("/apply")
async def apply_for_account(
    req: ApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Step 1: User applies with email + Instagram username + city
    
    This creates a PENDING user awaiting admin approval
    """
    # Check if username already exists
    existing = db.query(User).filter(
        User.instagram_username == req.instagram_username
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This Instagram account is already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == req.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered"
        )
    
    # Create pending user
    user = User(
        email=req.email,
        instagram_username=req.instagram_username,
        city=req.city,
        status=UserStatus.PENDING
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # TODO: Send email notification to admin
    # TODO: Send confirmation email to user
    
    return {
        "status": "success",
        "message": "Application submitted successfully! We'll review and approve within 24 hours.",
        "user_id": user.id,
        "data": {
            "email": user.email,
            "instagram_username": user.instagram_username,
            "city": user.city
        }
    }

@router.get("/status/{user_id}")
async def check_application_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Check if user has been approved and can start onboarding"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": user.status.value,
        "instagram_username": user.instagram_username,
        "city": user.city,
        "can_login": user.status == UserStatus.APPROVED,
        "approved_at": user.approved_at.isoformat() if user.approved_at else None
    }

@router.post("/login")
async def start_login(
    req: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Step 2: User enters password to start login
    
    This initiates the login flow with their dedicated proxy
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Account not approved yet. Please wait for admin approval."
        )
    
    if not user.proxy_url:
        raise HTTPException(
            status_code=500,
            detail="Proxy not configured. Please contact support."
        )
    
    # Update status
    user.status = UserStatus.ONBOARDING
    user.onboarding_stage = OnboardingStage.PASSWORD
    db.commit()
    
    # Log attempt
    attempt = LoginAttempt(
        user_id=user.id,
        attempt_type="password",
        success=False
    )
    db.add(attempt)
    db.commit()
    
    # Attempt login
    result = login_handler.attempt_login(
        username=user.instagram_username,
        password=req.password,
        proxy_url=user.proxy_url,
        device_id=user.device_id,
        uuid=user.uuid,
        phone_id=user.phone_id
    )
    
    # Update based on result
    if result["status"] == "success":
        # Login succeeded without 2FA!
        user.status = UserStatus.ACTIVE
        user.onboarding_stage = OnboardingStage.COMPLETE
        user.last_login_at = datetime.utcnow()
        
        # Save device IDs
        if "data" in result:
            user.device_id = result["data"].get("device_id")
            user.uuid = result["data"].get("uuid")
            user.phone_id = result["data"].get("phone_id")
            user.instagram_user_id = result["data"].get("user_id")
        
        attempt.success = True
        db.commit()
        
        return {
            "status": "success",
            "message": "Login successful! Your account is now active.",
            "next_step": "complete"
        }
    
    elif result["status"] == "2fa_required":
        # Need 2FA code
        user.onboarding_stage = OnboardingStage.TWO_FA
        
        # Save device IDs if provided
        if "data" in result:
            if result["data"].get("device_id"):
                user.device_id = result["data"]["device_id"]
            if result["data"].get("uuid"):
                user.uuid = result["data"]["uuid"]
            if result["data"].get("phone_id"):
                user.phone_id = result["data"]["phone_id"]
        
        db.commit()
        
        return {
            "status": "2fa_required",
            "message": "Please enter your 6-digit authentication code",
            "next_step": "submit_2fa"
        }
    
    elif result["status"] == "challenge_required":
        # Need challenge verification
        user.onboarding_stage = OnboardingStage.CHALLENGE
        user.checkpoint_count += 1
        user.last_checkpoint_at = datetime.utcnow()
        
        # Save device IDs if provided
        if "data" in result:
            if result["data"].get("device_id"):
                user.device_id = result["data"]["device_id"]
            if result["data"].get("uuid"):
                user.uuid = result["data"]["uuid"]
            if result["data"].get("phone_id"):
                user.phone_id = result["data"]["phone_id"]
        
        db.commit()
        
        # Auto-request SMS code
        code_result = login_handler.request_challenge_code(
            username=user.instagram_username,
            proxy_url=user.proxy_url,
            method="1",  # SMS
            device_id=user.device_id,
            uuid=user.uuid,
            phone_id=user.phone_id
        )
        
        return {
            "status": "challenge_required",
            "message": "Instagram needs to verify it's you. We've sent a code to your phone.",
            "next_step": "submit_challenge",
            "checkpoint_count": user.checkpoint_count
        }
    
    else:
        # Error
        attempt.error_message = result.get("message")
        db.commit()
        
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Login failed")
        )

@router.post("/submit-2fa")
async def submit_2fa_code(
    req: TwoFactorRequest,
    db: Session = Depends(get_db)
):
    """
    Step 3: User submits 2FA code
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.onboarding_stage != OnboardingStage.TWO_FA:
        raise HTTPException(
            status_code=400,
            detail="Invalid onboarding stage"
        )
    
    # Log attempt
    attempt = LoginAttempt(
        user_id=user.id,
        attempt_type="2fa",
        success=False
    )
    db.add(attempt)
    db.commit()
    
    # Complete 2FA
    result = login_handler.complete_2fa(
        username=user.instagram_username,
        verification_code=req.code,
        proxy_url=user.proxy_url,
        device_id=user.device_id,
        uuid=user.uuid,
        phone_id=user.phone_id
    )
    
    if result["status"] == "success":
        # Success!
        user.status = UserStatus.ACTIVE
        user.onboarding_stage = OnboardingStage.COMPLETE
        user.last_login_at = datetime.utcnow()
        
        # Save device IDs
        if "data" in result:
            user.device_id = result["data"].get("device_id")
            user.uuid = result["data"].get("uuid")
            user.phone_id = result["data"].get("phone_id")
            user.instagram_user_id = result["data"].get("user_id")
        
        attempt.success = True
        db.commit()
        
        return {
            "status": "success",
            "message": "Login successful! Your account is now active.",
            "next_step": "complete"
        }
    else:
        # Failed
        attempt.error_message = result.get("message")
        db.commit()
        
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "2FA verification failed")
        )

@router.post("/submit-challenge")
async def submit_challenge_code(
    req: ChallengeRequest,
    db: Session = Depends(get_db)
):
    """
    Step 4: User submits challenge verification code
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.onboarding_stage != OnboardingStage.CHALLENGE:
        raise HTTPException(
            status_code=400,
            detail="Invalid onboarding stage"
        )
    
    # Check checkpoint loop
    if user.checkpoint_count > 3:
        raise HTTPException(
            status_code=429,
            detail="Too many verification attempts. Please contact support for a new proxy."
        )
    
    # Log attempt
    attempt = LoginAttempt(
        user_id=user.id,
        attempt_type="challenge",
        success=False
    )
    db.add(attempt)
    db.commit()
    
    # Complete challenge
    result = login_handler.complete_challenge(
        username=user.instagram_username,
        verification_code=req.code,
        proxy_url=user.proxy_url,
        device_id=user.device_id,
        uuid=user.uuid,
        phone_id=user.phone_id
    )
    
    if result["status"] == "success":
        # Success!
        user.status = UserStatus.ACTIVE
        user.onboarding_stage = OnboardingStage.COMPLETE
        user.last_login_at = datetime.utcnow()
        user.checkpoint_count = 0  # Reset on success
        
        # Save device IDs
        if "data" in result:
            user.device_id = result["data"].get("device_id")
            user.uuid = result["data"].get("uuid")
            user.phone_id = result["data"].get("phone_id")
            user.instagram_user_id = result["data"].get("user_id")
        
        attempt.success = True
        db.commit()
        
        return {
            "status": "success",
            "message": "Verification successful! Your account is now active.",
            "next_step": "complete"
        }
    else:
        # Failed
        user.checkpoint_count += 1
        user.last_checkpoint_at = datetime.utcnow()
        attempt.error_message = result.get("message")
        db.commit()
        
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Challenge verification failed")
        )
