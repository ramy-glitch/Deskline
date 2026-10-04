"""Ask the chat model for one section label."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]

SectionId = Literal[
    "appointments",
    "referrals_waiting",
    "records_results",
    "unclear",
]


class SectionLabel(BaseModel):
    """The one section a question belongs to."""

    section_id: SectionId = Field(
        description=(
            "appointments, referrals_waiting, records_results, or unclear. "
            "Use unclear when the question fits more than one section or none."
        )
    )


def section_label(question: str) -> SectionLabel:
    load_dotenv(ROOT / ".env")
    model = ChatOllama(
        model=os.environ["CHAT_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
        temperature=0,
        reasoning=False,
    )
    structured = model.with_structured_output(SectionLabel)
    try:
        result = structured.invoke(
            "Choose one section for this question.\n"
            "appointments: booking or changing an appointment.\n"
            "referrals_waiting: a referral or a waiting time.\n"
            "records_results: health records or test results.\n"
            "unclear: more than one of those, or none of them.\n\n"
            f"Question: {question}"
        )
    except Exception:
        return SectionLabel(section_id="unclear")
    if not isinstance(result, SectionLabel):
        return SectionLabel(section_id="unclear")
    return result


if __name__ == "__main__":
    label = section_label("How can I change my hospital appointment?")
    print(label.model_dump())
    