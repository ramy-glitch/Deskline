"""HTTP entry. One question returns a cited answer or a ticket."""

from fastapi import FastAPI
from pydantic import BaseModel

from deskline.escalation.ticket import GAP_REASON, UNCLEAR_REASON, Ticket, open_ticket
from deskline.generation.check import claims_supported
from deskline.generation.draft import draft
from deskline.router.label import section_label

app = FastAPI()


class Question(BaseModel):
    question: str


class CitedAnswer(BaseModel):
    section_id: str
    answer: str
    source_url: str


@app.post("/ask", response_model_exclude_none=True)
def ask(body: Question) -> CitedAnswer | Ticket:
    label = section_label(body.question)
    if label.section_id == "unclear":
        return open_ticket(body.question, section_id=None, reason=UNCLEAR_REASON)

    text, url, passages, passage_ids = draft(body.question, label.section_id)
    if not claims_supported(passages, text):
        return open_ticket(
            body.question,
            section_id=label.section_id,
            reason=GAP_REASON,
            passage_ids=passage_ids,
        )
    return CitedAnswer(answer=text, source_url=url, section_id=label.section_id)