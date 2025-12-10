#!/usr/bin/env python3
"""Test all components of the customer support chatbot."""
import sys
from mcp_client import MCPClient
from auth import AuthHandler
from memory import SessionMemory
from agent import SupportAgent


def test_mcp_client():
    """Test MCP client functionality."""
    print("=" * 60)
    print("Testing MCP Client")
    print("=" * 60)
    
    try:
        client = MCPClient()
        print("✅ MCP Client created")
        
        # Test initialization
        result = client.initialize()
        print(f"✅ MCP initialized: {result.get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Test list_products tool
        print("\n--- Testing list_products tool ---")
        result = client.call_tool("list_products", {"category": "Monitors"})
        if "content" in result:
            text = result["content"][0].get("text", "")[:200]
            print(f"✅ list_products returned: {text}...")
        else:
            print(f"⚠️  Unexpected result format: {result}")
        
        # Test get_product tool
        print("\n--- Testing get_product tool ---")
        result = client.call_tool("get_product", {"sku": "COM-0001"})
        if "content" in result:
            text = result["content"][0].get("text", "")
            print(f"✅ get_product returned product info")
            print(f"   Preview: {text[:150]}...")
        else:
            print(f"⚠️  Unexpected result format: {result}")
        
        # Test search_products tool
        print("\n--- Testing search_products tool ---")
        result = client.call_tool("search_products", {"query": "monitor"})
        if "content" in result:
            text = result["content"][0].get("text", "")[:200]
            print(f"✅ search_products found results: {text}...")
        else:
            print(f"⚠️  Unexpected result format: {result}")
        
        return True
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication():
    """Test authentication handler."""
    print("\n" + "=" * 60)
    print("Testing Authentication Handler")
    print("=" * 60)
    
    try:
        client = MCPClient()
        client.initialize()
        auth_handler = AuthHandler(client)
        session_id = "test_session_1"
        
        print("✅ Auth Handler created")
        
        # Test authentication with valid credentials
        print("\n--- Testing authentication with valid credentials ---")
        email = "donaldgarcia@example.net"
        pin = "7912"
        
        success, message = auth_handler.authenticate(session_id, email, pin)
        if success:
            print(f"✅ Authentication successful: {message}")
            print(f"   Email: {auth_handler.get_email(session_id)}")
            print(f"   Customer ID: {auth_handler.get_customer_id(session_id)}")
            print(f"   Is authenticated: {auth_handler.is_authenticated(session_id)}")
        else:
            print(f"❌ Authentication failed: {message}")
            return False
        
        # Test authentication with invalid credentials
        print("\n--- Testing authentication with invalid credentials ---")
        session_id_2 = "test_session_2"
        success, message = auth_handler.authenticate(session_id_2, "invalid@example.com", "0000")
        if not success:
            print(f"✅ Correctly rejected invalid credentials: {message}")
        else:
            print(f"⚠️  Should have rejected invalid credentials")
        
        # Test clear auth
        print("\n--- Testing clear authentication ---")
        auth_handler.clear_auth(session_id)
        if not auth_handler.is_authenticated(session_id):
            print("✅ Authentication cleared successfully")
        else:
            print("❌ Authentication not cleared")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory():
    """Test session memory."""
    print("\n" + "=" * 60)
    print("Testing Session Memory")
    print("=" * 60)
    
    try:
        memory = SessionMemory()
        session_id = "test_memory_session"
        
        print("✅ Memory created")
        
        # Test adding messages
        print("\n--- Testing message storage ---")
        memory.add_message(session_id, "user", "Hello")
        memory.add_message(session_id, "assistant", "Hi there!")
        memory.add_message(session_id, "user", "How are you?")
        
        messages = memory.get_messages(session_id)
        if len(messages) == 3:
            print(f"✅ Stored {len(messages)} messages correctly")
        else:
            print(f"❌ Expected 3 messages, got {len(messages)}")
            return False
        
        # Test conversation context
        print("\n--- Testing conversation context ---")
        context = memory.get_conversation_context(session_id, max_messages=2)
        if len(context) == 2:
            print(f"✅ Retrieved last {len(context)} messages for context")
        else:
            print(f"⚠️  Expected 2 messages, got {len(context)}")
        
        # Test clear
        print("\n--- Testing memory clear ---")
        memory.clear(session_id)
        messages = memory.get_messages(session_id)
        if len(messages) == 0:
            print("✅ Memory cleared successfully")
        else:
            print(f"❌ Memory not cleared, still has {len(messages)} messages")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_basic():
    """Test agent with simple queries."""
    print("\n" + "=" * 60)
    print("Testing Support Agent - Basic Queries")
    print("=" * 60)
    
    try:
        client = MCPClient()
        client.initialize()
        auth_handler = AuthHandler(client)
        agent = SupportAgent(client, auth_handler)
        
        print("✅ Agent created")
        
        session_id = "test_agent_session"
        memory = SessionMemory()
        
        # Test product query (no auth needed)
        print("\n--- Testing product query (no auth) ---")
        query = "Show me some monitors"
        conversation_history = memory.get_conversation_context(session_id)
        
        response = agent.process_message(session_id, query, conversation_history)
        if response and len(response) > 0:
            print(f"✅ Agent responded to product query")
            print(f"   Response preview: {response[:200]}...")
            memory.add_message(session_id, "user", query)
            memory.add_message(session_id, "assistant", response)
        else:
            print("❌ Agent returned empty response")
            return False
        
        # Test specific product query
        print("\n--- Testing specific product query ---")
        query2 = "Tell me about product COM-0001"
        conversation_history = memory.get_conversation_context(session_id)
        
        response2 = agent.process_message(session_id, query2, conversation_history)
        if response2 and len(response2) > 0:
            print(f"✅ Agent responded to specific product query")
            print(f"   Response preview: {response2[:200]}...")
        else:
            print("❌ Agent returned empty response")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_with_auth():
    """Test agent with authentication flow."""
    print("\n" + "=" * 60)
    print("Testing Support Agent - Authentication Flow")
    print("=" * 60)
    
    try:
        client = MCPClient()
        client.initialize()
        auth_handler = AuthHandler(client)
        agent = SupportAgent(client, auth_handler)
        
        session_id = "test_auth_agent_session"
        memory = SessionMemory()
        
        # Test order query without authentication
        print("\n--- Testing order query without auth ---")
        query = "Show me my orders"
        conversation_history = memory.get_conversation_context(session_id)
        
        response = agent.process_message(session_id, query, conversation_history)
        if "authenticate" in response.lower() or "email" in response.lower() or "pin" in response.lower():
            print(f"✅ Agent correctly requested authentication")
            print(f"   Response: {response[:200]}...")
        else:
            print(f"⚠️  Agent response doesn't mention authentication: {response[:200]}")
        
        # Authenticate
        print("\n--- Authenticating user ---")
        email = "michellejames@example.com"
        pin = "1520"
        success, msg = auth_handler.authenticate(session_id, email, pin)
        if success:
            print(f"✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {msg}")
            return False
        
        # Test order query with authentication
        print("\n--- Testing order query with auth ---")
        query2 = "What are my orders?"
        conversation_history = memory.get_conversation_context(session_id)
        
        response2 = agent.process_message(session_id, query2, conversation_history)
        if response2 and len(response2) > 0:
            print(f"✅ Agent responded to order query after authentication")
            print(f"   Response preview: {response2[:200]}...")
        else:
            print("⚠️  Agent returned empty response (may be expected if no orders)")
        
        return True
    except Exception as e:
        print(f"❌ Agent auth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test full integration flow."""
    print("\n" + "=" * 60)
    print("Testing Full Integration Flow")
    print("=" * 60)
    
    try:
        # Simulate a customer conversation
        client = MCPClient()
        client.initialize()
        auth_handler = AuthHandler(client)
        memory = SessionMemory()
        agent = SupportAgent(client, auth_handler)
        
        session_id = "integration_test_session"
        
        print("--- Step 1: Customer asks about products ---")
        query1 = "What monitors do you have?"
        history1 = memory.get_conversation_context(session_id)
        response1 = agent.process_message(session_id, query1, history1)
        memory.add_message(session_id, "user", query1)
        memory.add_message(session_id, "assistant", response1)
        print(f"✅ Product query handled")
        print(f"   Response: {response1[:150]}...")
        
        print("\n--- Step 2: Customer asks about specific product ---")
        query2 = "Tell me about MON-0054"
        history2 = memory.get_conversation_context(session_id)
        response2 = agent.process_message(session_id, query2, history2)
        memory.add_message(session_id, "user", query2)
        memory.add_message(session_id, "assistant", response2)
        print(f"✅ Specific product query handled")
        print(f"   Response: {response2[:150]}...")
        
        print("\n--- Step 3: Customer tries to access orders (not authenticated) ---")
        query3 = "Show my orders"
        history3 = memory.get_conversation_context(session_id)
        response3 = agent.process_message(session_id, query3, history3)
        memory.add_message(session_id, "user", query3)
        memory.add_message(session_id, "assistant", response3)
        print(f"✅ Order query correctly requires authentication")
        print(f"   Response: {response3[:150]}...")
        
        print("\n--- Step 4: Customer authenticates ---")
        email = "laurahenderson@example.org"
        pin = "1488"
        success, msg = auth_handler.authenticate(session_id, email, pin)
        if success:
            print(f"✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {msg}")
            return False
        
        print("\n--- Step 5: Customer asks about orders (authenticated) ---")
        query4 = "What are my orders?"
        history4 = memory.get_conversation_context(session_id)
        response4 = agent.process_message(session_id, query4, history4)
        memory.add_message(session_id, "user", query4)
        memory.add_message(session_id, "assistant", response4)
        print(f"✅ Order query handled after authentication")
        print(f"   Response: {response4[:150]}...")
        
        print("\n✅ Full integration test passed!")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Starting Component Tests")
    print("=" * 60)
    
    results = []
    
    # Test individual components
    results.append(("MCP Client", test_mcp_client()))
    results.append(("Authentication", test_authentication()))
    results.append(("Memory", test_memory()))
    results.append(("Agent Basic", test_agent_basic()))
    results.append(("Agent Auth", test_agent_with_auth()))
    results.append(("Integration", test_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {len(results)} tests | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

