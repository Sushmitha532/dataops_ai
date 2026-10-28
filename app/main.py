from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.router import route_user_request

# Initialize the FastAPI app instance
app = FastAPI()

# Add this root endpoint so visiting the URL doesn't show "Not Found"
@app.get("/")
def read_root():
    return {"status": "online", "service": "DataOps AI Copilot API"}

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = route_user_request(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))