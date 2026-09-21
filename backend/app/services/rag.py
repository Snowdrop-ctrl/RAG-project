from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str


async def retrieve(question: str, top_k: int = 4) -> list[Chunk]:
    """Fetch the most relevant chunks for a question. Placeholder until a vector store exists."""
    return [
        Chunk(text="Sample chunk about the topic.", source="sample-document.pdf"),
        Chunk(text="Another relevant passage.", source="knowledge-base.md"),
    ][:top_k]
