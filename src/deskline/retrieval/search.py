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


def passages_for_section(question: str, section_id: str) -> list[Document]:
    store = open_store()
    return store.similarity_search(
        question,
        k=4,
        filter={"section_id": section_id},
    )