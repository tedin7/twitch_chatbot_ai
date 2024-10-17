from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from llm_handler import LLMHandler
from config import MODEL_PATH
from pydantic import BaseModel

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

llm_handler = LLMHandler(model_path=MODEL_PATH)

class PromptRequest(BaseModel):
    prompt: str
    user: str

@app.post("/generate")
@limiter.limit("5/minute")
async def generate_response(request: Request, prompt_request: PromptRequest):
    try:
        response = llm_handler.generate_response(prompt_request.prompt, prompt_request.user)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_info")
async def get_model_info():
    return llm_handler.get_model_info()
