from fastapi import APIRouter

from app.schemas import ChatMode, ChatRequest, ChatResponse
from app.services import llm, rag

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if req.mode == ChatMode.LLM:
        return ChatResponse(answer=await llm.generate_answer(req.question))

    chunks = await rag.retrieve(req.question)
    answer = await llm.generate_answer(req.question, context=[c.text for c in chunks])
    return ChatResponse(answer=answer, sources=sorted({c.source for c in chunks}))
