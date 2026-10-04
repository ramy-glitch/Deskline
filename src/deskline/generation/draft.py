"""Draft a cited answer from passages already retrieved."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from deskline.retrieval.search import passages_for_section

ROOT = Path(__file__).resolve().parents[3]


def draft(question: str, section_id: str) -> tuple[str, str, str, list[str]]:
    load_dotenv(ROOT / ".env")
    found = passages_for_section(question, section_id)
    if not found:
        raise SystemExit(f"no passages for {section_id}")

    passages = "\n\n".join(doc.page_content for doc in found)
    passage_ids = [doc.id for doc in found if doc.id]
    model = ChatOllama(
        model=os.environ["CHAT_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
        reasoning=False,
    )
    answer = model.invoke(
        "Answer using only these passages. "
        "Do not add a rule that is not written in them.\n\n"
        f"Passages:\n{passages}\n\nQuestion: {question}"
    )
    source_url = found[0].metadata["source_url"]
    return str(answer.content), source_url, passages, passage_ids


if __name__ == "__main__":
    text, url, _, _ = draft("How can I change my hospital appointment?", "appointments")
    print(text)
    print(url)