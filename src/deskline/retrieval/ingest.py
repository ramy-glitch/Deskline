"""Load the approved pages once: split, embed, and store chunks."""

import json
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import Column, PGEngine, PGVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "data" / "corpus"
METADATA = ROOT / "data" / "metadata"

# First-run length. i will Change it later only with a before-and-after eval run.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SECTIONS = {
    "appointments": "Appointments",
    "referrals_waiting": "Referrals & Waiting",
    "records_results": "Records & Results",
}


def psycopg_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def ensure_sections(database_url: str) -> None:
    with psycopg.connect(psycopg_url(database_url)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )
        for section_id, name in SECTIONS.items():
            conn.execute(
                """
                INSERT INTO sections (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                """,
                (section_id, name),
            )


def load_pages() -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    documents: list[Document] = []

    for path in sorted(METADATA.glob("*.json")):
        if path.name == "document.example.json":
            continue

        row = json.loads(path.read_text(encoding="utf-8"))
        section_id = row["section"]
        if section_id not in SECTIONS:
            raise SystemExit(f"{path.name} has an unknown section: {section_id}")

        prefix = section_id + "-"
        if not path.stem.startswith(prefix):
            raise SystemExit(f"{path.name} does not start with {prefix}")

        slug = path.stem[len(prefix) :]
        text_path = CORPUS / section_id / f"{slug}.txt"
        if not text_path.is_file():
            raise SystemExit(f"missing text file for {path.name}: {text_path}")

        text = text_path.read_text(encoding="utf-8").strip()
        if not text:
            raise SystemExit(f"{text_path} is empty")

        for passage in splitter.split_text(text):
            documents.append(
                Document(
                    page_content=passage,
                    metadata={
                        "section_id": section_id,
                        "source_url": row["url"],
                    },
                )
            )
        print(f"{section_id}/{slug}.txt -> {len(splitter.split_text(text))} passages")

    if not documents:
        raise SystemExit("no metadata rows to ingest")
    return documents


def main() -> None:
    load_dotenv(ROOT / ".env")
    database_url = os.environ["DATABASE_URL"]
    dimensions = int(os.environ["EMBEDDING_DIMENSIONS"])

    ensure_sections(database_url)
    documents = load_pages()

    engine = PGEngine.from_connection_string(database_url)
    try:
        engine.init_vectorstore_table(
            table_name="chunks",
            vector_size=dimensions,
            metadata_columns=[
                Column("section_id", "TEXT", nullable=False),
                Column("source_url", "TEXT", nullable=False),
            ],
        )
    except Exception as exc:
        if "already exists" in str(exc).lower():
            raise SystemExit(
                "chunks already exists. Ingest runs once. "
                "Do not run it again unless the table is dropped on purpose."
            ) from exc
        raise

    embeddings = OllamaEmbeddings(
        model=os.environ["EMBEDDING_MODEL"],
        base_url=os.environ["OLLAMA_BASE_URL"],
    )
    store = PGVectorStore.create_sync(
        engine=engine,
        table_name="chunks",
        embedding_service=embeddings,
        metadata_columns=["section_id", "source_url"],
    )
    store.add_documents(documents)
    print(f"stored {len(documents)} passages")


if __name__ == "__main__":
    main()