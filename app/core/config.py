import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Retrieve Nebius credentials and model configuration from environment
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.nebius.ai/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-ultra-70b")

if not NEBIUS_API_KEY:
  raise ValueError(
      "NEBIUS_API_KEY is missing from environment variables or .env file."
  )

# Initialize the OpenAI-compatible client configured for Nebius Token Factory

import httpx

nebius_client = OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY,
    http_client=httpx.Client(proxies=None)
)