from enum import StrEnum

from pydantic import BaseModel, Field


class ChatMode(StrEnum):
    LLM = "llm"
    LLM_RAG = "llm_rag"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: ChatMode = ChatMode.LLM_RAG


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
