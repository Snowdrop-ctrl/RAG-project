"""DeepSeek chat client (OpenAI-compatible /chat/completions endpoint)."""

import httpx

from app.config import settings

PLAIN_SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and concisely."

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions about the user's documents.\n"
    "Rules:\n"
    "1. Answer using ONLY the numbered context passages below.\n"
    "2. If the context does not contain the answer, say so plainly instead of guessing.\n"
    "3. Cite the passages you used with their numbers, e.g. [1] or [2].\n"
    "4. Be concise and factual."
)


class LLMError(RuntimeError):
    """The LLM could not be reached or returned an error."""


class LLMNotConfiguredError(LLMError):
    """No API key is set."""


def build_context_prompt(question: str, context: list[str]) -> str:
    passages = "\n\n".join(f"[{i}] {text}" for i, text in enumerate(context, start=1))
    return f"Context passages:\n\n{passages}\n\nQuestion: {question}"


async def complete(messages: list[dict[str, str]]) -> str:
    if not settings.deepseek_api_key:
        raise LLMNotConfiguredError(
            "DEEPSEEK_API_KEY is not set. Add it to backend/.env to enable answers."
        )

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            res = await client.post(
                f"{settings.deepseek_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
                json={
                    "model": settings.deepseek_model,
                    "messages": messages,
                    "max_tokens": settings.llm_max_tokens,
                    "stream": False,
                },
            )
    except httpx.HTTPError as exc:
        raise LLMError(f"Could not reach the LLM: {exc}") from exc

    if res.status_code == 401:
        raise LLMNotConfiguredError("DeepSeek rejected the API key (401). Check DEEPSEEK_API_KEY.")
    if res.status_code != 200:
        raise LLMError(f"LLM request failed ({res.status_code}): {res.text[:300]}")

    try:
        return res.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMError("Unexpected response shape from the LLM.") from exc


async def generate_answer(question: str, context: list[str] | None = None) -> str:
    if context:
        return await complete(
            [
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": build_context_prompt(question, context)},
            ]
        )
    return await complete(
        [
            {"role": "system", "content": PLAIN_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
    )
