async def generate_answer(question: str, context: list[str] | None = None) -> str:
    """Generate an answer with the LLM. Placeholder until a model is wired in."""
    if context:
        return f"[placeholder] Answer to {question!r} using {len(context)} retrieved chunk(s)."
    return f"[placeholder] Direct LLM answer to {question!r}."
