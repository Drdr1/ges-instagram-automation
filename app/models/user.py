from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Text
from datetime import datetime
import enum
from app.database import Base

class UserStatus(enum.Enum):
    PENDING = "pending"           # Applied, waiting approval
    APPROVED = "approved"         # Admin approved, proxy purchased  
    ONBOARDING = "onboarding"     # In login process
    ACTIVE = "active"             # Successfully logged in
    SUSPENDED = "suspended"       # Account issues
    BANNED = "banned"             # Instagram banned

class OnboardingStage(enum.Enum):
    PASSWORD = "password"
    TWO_FA = "2fa"
    CHALLENGE = "challenge"
    COMPLETE = "complete"

class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Application data
    email = Column(String(255), unique=True, nullable=False, index=True)
    instagram_username = Column(String(255), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False)
    
    # Proxy information (assigned after approval)
    proxy_url = Column(Text, nullable=True)  # http://user:pass@ip:port
    proxy_provider_id = Column(String(255), nullable=True)
    proxy_city = Column(String(100), nullable=True)
    
    # Instagram session data
    device_id = Column(String(255), nullable=True)
    uuid = Column(String(255), nullable=True)
    phone_id = Column(String(255), nullable=True)
    session_file_path = Column(Text, nullable=True)
    instagram_user_id = Column(String(255), nullable=True)
    
    # Backup code (optional, for permanent access)
    backup_code_encrypted = Column(Text, nullable=True)
    has_backup_code = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    onboarding_stage = Column(Enum(OnboardingStage), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Challenge/Checkpoint tracking
    checkpoint_count = Column(Integer, default=0)
    last_checkpoint_at = Column(DateTime, nullable=True)
    
    # Account health
    is_active = Column(Boolean, default=True)
    ban_reason = Column(Text, nullable=True)

    # ManyChat Integration
    manychat_subscriber_id = Column(String(255), nullable=True, unique=True)
    manychat_connected_at = Column(DateTime, nullable=True)
    chatbot_enabled = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.instagram_username} - {self.status.value}>"

class LoginAttempt(Base):
    """Track all login attempts for debugging"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    attempt_type = Column(String(50))  # password, 2fa, challenge
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
