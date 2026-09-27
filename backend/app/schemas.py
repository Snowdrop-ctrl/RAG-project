from enum import StrEnum

from pydantic import BaseModel, Field


class ChatMode(StrEnum):
    LLM = "llm"
    LLM_RAG = "llm_rag"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: ChatMode = ChatMode.LLM_RAG


class Source(BaseModel):
    label: str
    source: str
    page: int | None = None
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []


class DocumentInfo(BaseModel):
    source: str
    chunks: int


class DocumentList(BaseModel):
    documents: list[DocumentInfo]
    total_chunks: int
