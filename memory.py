"""Session-based conversation memory manager."""
from typing import List, Dict, Any


class SessionMemory:
    """Manages conversation memory per session."""
    
    def __init__(self):
        self.memories: Dict[str, List[Dict[str, str]]] = {}
    
    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        return self.memories.get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session memory."""
        if session_id not in self.memories:
            self.memories[session_id] = []
        
        self.memories[session_id].append({
            "role": role,
            "content": content
        })
    
    def clear(self, session_id: str):
        """Clear memory for a session."""
        if session_id in self.memories:
            del self.memories[session_id]
    
    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context."""
        messages = self.get_messages(session_id)
        return messages[-max_messages:] if len(messages) > max_messages else messages

