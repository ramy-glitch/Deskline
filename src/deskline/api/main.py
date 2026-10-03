"""HTTP entry for one known section."""

from fastapi import FastAPI
from pydantic import BaseModel

from deskline.generation.draft import draft

app = FastAPI()


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str
    source_url: str
    section_id: str


@app.post("/ask")
def ask(body: Question) -> Answer:
    text, url = draft(body.question, "appointments")
    return Answer(answer=text, source_url=url, section_id="appointments")