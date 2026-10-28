from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.router import route_agent  # or your router function
from app.agents.router import route_user_request as agent_router

app.include_router(agent_router)

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = route_agent(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))