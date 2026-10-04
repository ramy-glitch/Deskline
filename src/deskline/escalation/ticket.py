"""Write a ticket when a turn stops."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[3]

UNCLEAR_REASON = "The section was not clear."
GAP_REASON = "The guidance is insufficient."


class Ticket(BaseModel):
    ticket_id: str
    section_id: str | None = None
    question: str
    passage_ids: list[str]
    reason: str


def psycopg_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def open_ticket(
    question: str,
    *,
    section_id: str | None,
    reason: str,
    passage_ids: list[str] | None = None,
) -> Ticket:
    load_dotenv(ROOT / ".env")
    ids = passage_ids or []
    with psycopg.connect(psycopg_url(os.environ["DATABASE_URL"])) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                section_id TEXT,
                question TEXT NOT NULL,
                passage_ids TEXT[] NOT NULL DEFAULT '{}',
                reason TEXT NOT NULL
            )
            """
        )
        row = conn.execute(
            """
            INSERT INTO tickets (section_id, question, passage_ids, reason)
            VALUES (%s, %s, %s, %s)
            RETURNING id::text
            """,
            (section_id, question, ids, reason),
        ).fetchone()
    return Ticket(
        ticket_id=row[0],
        question=question,
        passage_ids=ids,
        reason=reason,
        section_id=section_id,
    )