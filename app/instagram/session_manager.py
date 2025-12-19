from pathlib import Path
from typing import Dict, Optional
from instagrapi import Client
import json

class SessionManager:
    """Manages Instagram session persistence"""
    
    def __init__(self, session_dir: str = "./sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
    
    def get_session_path(self, username: str) -> Path:
        """Get session file path for user"""
        return self.session_dir / f"{username}.json"
    
    def session_exists(self, username: str) -> bool:
        """Check if session file exists"""
        return self.get_session_path(username).exists()
    
    def load_session(self, client: Client, username: str) -> bool:
        """Load existing session into client"""
        session_file = self.get_session_path(username)
        if session_file.exists():
            try:
                client.load_settings(session_file)
                return True
            except Exception as e:
                print(f"Failed to load session: {e}")
                return False
        return False
    
    def save_session(self, client: Client, username: str) -> bool:
        """Save client session to file"""
        session_file = self.get_session_path(username)
        try:
            client.dump_settings(session_file)
            return True
        except Exception as e:
            print(f"Failed to save session: {e}")
            return False
    
    def delete_session(self, username: str) -> bool:
        """Delete session file"""
        session_file = self.get_session_path(username)
        if session_file.exists():
            try:
                session_file.unlink()
                return True
            except Exception as e:
                print(f"Failed to delete session: {e}")
                return False
        return False
    
    def get_device_settings(
        self, 
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Dict:
        """
        Get consistent device settings
        
        CRITICAL: These must stay consistent per user to avoid checkpoints
        """
        settings = {
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "OnePlus6T",
            "model": "ONEPLUS A6003",
            "cpu": "qcom"
        }
        
        # Use existing IDs if provided (for returning users)
        if device_id:
            settings["device_id"] = device_id
        if uuid:
            settings["uuid"] = uuid
        if phone_id:
            settings["phone_id"] = phone_id
        
        return settings
