"""LLM agent with tool calling capabilities."""
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from mcp_client import MCPClient
from auth import AuthHandler


class SupportAgent:
    """Customer support agent with MCP tool integration."""
    
    def __init__(self, mcp_client: MCPClient, auth_handler: AuthHandler):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.mcp_client = mcp_client
        self.auth_handler = auth_handler
        
        # Initialize MCP connection
        self.mcp_client.initialize()
        
        # Define available tools
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define tool schemas for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_products",
                    "description": "List products with optional filters by category or active status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category (e.g., 'Computers', 'Monitors', 'Printers')"
                            },
                            "is_active": {
                                "type": "boolean",
                                "description": "Filter by active status"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product",
                    "description": "Get detailed product information by SKU",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sku": {
                                "type": "string",
                                "description": "Product SKU (e.g., 'COM-0001', 'MON-0054')"
                            }
                        },
                        "required": ["sku"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search products by name or description keyword",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search term (case-insensitive, partial match)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer",
                    "description": "Get customer information by customer ID. Requires authentication.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Customer UUID"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_orders",
                    "description": "List orders with optional filters. Requires authentication.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Filter by customer UUID"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by status: draft, submitted, approved, fulfilled, cancelled"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order",
                    "description": "Get detailed order information including items. Requires authentication.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Order UUID"
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_order",
                    "description": "Create a new order with items. Requires authentication.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Customer UUID"
                            },
                            "items": {
                                "type": "array",
                                "description": "List of order items",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "sku": {"type": "string"},
                                        "quantity": {"type": "integer"},
                                        "unit_price": {"type": "string"},
                                        "currency": {"type": "string", "default": "USD"}
                                    },
                                    "required": ["sku", "quantity", "unit_price"]
                                }
                            }
                        },
                        "required": ["customer_id", "items"]
                    }
                }
            }
        ]
    
    def _requires_auth(self, tool_name: str) -> bool:
        """Check if tool requires authentication."""
        auth_required_tools = ["get_customer", "list_orders", "get_order", "create_order"]
        return tool_name in auth_required_tools
    
    def _get_customer_id(self, session_id: str) -> Optional[str]:
        """Get customer_id from authenticated session."""
        if not self.auth_handler.is_authenticated(session_id):
            return None
        return self.auth_handler.get_customer_id(session_id)
    
    def process_message(self, session_id: str, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """Process user message and return response."""
        # Check if message is about authentication
        if "email" in user_message.lower() and "pin" in user_message.lower():
            # Try to extract email and PIN from message
            # This is a simple approach - in production, use structured input
            return "To authenticate, please provide your email and PIN in the format: 'email: your@email.com, pin: 1234'"
        
        # Build system message with authentication status
        is_authenticated = self.auth_handler.is_authenticated(session_id)
        auth_status = "authenticated" if is_authenticated else "not authenticated"
        customer_email = self.auth_handler.get_email(session_id) if is_authenticated else None
        
        system_content = """You are a helpful customer support agent for a computer products company.
You can help customers with:
- Product inquiries (browsing, searching, getting details) - no authentication needed
- Order management (viewing orders, order status, placing orders) - requires authentication

Current session status: """ + auth_status
        if customer_email:
            system_content += f"\nAuthenticated customer: {customer_email}"
        system_content += """

When a customer asks about orders and is not authenticated, ask them to provide their email and PIN.
If the customer is already authenticated, you can directly help with their orders.
Be friendly, professional, and helpful. Provide clear, concise answers."""
        
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Check if query might need authentication
        order_keywords = ["order", "purchase", "buy", "my orders", "order history", "track order", "place order"]
        needs_auth = any(keyword in user_message.lower() for keyword in order_keywords)
        
        if needs_auth and not self.auth_handler.is_authenticated(session_id):
            return "To access your orders, I need to verify your identity. Please provide your email and PIN in this format: 'email: your@email.com, pin: 1234'"
        
        try:
            # Call OpenAI with tool calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Handle tool calls
            if message.tool_calls:
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Check authentication for order-related tools
                    if self._requires_auth(tool_name) and not self.auth_handler.is_authenticated(session_id):
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": "Authentication required. Please provide your email and PIN."
                        })
                        continue
                    
                    # Inject customer_id for order-related tools if not provided
                    if self._requires_auth(tool_name):
                        customer_id = self._get_customer_id(session_id)
                        if customer_id:
                            # Add customer_id to tool args if not present and tool needs it
                            if tool_name in ["list_orders", "get_customer", "create_order"]:
                                if "customer_id" not in tool_args or not tool_args.get("customer_id"):
                                    tool_args["customer_id"] = customer_id
                        elif tool_name == "list_orders":
                            # For list_orders, if no customer_id, we can still call it without filter
                            # The MCP server will handle it
                            pass
                    
                    # Call MCP tool
                    try:
                        result = self.mcp_client.call_tool(tool_name, tool_args)
                        
                        # Extract text content from result
                        if "content" in result and len(result["content"]) > 0:
                            content = result["content"][0].get("text", str(result))
                        elif "structuredContent" in result:
                            content = result["structuredContent"].get("result", str(result))
                        else:
                            content = str(result)
                        
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": content
                        })
                    except Exception as e:
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": f"Error: {str(e)}"
                        })
                
                # Get final response with tool results
                messages.append(message)
                messages.extend(tool_results)
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                return final_response.choices[0].message.content
            else:
                return message.content
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."

