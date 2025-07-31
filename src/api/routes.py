from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from llm.gpt2_poetry import GPT2Poetry
from pydantic import BaseModel

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 50
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.95
    repetition_penalty: float = 1.2


model_router = APIRouter()

@model_router.post("/generate_poem")
async def generate_poem(request: GenerationRequest):
    """
    Generate a poem based on the given prompt.
    """

    prompt = request.prompt
    max_length = request.max_length
    temperature = request.temperature
    top_k = request.top_k
    top_p = request.top_p
    repetition_penalty = request.repetition_penalty

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if not (0 < max_length <= 200):
        raise HTTPException(status_code=400, detail="Max length must be between 1 and 200")
    
    if not (0 <= temperature <= 2):
        raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")
    
    if not (0 <= top_k <= 100):
        raise HTTPException(status_code=400, detail="Top-K must be between 0 and 100")
    
    if not (0 <= top_p <= 1):
        raise HTTPException(status_code=400, detail="Top-P must be between 0 and 1")
    
    if not (1 <= repetition_penalty <= 2):
        raise HTTPException(status_code=400, detail="Repetition penalty must be between 1 and 2")

    gpt2_poetry = GPT2Poetry()
    poem = gpt2_poetry.generate_poem(
        prompt=prompt,
        max_length=max_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty
    )
    
    if not poem:
        raise HTTPException(status_code=500, detail="Failed to generate poem")
    return JSONResponse(status_code=200, content={"poem": poem})