import openai
from openai._base_client import SyncHttpxClientWrapper

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