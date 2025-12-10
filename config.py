"""Configuration management for the customer support chatbot."""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp")

# HuggingFace Configuration (for deployment)
HF_TOKEN = os.getenv("HF_TOKEN", "")

# OpenAI Model
OPENAI_MODEL = "gpt-4o-mini"

