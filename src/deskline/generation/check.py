"""Decide whether a draft stays inside the passages."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]


class Grounding(BaseModel):
    """Whether every claim in the draft is written in the passages."""

    supported: bool = Field(
        description=(
            "True only when every claim in the answer is written in the passages. "
            "False when the answer adds a fact, or when it says the passages do not contain the answer."
        )
    )


def claims_supported(passages: str, answer: str) -> bool:
    load_dotenv(ROOT / ".env")
    model = ChatOllama(
        model=os.environ["CHAT_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
        temperature=0,
        reasoning=False,
    )
    structured = model.with_structured_output(Grounding)
    try:
        result = structured.invoke(
            "Is every claim in the answer written in the passages?\n"
            "Answer true only when each claim appears in the passages.\n"
            "Answer false when the answer adds a wait, a step, or a rule, "
            "or when the answer says the passages do not contain the fact.\n\n"
            f"Passages:\n{passages}\n\nAnswer:\n{answer}"
        )
    except Exception:
        return False
    if not isinstance(result, Grounding):
        return False
    return result.supported