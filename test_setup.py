#!/usr/bin/env python3
"""Quick test to verify setup is working."""
import sys

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import config
        print("✅ Config module imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from mcp_client import MCPClient
        print("✅ MCP Client imported")
    except Exception as e:
        print(f"❌ MCP Client import failed: {e}")
        return False
    
    try:
        from auth import AuthHandler
        print("✅ Auth Handler imported")
    except Exception as e:
        print(f"❌ Auth Handler import failed: {e}")
        return False
    
    try:
        from memory import SessionMemory
        print("✅ Memory module imported")
    except Exception as e:
        print(f"❌ Memory import failed: {e}")
        return False
    
    try:
        from agent import SupportAgent
        print("✅ Support Agent imported")
    except Exception as e:
        print(f"❌ Support Agent import failed: {e}")
        return False
    
    try:
        import gradio as gr
        print("✅ Gradio imported")
    except Exception as e:
        print(f"❌ Gradio import failed: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ OpenAI imported")
    except Exception as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    return True

def test_mcp_connection():
    """Test MCP server connection."""
    try:
        from mcp_client import MCPClient
        client = MCPClient()
        result = client.initialize()
        print("✅ MCP server connection successful")
        print(f"   Server: {result.get('serverInfo', {}).get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ MCP server connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing setup...")
    print("-" * 50)
    
    imports_ok = test_imports()
    print("-" * 50)
    
    if imports_ok:
        mcp_ok = test_mcp_connection()
        print("-" * 50)
        
        if mcp_ok:
            print("✅ All tests passed! Setup is ready.")
            sys.exit(0)
        else:
            print("⚠️  Imports OK but MCP connection failed. Check your .env file.")
            sys.exit(1)
    else:
        print("❌ Import tests failed. Check your dependencies.")
        sys.exit(1)

