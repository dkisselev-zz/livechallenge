"""MCP server client for JSON-RPC communication."""
import requests
import json
from typing import Dict, Any, Optional
from config import MCP_SERVER_URL


class MCPClient:
    """Client for communicating with MCP server via JSON-RPC 2.0."""
    
    def __init__(self):
        self.url = MCP_SERVER_URL
        self.request_id = 0
        self._initialized = False
    
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
    
    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make JSON-RPC call to MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        if params:
            payload["params"] = params
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP Error: {result['error'].get('message', 'Unknown error')}")
            
            return result.get("result", {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to communicate with MCP server: {str(e)}")
    
    def initialize(self):
        """Initialize MCP connection."""
        if self._initialized:
            return
        
        result = self._call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "customer-support-chatbot",
                "version": "1.0.0"
            }
        })
        self._initialized = True
        return result
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        if not self._initialized:
            self.initialize()
        
        result = self._call("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return result
    
    def verify_customer(self, email: str, pin: str) -> Dict[str, Any]:
        """Verify customer with email and PIN."""
        return self.call_tool("verify_customer_pin", {
            "email": email,
            "pin": pin
        })

