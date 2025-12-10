#!/usr/bin/env python3
"""
Test script to explore MCP server capabilities
"""
import requests
import json
import time
import sys

def test_mcp_server():
    url = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"
    
    # Test 1: Check if it requires SSE
    print("=" * 60)
    print("Test 1: Testing with Accept: text/event-stream")
    print("=" * 60)
    
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Headers: {dict(response.headers)}")
        print("\nStreaming data (first 10 seconds):")
        print("-" * 60)
        
        start_time = time.time()
        for line in response.iter_lines():
            if time.time() - start_time > 10:
                break
            if line:
                decoded = line.decode('utf-8')
                print(decoded)
                # Try to parse as JSON if it looks like JSON-RPC
                if decoded.strip().startswith('data:'):
                    data_part = decoded.replace('data:', '').strip()
                    try:
                        json_data = json.loads(data_part)
                        print(f"  -> Parsed JSON: {json.dumps(json_data, indent=2)}")
                    except:
                        pass
                elif decoded.strip().startswith('{'):
                    try:
                        json_data = json.loads(decoded)
                        print(f"  -> Parsed JSON: {json.dumps(json_data, indent=2)}")
                    except:
                        pass
    except requests.exceptions.Timeout:
        print("Request timed out (this is expected for SSE streams)")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try POST with JSON-RPC initialize (with Accept: application/json)
    print("\n" + "=" * 60)
    print("Test 2: Testing POST with JSON-RPC initialize")
    print("=" * 60)
    
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        # Try POST with Accept: application/json
        response = requests.post(url, json=initialize_request, 
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.headers.get('Content-Type') == 'application/json':
            print(f"Parsed JSON: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2b: Try sending JSON-RPC over SSE connection
    print("\n" + "=" * 60)
    print("Test 2b: Testing JSON-RPC over SSE connection")
    print("=" * 60)
    
    try:
        # Open SSE connection and send initialize message
        sse_headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        response = requests.post(url, json=initialize_request, 
                                headers={
                                    "Content-Type": "application/json",
                                    **sse_headers
                                }, stream=True, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("Reading SSE stream (5 seconds):")
            start_time = time.time()
            for line in response.iter_lines():
                if time.time() - start_time > 5:
                    break
                if line:
                    decoded = line.decode('utf-8')
                    print(f"  {decoded}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: List available tools
    print("\n" + "=" * 60)
    print("Test 3: Listing available tools")
    print("=" * 60)
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    try:
        response = requests.post(url, json=tools_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: List available resources
    print("\n" + "=" * 60)
    print("Test 4: Listing available resources")
    print("=" * 60)
    
    resources_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list"
    }
    
    try:
        response = requests.post(url, json=resources_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: List available prompts
    print("\n" + "=" * 60)
    print("Test 5: Listing available prompts")
    print("=" * 60)
    
    prompts_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list"
    }
    
    try:
        response = requests.post(url, json=prompts_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Test some tools
    print("\n" + "=" * 60)
    print("Test 6: Testing tools")
    print("=" * 60)
    
    # Test list_products
    print("\n--- Testing list_products ---")
    list_products_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "list_products",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(url, json=list_products_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"list_products result:\n{json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get_product
    print("\n--- Testing get_product with SKU 'COM-0001' ---")
    get_product_request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "get_product",
            "arguments": {
                "sku": "COM-0001"
            }
        }
    }
    
    try:
        response = requests.post(url, json=get_product_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"get_product result:\n{json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test search_products
    print("\n--- Testing search_products with query 'monitor' ---")
    search_products_request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "search_products",
            "arguments": {
                "query": "monitor"
            }
        }
    }
    
    try:
        response = requests.post(url, json=search_products_request,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"search_products result:\n{json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mcp_server()

