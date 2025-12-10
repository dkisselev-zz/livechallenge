# Customer Support Chatbot

A prototype customer support chatbot for a computer products company, built with Gradio, OpenAI GPT-4o-mini, and MCP server integration.

## Features

- **Product Inquiries**: Browse, search, and get details about products (no authentication required)
- **Order Management**: View and manage orders (requires authentication)
- **Session Memory**: Maintains conversation context within each session
- **Authentication**: Simple email/PIN authentication for order access

## Setup

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create Virtual Environment and Install Dependencies**
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

   Or use the provided run script:
   ```bash
   ./run.sh
   ```

3. **Configure Environment Variables**
   
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MCP_SERVER_URL=https://vipfapwm3x.us-east-1.awsapprunner.com/mcp
   HF_TOKEN=your_huggingface_token  # Optional, for deployment
   ```

4. **Run the Application**
   ```bash
   # Using the venv directly
   .venv/bin/python app.py
   
   # Or using the run script
   ./run.sh
   ```

   The application will start on `http://localhost:7860`

## Usage

### Product Queries (No Authentication)
- "Show me monitors"
- "What products do you have?"
- "Tell me about product COM-0001"
- "Search for printers"

### Order Queries (Requires Authentication)
- "Show my orders"
- "What's the status of my order?"
- "I want to place an order"

### Authentication
To authenticate, include in your message:
```
email: your@email.com, pin: 1234
```

## Test Customers

The following test customers are available:

- donaldgarcia@example.net / 7912
- michellejames@example.com / 1520
- laurahenderson@example.org / 1488
- spenceamanda@example.org / 2535
- glee@example.net / 4582
- williamsthomas@example.net / 4811
- justin78@example.net / 9279
- jason31@example.com / 1434
- samuel81@example.com / 4257
- williamleon@example.net / 9928

## Deployment to HuggingFace

1. Create a HuggingFace Space
2. Upload all files
3. Set environment variables in Space settings
4. The app will automatically deploy

## Architecture

- **app.py**: Gradio UI and session management
- **agent.py**: LLM agent with tool calling
- **mcp_client.py**: MCP server JSON-RPC client
- **auth.py**: Authentication handler
- **memory.py**: Session-based conversation memory
- **config.py**: Configuration management

## Notes

- Conversation memory is session-scoped and lost when the application restarts
- Authentication is required only for order-related operations
- The agent uses OpenAI function calling to select and invoke MCP tools

