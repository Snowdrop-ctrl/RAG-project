from fastapi import APIRouter, HTTPException

from app.schemas import ChatMode, ChatRequest, ChatResponse, Source
from app.services import llm, rag

router = APIRouter(tags=["chat"])

NO_DOCUMENTS_HINT = (
    "I could not find anything relevant in your documents. "
    "Upload documents first, or switch to LLM mode to answer without them."
)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        if req.mode == ChatMode.LLM:
            return ChatResponse(answer=await llm.generate_answer(req.question))

        chunks = await rag.retrieve(req.question)
        if not chunks:
            return ChatResponse(answer=NO_DOCUMENTS_HINT)

        answer = await llm.generate_answer(req.question, context=[c.text for c in chunks])
        sources = [
            Source(label=c.label, source=c.source, page=c.page, score=round(c.score, 3))
            for c in chunks
        ]
        return ChatResponse(answer=answer, sources=sources)

    except llm.LLMNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except llm.LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
