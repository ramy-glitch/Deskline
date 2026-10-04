"""Decide whether a question asks for clinical advice."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]


class ClinicalBoundary(BaseModel):
    """Whether the question asks for clinical advice."""

    clinical: bool = Field(
        description=(
            "True when the question asks for a diagnosis, a treatment, "
            "or an interpretation of symptoms or results."
        )
    )


def seeks_clinical_advice(question: str) -> bool:
    load_dotenv(ROOT / ".env")
    model = ChatOllama(
        model=os.environ["CHAT_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
        temperature=0,
        reasoning=False,
    )
    structured = model.with_structured_output(ClinicalBoundary)
    try:
        result = structured.invoke(
            "Decide whether this question asks for clinical advice.\n"
            "clinical is true when it asks for a diagnosis, a treatment, "
            "or an interpretation of symptoms or results.\n"
            "clinical is false when it asks about an appointment, a referral, "
            "a waiting time, a health record, or how to see a test result.\n"
            "Asking how to see a result is not an interpretation of that result.\n\n"
            f"Question: {question}"
        )
    except Exception:
        return True
    if not isinstance(result, ClinicalBoundary):
        return True
    return result.clinical