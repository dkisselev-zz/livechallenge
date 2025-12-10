"""Gradio UI for customer support chatbot."""
import gradio as gr
import re
from typing import Optional
from agent import SupportAgent
from mcp_client import MCPClient
from auth import AuthHandler
from memory import SessionMemory


# Initialize components
mcp_client = MCPClient()
auth_handler = AuthHandler(mcp_client)
memory = SessionMemory()
agent = SupportAgent(mcp_client, auth_handler)


def parse_auth(message: str) -> tuple[Optional[str], Optional[str]]:
    """Parse email and PIN from message."""
    email_pattern = r'email:\s*([^\s,]+)'
    pin_pattern = r'pin:\s*(\d{4})'
    
    email_match = re.search(email_pattern, message, re.IGNORECASE)
    pin_match = re.search(pin_pattern, message, re.IGNORECASE)
    
    email = email_match.group(1) if email_match else None
    pin = pin_match.group(1) if pin_match else None
    
    return email, pin


def chat_response(message, history, session_id):
    """Handle chat message and return response."""
    if not message:
        return history, ""
    
    # Check if message contains authentication
    email, pin = parse_auth(message)
    if email and pin:
        # Attempt authentication
        success, msg = auth_handler.authenticate(session_id, email, pin)
        if success:
            response = "✅ Authentication successful! How can I help you today?"
        else:
            response = f"❌ Authentication failed: {msg}. Please check your email and PIN and try again."
        
        # Gradio 6.x format: list of dicts with role and content
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        memory.add_message(session_id, "user", message)
        memory.add_message(session_id, "assistant", response)
        return history, ""
    
    # Get conversation history
    conv_history = memory.get_conversation_context(session_id)
    
    # Process message with agent
    response = agent.process_message(session_id, message, conv_history)
    
    # Update history - Gradio 6.x format
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    memory.add_message(session_id, "user", message)
    memory.add_message(session_id, "assistant", response)
    
    return history, ""


def create_interface():
    """Create Gradio interface."""
    with gr.Blocks() as demo:
        gr.Markdown("# 🛒 Customer Support Chatbot")
        gr.Markdown("Welcome! I can help you with product inquiries and order management.")
        gr.Markdown("**Note:** For order-related queries, you'll need to authenticate with your email and PIN.")
        
        chatbot = gr.Chatbot(
            label="Chat",
            height=500
        )
        
        msg = gr.Textbox(
            label="Your Message",
            placeholder="Type your message here...",
            lines=2
        )
        
        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear Chat")
        
        gr.Markdown("### Authentication")
        gr.Markdown("To authenticate, include in your message: `email: your@email.com, pin: 1234`")
        
        # Session state
        session_id = gr.State(value="default_session")
        
        # Event handlers
        def submit_message(message, history, session):
            history, _ = chat_response(message, history, session)
            return history, ""
        
        def clear_chat(session):
            memory.clear(session)
            auth_handler.clear_auth(session)
            return []  # Return empty list for Gradio 6.x
        
        submit_btn.click(
            submit_message,
            inputs=[msg, chatbot, session_id],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            submit_message,
            inputs=[msg, chatbot, session_id],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(
            clear_chat,
            inputs=[session_id],
            outputs=[chatbot]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

