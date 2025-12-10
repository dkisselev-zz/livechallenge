"""Authentication handler for customer sessions."""
import re
from typing import Dict, Optional, Any
from mcp_client import MCPClient


class AuthHandler:
    """Manages customer authentication state per session."""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.auth_state: Dict[str, Dict[str, Any]] = {}
    
    def authenticate(self, session_id: str, email: str, pin: str) -> tuple[bool, str]:
        """Authenticate customer and store session state."""
        try:
            result = self.mcp_client.verify_customer(email, pin)
            
            # Extract customer_id from result
            # The result contains formatted text with customer details
            # Format: "Customer ID: <uuid>"
            customer_id = None
            customer_info_text = ""
            
            if "content" in result and len(result["content"]) > 0:
                customer_info_text = result["content"][0].get("text", "")
            elif "structuredContent" in result:
                customer_info_text = result["structuredContent"].get("result", "")
            
            # Extract customer_id from text - look for "Customer ID: <uuid>" pattern
            # The UUID appears after "Customer ID: " in the response
            uuid_pattern = r'Customer ID:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
            match = re.search(uuid_pattern, customer_info_text, re.IGNORECASE)
            if match:
                customer_id = match.group(1)
            else:
                # Fallback: try to find any UUID in the text
                uuid_pattern_fallback = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                matches = re.findall(uuid_pattern_fallback, customer_info_text, re.IGNORECASE)
                if matches:
                    customer_id = matches[0]
            
            self.auth_state[session_id] = {
                "email": email,
                "authenticated": True,
                "customer_id": customer_id,
                "customer_info": result,
                "customer_info_text": customer_info_text
            }
            return True, "Authentication successful"
        except Exception as e:
            return False, str(e)
    
    def is_authenticated(self, session_id: str) -> bool:
        """Check if session is authenticated."""
        return self.auth_state.get(session_id, {}).get("authenticated", False)
    
    def get_email(self, session_id: str) -> Optional[str]:
        """Get authenticated email for session."""
        return self.auth_state.get(session_id, {}).get("email")
    
    def get_customer_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get customer info for authenticated session."""
        return self.auth_state.get(session_id, {}).get("customer_info")
    
    def get_customer_id(self, session_id: str) -> Optional[str]:
        """Get customer ID for authenticated session."""
        return self.auth_state.get(session_id, {}).get("customer_id")
    
    def clear_auth(self, session_id: str):
        """Clear authentication for session."""
        if session_id in self.auth_state:
            del self.auth_state[session_id]

