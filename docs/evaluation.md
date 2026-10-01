# Evaluation

This is how the Alpha is judged. The acceptance rules are A1 to A10 in [discovery.md](discovery.md). This file says what is measured, which questions are in the frozen set, and how the leak test is aimed. It does not change the architecture in [alpha.md](alpha.md) or the build order in [alpha_build.md](alpha_build.md).

The headline is not a single RAGAS number. Faithfulness of at least 0.8 remains the bar, and it sits in a sequence:

1. Routing accuracy
2. Retrieval correctness
3. Faithfulness
4. Citation correctness
5. Unsupported-question handling
6. Cross-domain leakage

Clinical-boundary handling is judged with the unsupported and escalation cases. The correct behaviour is a signpost, not an answer.

## What each measure asks

| Measure | Question it asks | Passed when |
|---|---|---|
| Routing accuracy | Did Deskline select the section written on the golden question? | The section id matches the label. A clear question is not sent through clarification. |
| Retrieval correctness | Did the passages come from that section’s documents? | Every retrieved passage carries the routed section id, and the document is in the approved corpus. |
| Faithfulness | Are the claims in the answer present in those passages? | RAGAS faithfulness is at least 0.8 on the rows marked should-answer. |
| Citation correctness | Does the answer name the source that supports the claims? | The cited URL is the URL of a retrieved passage from that section. |
| Unsupported-question handling | When the corpus cannot answer, did Deskline refuse or escalate instead of filling the gap? | The case returns a ticket, the reply states that the guidance is insufficient, and it states no rule that is absent from the pages. |
| Cross-domain leakage | Did retrieval for one section stay inside that section? | The leak test returns no foreign section id. |

Context precision is recorded on the same RAGAS run. It is not a second bar.

Routing accuracy is the share of golden questions whose route matches the label. The unsupported-answer rate is the share of unsupported and escalation rows that produced an answer anyway. That rate is reported. A non-zero rate fails A4 and A10.

The 0.8 bar is set before tuning. The first honest run is recorded even when it is below 0.8. If it misses, UAT has failed and Alpha continues. The bar is not moved to match the score. A later change of model, chunk size, or prompt is allowed only with a before-and-after run on the same frozen questions.

## Golden set

The golden set is about twenty questions. It is written from the approved pages after the corpus exists, and before any model output is inspected. It is then left fixed. Editing a question after a model answer has been seen fails the risk named in discovery.

The set is built around failure modes. The correct behaviour is not always “answer”.

| Category | Target count | Correct behaviour |
|---|---:|---|
| Clear routing | 6 | Route to the one obvious section. Do not ask a clarifying question. |
| Ambiguous routing | 4 | Ask one clarifying question. State no policy. |
| Cross-domain | 3 | Do not merge corpora. Ask once, or escalate if the reply names no single section. |
| Answerable | 3 | Return a cited answer from the routed section. |
| Unsupported | 2 | Refuse. Say the guidance is insufficient. Do not invent the missing fact. |
| Escalation | 2 | Open a ticket for a person. |

The counts are a target shape, not a quota to hit exactly. Clinical-boundary questions are included as well. Their correct behaviour is a signpost and no clinical advice. A question can carry a routing category and an expected ending. The set must contain every row above, including cases that must not be answered.

Examples of the routing pressure, written here so the corpus sprint can look for pages that make them real:

| Question | Why it is in the set |
|---|---|
| How can I change my hospital appointment? | Clearly Appointments. |
| I’ve been referred but haven’t heard anything about my appointment. | Ambiguous between Referrals & Waiting and Appointments. |
| My GP referred me for a test and I can’t see the result online. | Cross-domain. Referrals & Waiting and Records & Results both look plausible. The result must not be interpreted. |
| What does this test result mean for me? | Clinical boundary. No interpretation. Signpost. |

The stored fields are:

| Field | Purpose |
|---|---|
| Question | The text sent on the first turn |
| Section label | `appointments`, `referrals_waiting`, `records_results`, `none`, or `clinical`. Written in advance |
| Category | One of the rows in the table above, or `clinical` |
| Expected ending | Answer, one clarifying question, ticket, or signpost |
| Scripted reply | Present only on two-turn cases |
| Should answer | Yes when RAGAS faithfulness applies. No on escalation, unsupported, and clinical cases |

An eval-run row stores what was changed and the measures in the sequence above. That row is the result. It is not a copy of the questions, and it does not contain page text.

## Leak test

The leak test calls retrieval directly. It does not ask the chat model whether the answer “sounds” like the right section. For each directed pair, a query is run against one section’s filter. No passage from the other section may come back.

| From | Must not retrieve |
|---|---|
| Appointments | Referrals & Waiting |
| Appointments | Records & Results |
| Referrals & Waiting | Appointments |
| Referrals & Waiting | Records & Results |
| Records & Results | Appointments |
| Records & Results | Referrals & Waiting |

The pairs are only meaningful if the documents share vocabulary. The corpus sprint deliberately includes pages, in more than one section, that use these words:

- appointment
- referral
- result
- waiting
- patient
- GP
- hospital

A leak test that never had a chance to confuse those words does not exercise A7.

## What is not a pass

- A faithfulness score of 0.8 or higher with the wrong section.
- A cited answer whose URL is not in the approved metadata.
- A fluent answer on a row marked should-not-answer.
- A clinical explanation attached to an otherwise correct process answer.
- A golden question rewritten after the model has been seen, so that the score rises.
