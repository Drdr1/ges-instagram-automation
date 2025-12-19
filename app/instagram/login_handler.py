from instagrapi import Client
from instagrapi.exceptions import (
    TwoFactorRequired,
    ChallengeRequired,
    BadPassword,
    LoginRequired
)
from typing import Dict, Optional
from app.instagram.session_manager import SessionManager
import time

class LoginHandler:
    """Handles all Instagram login flows"""
    
    def __init__(self):
        self.session_manager = SessionManager()
    
    def init_client(
        self,
        proxy_url: str,
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Client:
        """Initialize Instagram client with proxy and device settings"""
        cl = Client()
        
        # Set proxy FIRST
        cl.set_proxy(proxy_url)
        
        # Set device settings
        device_settings = self.session_manager.get_device_settings(
            device_id=device_id,
            uuid=uuid,
            phone_id=phone_id
        )
        cl.set_device(device_settings)
        
        # Delay to mimic human behavior
        cl.delay_range = [1, 3]
        
        return cl
    
    def attempt_login(
        self,
        username: str,
        password: str,
        proxy_url: str,
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Dict:
        """
        Attempt initial login
        
        Returns status:
        - success: Login completed
        - 2fa_required: Need 2FA code
        - challenge_required: Need challenge verification
        - error: Login failed
        """
        try:
            # Initialize client
            cl = self.init_client(proxy_url, device_id, uuid, phone_id)
            
            # Try to load existing session
            if self.session_manager.session_exists(username):
                self.session_manager.load_session(cl, username)
                
                # Verify session is still valid
                try:
                    cl.get_timeline_feed()
                    return {
                        "status": "success",
                        "message": "Session restored successfully",
                        "data": {
                            "user_id": cl.user_id,
                            "device_id": cl.device_id,
                            "uuid": cl.uuid,
                            "phone_id": cl.phone_id
                        }
                    }
                except LoginRequired:
                    # Session expired, continue with login
                    pass
            
            # Attempt fresh login
            cl.login(username, password)
            
            # Success! Save session
            self.session_manager.save_session(cl, username)
            
            return {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "user_id": cl.user_id,
                    "device_id": cl.device_id,
                    "uuid": cl.uuid,
                    "phone_id": cl.phone_id
                }
            }
            
        except TwoFactorRequired:
            # Store partial client state
            # We'll need this to continue the 2FA flow
            return {
                "status": "2fa_required",
                "message": "Please enter your 2FA code",
                "data": {
                    "device_id": cl.device_id if 'cl' in locals() else None,
                    "uuid": cl.uuid if 'cl' in locals() else None,
                    "phone_id": cl.phone_id if 'cl' in locals() else None
                }
            }
            
        except ChallengeRequired as e:
            return {
                "status": "challenge_required",
                "message": "Instagram requires verification",
                "data": {
                    "device_id": cl.device_id if 'cl' in locals() else None,
                    "uuid": cl.uuid if 'cl' in locals() else None,
                    "phone_id": cl.phone_id if 'cl' in locals() else None
                }
            }
            
        except BadPassword:
            return {
                "status": "error",
                "message": "Incorrect password"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Login failed: {str(e)}"
            }
    
    def complete_2fa(
        self,
        username: str,
        verification_code: str,
        proxy_url: str,
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Dict:
        """Complete 2FA login"""
        try:
            # Reinitialize client with same settings
            cl = self.init_client(proxy_url, device_id, uuid, phone_id)
            
            # Load partial session if exists
            self.session_manager.load_session(cl, username)
            
            # Complete 2FA
            cl.two_factor_login(verification_code)
            
            # Save complete session
            self.session_manager.save_session(cl, username)
            
            return {
                "status": "success",
                "message": "2FA verification successful",
                "data": {
                    "user_id": cl.user_id,
                    "device_id": cl.device_id,
                    "uuid": cl.uuid,
                    "phone_id": cl.phone_id
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"2FA failed: {str(e)}"
            }
    
    def request_challenge_code(
        self,
        username: str,
        proxy_url: str,
        method: str = "1",  # 0=email, 1=sms
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Dict:
        """Request challenge verification code"""
        try:
            cl = self.init_client(proxy_url, device_id, uuid, phone_id)
            self.session_manager.load_session(cl, username)
            
            # Request code
            cl.challenge_code_handler(username, method)
            
            return {
                "status": "code_sent",
                "message": f"Code sent via {'SMS' if method == '1' else 'email'}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send code: {str(e)}"
            }
    
    def complete_challenge(
        self,
        username: str,
        verification_code: str,
        proxy_url: str,
        device_id: Optional[str] = None,
        uuid: Optional[str] = None,
        phone_id: Optional[str] = None
    ) -> Dict:
        """Complete challenge verification"""
        try:
            cl = self.init_client(proxy_url, device_id, uuid, phone_id)
            self.session_manager.load_session(cl, username)
            
            # Resolve challenge
            cl.challenge_resolve(username, verification_code)
            
            # Save session
            self.session_manager.save_session(cl, username)
            
            return {
                "status": "success",
                "message": "Challenge verification successful",
                "data": {
                    "user_id": cl.user_id,
                    "device_id": cl.device_id,
                    "uuid": cl.uuid,
                    "phone_id": cl.phone_id
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Challenge failed: {str(e)}"
            }
