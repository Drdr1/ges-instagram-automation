from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.utils.encryption import encryption

router = APIRouter(prefix="/api/settings", tags=["settings"])

class BackupCodeRequest(BaseModel):
    user_id: int
    backup_code: str

@router.post("/add-backup-code")
async def add_backup_code(
    req: BackupCodeRequest,
    db: Session = Depends(get_db)
):
    """
    User adds backup code for permanent access
    
    Benefits:
    - Never get logged out
    - Skip 2FA in future
    - More stable sessions
    """
    user = db.query(User).filter(User.id == req.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Encrypt and save backup code
    encrypted_code = encryption.encrypt(req.backup_code)
    user.backup_code_encrypted = encrypted_code
    user.has_backup_code = True
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Backup code added! You'll never be logged out again."
    }

@router.delete("/remove-backup-code/{user_id}")
async def remove_backup_code(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Remove stored backup code"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.backup_code_encrypted = None
    user.has_backup_code = False
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Backup code removed"
    }
