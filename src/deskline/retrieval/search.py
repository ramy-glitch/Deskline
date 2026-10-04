"""Read passages for a section that is already known."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGEngine, PGVectorStore

ROOT = Path(__file__).resolve().parents[3]


def open_store() -> PGVectorStore:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    load_dotenv(ROOT / ".env")
    engine = PGEngine.from_connection_string(os.environ["DATABASE_URL"])
    embeddings = OllamaEmbeddings(
        model=os.environ["EMBEDDING_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
    )
    return PGVectorStore.create_sync(
        engine=engine,
        table_name="chunks",
        embedding_service=embeddings,
        metadata_columns=["section_id", "source_url"],
    )


ALLOWED = {"appointments", "referrals_waiting", "records_results"}

def passages_for_section(question: str, section_id: str) -> list[Document]:
    if section_id not in ALLOWED:
        raise ValueError(f"unknown section: {section_id}")
    store = open_store()
    found = store.similarity_search(
        question,
        k=4,
        filter={"section_id": section_id},
    )
    kept = [
        doc
        for doc in found
        if doc.metadata.get("section_id") == section_id
    ]
    if len(kept) != len(found):
        raise RuntimeError(f"foreign passage returned for {section_id}")
    return kept