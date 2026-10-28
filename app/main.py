from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.router import route_user_request

# Initialize the FastAPI app instance
app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Call your supervisor router directly
        response = route_user_request(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))