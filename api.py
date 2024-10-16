from fastapi import FastAPI, HTTPException
from llm_handler import LLMHandler
from config import MODEL_PATH
from pydantic import BaseModel

app = FastAPI()
llm_handler = LLMHandler(model_path=MODEL_PATH)

class PromptRequest(BaseModel):
    prompt: str
    user: str

@app.post("/generate")
async def generate_response(request: PromptRequest):
    try:
        response = llm_handler.generate_response(request.prompt, request.user)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_info")
async def get_model_info():
    return llm_handler.get_model_info()
