import os
import openai
from openai import OpenAI
import httpx
from openai._base_client import SyncHttpxClientWrapper

# Load environment variables
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3.1-70B-Instruct")

# Patch for httpx 0.28+ compatibility with OpenAI client
class CustomHttpxClientWrapper(SyncHttpxClientWrapper):
    def __init__(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        super().__init__(*args, **kwargs)

openai._base_client.SyncHttpxClientWrapper = CustomHttpxClientWrapper

# Initialize the OpenAI-compatible client configured for Nebius Token Factory
nebius_client = OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY
)