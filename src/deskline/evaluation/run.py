"""Score the frozen golden set. Started by hand. Not part of a request."""

import asyncio
import json
import os
import sys
from pathlib import Path

import psycopg
from datasets import Dataset
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference
from ragas.run_config import RunConfig

from deskline.api.main import CitedAnswer, Question, Signpost, Ticket, ask
from deskline.escalation.ticket import psycopg_url
from deskline.retrieval.search import passages_for_section

ROOT = Path(__file__).resolve().parents[3]
GOLDEN = ROOT / "eval" / "golden.json"
SECTIONS = {"appointments", "referrals_waiting", "records_results"}
BAR = 0.8


def ending_of(result: CitedAnswer | Ticket | Signpost | None) -> str:
    if isinstance(result, CitedAnswer):
        return "answer"
    if isinstance(result, Ticket):
        return "ticket"
    if isinstance(result, Signpost):
        return "signpost"
    return "error"


def section_of(result: CitedAnswer | Ticket | Signpost | None) -> str | None:
    if isinstance(result, (CitedAnswer, Ticket)):
        return result.section_id
    return None


def route_matches(label: str, result: CitedAnswer | Ticket | Signpost | None) -> bool:
    if label == "clinical":
        return isinstance(result, Signpost)
    if label == "none":
        return isinstance(result, Ticket) and result.section_id is None
    return section_of(result) == label


def contexts_for(question: str, section_id: str) -> tuple[list[str], bool, str]:
    found = passages_for_section(question, section_id)
    passages = [doc.page_content for doc in found]
    urls = [doc.metadata.get("source_url") for doc in found]
    return passages, True, urls


def mean_or_none(frame, column: str) -> float | None:
    if column not in frame:
        return None
    value = frame[column].mean(skipna=True)
    if value != value:
        return None
    return float(value)


def store_run(note: str, scores: dict[str, float | None]) -> str:
    load_dotenv(ROOT / ".env")
    with psycopg.connect(psycopg_url(os.environ["DATABASE_URL"])) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS eval_runs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                note TEXT NOT NULL,
                routing_accuracy DOUBLE PRECISION,
                faithfulness DOUBLE PRECISION,
                context_precision DOUBLE PRECISION,
                citation_correctness DOUBLE PRECISION,
                unsupported_answer_rate DOUBLE PRECISION
            )
            """
        )
        row = conn.execute(
            """
            INSERT INTO eval_runs (
                note, routing_accuracy, faithfulness, context_precision,
                citation_correctness, unsupported_answer_rate
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id::text
            """,
            (
                note,
                scores["routing_accuracy"],
                scores["faithfulness"],
                scores["context_precision"],
                scores["citation_correctness"],
                scores["unsupported_answer_rate"],
            ),
        ).fetchone()
    return row[0]


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    load_dotenv(ROOT / ".env")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    note = " ".join(sys.argv[1:]) or "eval run"

    samples = []
    route_hits = 0
    cited_ok = 0
    cited_total = 0
    unsupported_answers = 0
    unsupported_total = 0

    for row in golden:
        try:
            result = ask(Question(question=row["question"]))
        except SystemExit:
            result = None
        if route_matches(row["section_label"], result):
            route_hits += 1
        if row["category"] in {"unsupported", "escalation"}:
            unsupported_total += 1
            if ending_of(result) == "answer":
                unsupported_answers += 1
        if not row["should_answer"] or not isinstance(result, CitedAnswer):
            continue
        passages, _, urls = contexts_for(row["question"], result.section_id)
        cited_total += 1
        if result.source_url in urls:
            cited_ok += 1
        samples.append(
            {
                "user_input": row["question"],
                "response": result.answer,
                "retrieved_contexts": passages,
            }
        )

    faithfulness = None
    context_precision = None
    if samples:
        judge = LangchainLLMWrapper(
            ChatOllama(
                model=os.environ["CHAT_MODEL"],
                base_url=os.environ["OLLAMA_BASE_URL"],
                temperature=0,
                reasoning=False,
                num_ctx=8192,
            )
        )
        scored = evaluate(
            Dataset.from_list(samples),
            metrics=[Faithfulness(), LLMContextPrecisionWithoutReference()],
            llm=judge,
            run_config=RunConfig(max_workers=1, timeout=180),
            raise_exceptions=False,
        )
        frame = scored.to_pandas()
        faithfulness = mean_or_none(frame, "faithfulness")
        context_precision = mean_or_none(
            frame, "llm_context_precision_without_reference"
        )

    scores = {
        "routing_accuracy": route_hits / len(golden),
        "faithfulness": faithfulness,
        "context_precision": context_precision,
        "citation_correctness": (cited_ok / cited_total) if cited_total else None,
        "unsupported_answer_rate": (
            unsupported_answers / unsupported_total if unsupported_total else None
        ),
    }
    run_id = store_run(note, scores)
    for name, value in scores.items():
        print(f"{name}: {value}")
    print(f"faithfulness bar: {BAR}")
    print(f"eval_run: {run_id}")


if __name__ == "__main__":
    main()