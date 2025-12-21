from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound
from typing import Dict, List, Optional
from app.instagram.session_manager import SessionManager
import time

class DMHandler:
    """Handles all Instagram DM operations"""
    
    def __init__(self):
        self.session_manager = SessionManager()
    
    def _get_authenticated_client(self, username: str, proxy_url: str) -> Client:
        """Get authenticated Instagram client for user"""
        cl = Client()
        cl.set_proxy(proxy_url)
        
        # Load session
        session_file = self.session_manager.get_session_path(username)
        if not session_file.exists():
            raise Exception(f"No active session for {username}. Please login first.")
        
        cl.load_settings(session_file)
        
        # Verify session is still valid
        try:
            cl.get_timeline_feed()
        except LoginRequired:
            raise Exception(f"Session expired for {username}. Please re-login.")
        
        return cl
    
    def send_dm(
        self,
        username: str,
        proxy_url: str,
        recipient_username: str,
        message: str
    ) -> Dict:
        """
        Send a DM to a single user
        
        Args:
            username: Instagram username of sender (logged in user)
            proxy_url: User's dedicated proxy
            recipient_username: Instagram username of recipient
            message: Message text to send
            
        Returns:
            {
                "status": "success" | "error",
                "message": str,
                "thread_id": str (if successful)
            }
        """
        try:
            cl = self._get_authenticated_client(username, proxy_url)
            
            # Get recipient user ID
            try:
                recipient = cl.user_info_by_username(recipient_username)
                recipient_id = recipient.pk
            except UserNotFound:
                return {
                    "status": "error",
                    "message": f"User '{recipient_username}' not found"
                }
            
            # Send DM
            thread = cl.direct_send(message, [recipient_id])
            
            return {
                "status": "success",
                "message": "DM sent successfully",
                "thread_id": str(thread.id),
                "recipient_username": recipient_username
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send DM: {str(e)}"
            }
    
    def send_bulk_dms(
        self,
        username: str,
        proxy_url: str,
        recipients: List[str],
        message: str,
        delay_seconds: int = 30
    ) -> Dict:
        """
        Send DMs to multiple users with delay between each
        
        Args:
            username: Instagram username of sender
            proxy_url: User's dedicated proxy
            recipients: List of recipient usernames
            message: Message text to send
            delay_seconds: Delay between DMs (to avoid rate limits)
            
        Returns:
            {
                "status": "success" | "partial" | "error",
                "total": int,
                "sent": int,
                "failed": int,
                "results": [...]
            }
        """
        try:
            cl = self._get_authenticated_client(username, proxy_url)
            
            results = []
            sent_count = 0
            failed_count = 0
            
            for recipient_username in recipients:
                try:
                    # Get recipient user ID
                    recipient = cl.user_info_by_username(recipient_username)
                    recipient_id = recipient.pk
                    
                    # Send DM
                    thread = cl.direct_send(message, [recipient_id])
                    
                    results.append({
                        "recipient": recipient_username,
                        "status": "sent",
                        "thread_id": str(thread.id)
                    })
                    sent_count += 1
                    
                    # Delay to avoid rate limits
                    if recipient_username != recipients[-1]:  # Not last recipient
                        time.sleep(delay_seconds)
                    
                except UserNotFound:
                    results.append({
                        "recipient": recipient_username,
                        "status": "failed",
                        "error": "User not found"
                    })
                    failed_count += 1
                    
                except Exception as e:
                    results.append({
                        "recipient": recipient_username,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_count += 1
            
            overall_status = "success" if failed_count == 0 else (
                "partial" if sent_count > 0 else "error"
            )
            
            return {
                "status": overall_status,
                "total": len(recipients),
                "sent": sent_count,
                "failed": failed_count,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Bulk DM failed: {str(e)}",
                "total": len(recipients),
                "sent": 0,
                "failed": len(recipients)
            }
    
    def get_inbox(
        self,
        username: str,
        proxy_url: str,
        limit: int = 20
    ) -> Dict:
        """
        Get user's DM inbox
        
        Returns:
            {
                "status": "success" | "error",
                "threads": [...]
            }
        """
        try:
            cl = self._get_authenticated_client(username, proxy_url)
            
            threads = cl.direct_threads(amount=limit)
            
            inbox = []
            for thread in threads:
                inbox.append({
                    "thread_id": str(thread.id),
                    "users": [u.username for u in thread.users],
                    "last_activity": str(thread.last_activity_at),
                    "unread": thread.is_unread,
                    "message_count": thread.messages_count
                })
            
            return {
                "status": "success",
                "threads": inbox
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get inbox: {str(e)}"
            }
    
    def get_thread_messages(
        self,
        username: str,
        proxy_url: str,
        thread_id: str,
        limit: int = 50
    ) -> Dict:
        """
        Get messages from a specific thread
        """
        try:
            cl = self._get_authenticated_client(username, proxy_url)
            
            messages = cl.direct_messages(thread_id, amount=limit)
            
            message_list = []
            for msg in messages:
                message_list.append({
                    "message_id": str(msg.id),
                    "user_id": str(msg.user_id),
                    "text": msg.text if hasattr(msg, 'text') else None,
                    "timestamp": str(msg.timestamp)
                })
            
            return {
                "status": "success",
                "messages": message_list
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get thread messages: {str(e)}"
            }
