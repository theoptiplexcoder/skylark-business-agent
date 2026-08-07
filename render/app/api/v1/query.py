from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Union
from app.agents.query_agent import QueryAgentWorkflow
from langchain_huggingface import HuggingFaceEndpoint
from app.core.config import get_settings

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    query: str

settings = get_settings()

def get_llm():
    # In a real setup, configure model kwargs here
    return HuggingFaceEndpoint(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1")

@router.post("")
async def execute_query(request: QueryRequest, llm = Depends(get_llm)):
    agent = QueryAgentWorkflow(llm=llm)
    try:
        result = await agent.run(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
