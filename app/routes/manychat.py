from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, UserStatus
from app.integrations.manychat_handler import ManyChatHandler
from app.config import get_settings
from datetime import datetime
import hmac
import hashlib

router = APIRouter(prefix="/api/manychat", tags=["manychat"])
settings = get_settings()
manychat = ManyChatHandler(api_key=settings.manychat_api_key)

class ConnectManyChatRequest(BaseModel):
    user_id: int

class SendMessageRequest(BaseModel):
    user_id: int
    message: str

@router.post("/connect")
async def connect_manychat(req: ConnectManyChatRequest, db: Session = Depends(get_db)):
    """
    Connect user to ManyChat
    
    Called after successful Instagram login
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="User must complete Instagram login first"
        )
    
    # Create subscriber in ManyChat
    result = manychat.create_subscriber(
        instagram_user_id=user.instagram_user_id,
        instagram_username=user.instagram_username,
        email=user.email
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Save ManyChat subscriber ID
    user.manychat_subscriber_id = result["data"]["data"]["id"]
    user.manychat_connected_at = datetime.utcnow()
    user.chatbot_enabled = True
    
    # Add tags for segmentation
    manychat.add_tag(user.manychat_subscriber_id, user.city)
    manychat.add_tag(user.manychat_subscriber_id, "nightlife")
    
    db.commit()
    
    return {
        "status": "success",
        "message": "ManyChat connected successfully",
        "subscriber_id": user.manychat_subscriber_id
    }

@router.post("/webhook")
async def manychat_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for receiving messages from ManyChat
    
    ManyChat will POST here when users send messages
    
    Setup in ManyChat:
    Settings → API → Webhooks → Add webhook URL:
    https://your-domain.com/api/manychat/webhook
    """
    # Verify webhook signature (security)
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()
    
    # Verify signature
    expected_signature = "sha256=" + hmac.new(
        settings.manychat_webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected_signature:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse webhook data
    data = await request.json()
    
    event_type = data.get("type")
    
    if event_type == "message":
        # New message received
        subscriber_id = data["data"]["subscriber"]["id"]
        message_text = data["data"]["message"]["text"]
        
        # Find user by subscriber ID
        user = db.query(User).filter(
            User.manychat_subscriber_id == subscriber_id
        ).first()
        
        if user:
            # TODO: Process message with your AI
            # TODO: Store in your custom inbox
            # TODO: Send to your Java backend
            
            # For now, log it
            print(f"Message from {user.instagram_username}: {message_text}")
            
            # You can forward to your Java backend here
            # requests.post("http://your-java-backend:8080/inbox/message", json={
            #     "user_id": user.id,
            #     "message": message_text,
            #     "timestamp": data["data"]["timestamp"]
            # })
    
    return {"status": "received"}

@router.post("/send-message")
async def send_message_via_manychat(
    req: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to user via ManyChat
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.manychat_subscriber_id:
        raise HTTPException(
            status_code=400,
            detail="User not connected to ManyChat"
        )
    
    result = manychat.send_message(
        subscriber_id=user.manychat_subscriber_id,
        message=req.message
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result
