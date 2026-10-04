"""HTTP entry. One question returns a cited answer, a ticket, or a signpost."""

from fastapi import FastAPI
from pydantic import BaseModel

from deskline.escalation.signpost import SIGNPOST
from deskline.escalation.ticket import GAP_REASON, UNCLEAR_REASON, Ticket, open_ticket
from deskline.generation.check import claims_supported
from deskline.generation.draft import draft
from deskline.router.clinical import seeks_clinical_advice
from deskline.router.label import section_label

app = FastAPI()


class Question(BaseModel):
    question: str


class CitedAnswer(BaseModel):
    section_id: str
    answer: str
    source_url: str


class Signpost(BaseModel):
    signpost: str


@app.post("/ask", response_model_exclude_none=True)
def ask(body: Question) -> CitedAnswer | Ticket | Signpost:
    if seeks_clinical_advice(body.question):
        return Signpost(signpost=SIGNPOST)

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