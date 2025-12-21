import requests
from typing import Dict, Optional

class ManyChatHandler:
    """
    Handles ManyChat API integration
    
    Docs: https://api.manychat.com/docs
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.manychat.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_subscriber(
        self,
        instagram_user_id: str,
        instagram_username: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict:
        """
        Create a subscriber in ManyChat
        
        This links the Instagram user to your ManyChat account
        """
        url = f"{self.base_url}/fb/subscriber/createSubscriber"
        
        payload = {
            "psid": instagram_user_id,  # Instagram User ID
            "whitelisted": True,
            "subscribed": True,
            "first_name": first_name or instagram_username,
            "last_name": last_name or "",
            "email": email,
            "has_opt_in_sms": False,
            "has_opt_in_email": bool(email),
            "consent_phrase": "GES Instagram Automation",
            "custom_fields": [
                {
                    "id": 12345,  # Your custom field ID
                    "value": instagram_username
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json()
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to create subscriber: {str(e)}"
            }
    
    def send_message(
        self,
        subscriber_id: str,
        message: str,
        tag: str = "ACCOUNT_UPDATE"
    ) -> Dict:
        """
        Send a message to a subscriber via ManyChat
        
        Tags: ACCOUNT_UPDATE, CONFIRMED_EVENT_UPDATE, POST_PURCHASE_UPDATE, etc.
        """
        url = f"{self.base_url}/fb/sending/sendContent"
        
        payload = {
            "subscriber_id": subscriber_id,
            "data": {
                "version": "v2",
                "content": {
                    "messages": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            },
            "message_tag": tag
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json()
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to send message: {str(e)}"
            }
    
    def get_subscriber_info(self, subscriber_id: str) -> Dict:
        """
        Get subscriber information
        """
        url = f"{self.base_url}/fb/subscriber/getInfo"
        
        params = {"subscriber_id": subscriber_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json()
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to get subscriber: {str(e)}"
            }
    
    def add_tag(self, subscriber_id: str, tag_name: str) -> Dict:
        """
        Add a tag to subscriber (for segmentation)
        """
        url = f"{self.base_url}/fb/subscriber/addTag"
        
        payload = {
            "subscriber_id": subscriber_id,
            "tag_name": tag_name
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success"
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to add tag: {str(e)}"
            }
    
    def set_custom_field(
        self,
        subscriber_id: str,
        field_id: int,
        value: str
    ) -> Dict:
        """
        Set a custom field for subscriber
        
        Useful for storing:
        - Nightclub name
        - City
        - VIP status
        - etc.
        """
        url = f"{self.base_url}/fb/subscriber/setCustomField"
        
        payload = {
            "subscriber_id": subscriber_id,
            "field_id": field_id,
            "field_value": value
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success"
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"Failed to set custom field: {str(e)}"
            }
