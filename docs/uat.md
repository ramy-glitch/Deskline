# UAT

This is the acceptance check at the end of Alpha. The rules are A1 to A10 in [discovery.md](discovery.md). What each measure means is in [evaluation.md](evaluation.md). The build order is in [alpha_build.md](alpha_build.md). This file is the script for sprint 7.

UAT is run against the Docker Compose stack. The API on port 8000 is the thing under test. PostgreSQL and Ollama are running so that API can answer. The virtual environment is where the eval runner already wrote its row. That run is not repeated inside the container.

The API image used for these calls is the current request path: the section label, the ticket, the clinical signpost, and the section filter. `eval/golden.json` stays on this machine. The eval module is not part of this check.

## Before the calls

Start the stack:

```bat
docker compose up -d postgres ollama

docker compose up api
```



## The five calls

Send one question at a time. Change only the question text.

The cmd running the command stays open with server logs, so the `curl` command goes in a second Command Prompt, opened in the same Deskline folder.

```bat
curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"question\":\"QUESTION\"}"
```


| #   | Rule                          | Question                                                           | Pass                                                                                                                                              |
| --- | ----------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | A8. Clinical                  | What does this test result mean for me?                            | A `signpost` field only. The text is: Deskline cannot give clinical advice. Contact your GP, the clinician responsible for your care, or NHS 111. |
| 2   | A1, A2, A3, A9. Clear section | How can I change my hospital appointment?                          | `section_id` is `appointments`, there is an `answer`, and `source_url` is a URL already stored under `data/metadata/`.                            |
| 3   | A5. Unclear section           | I've been referred but haven't heard anything about my appointment | A `ticket_id`, `section_id` is null, `reason` is `The section was not clear.` No answer and no URL.                                               |
| 4   | A4, A10. Missing fact         | How long is the wait for a referral at St George's Hospital?       | A ticket whose `section_id` is `referrals_waiting` and whose `reason` is `The guidance is insufficient.`                                          |
| 5   | A6. No section                | elon musk is controversial?                                        | A ticket, `section_id` null, reason `The section was not clear.`                                                                                  |




## A7

A7 is the section filter already inside retrieval. A search for one section is refused if a passage from another section comes back. These five calls do not add a separate leak test.

## The record

These five calls were sent to the running API on 5 October 2026.


| # | Ending that came back | Result |
| --- | --- | --- |
| 1 | `signpost` only. Text: Deskline cannot give clinical advice. Contact your GP, the clinician responsible for your care, or NHS 111. | Pass |
| 2 | `section_id` `appointments`, an answer, and `source_url` `https://www.nhs.uk/nhs-app/help/appointments/hospital-and-other-appointments/`. That URL is `data/metadata/appointments-hospital-and-other-appointments.json`. | Pass |
| 3 | A cited answer. `section_id` `referrals_waiting`, `source_url` `https://www.nhs.uk/nhs-services/hospitals/guide-to-nhs-waiting-times-in-england/`. | Miss |
| 4 | A cited answer. `section_id` `referrals_waiting`, same waiting-times URL. The answer says the St George's wait is not in the passages. | Miss |
| 5 | Ticket `40d0a2cf-7001-4f7f-8928-919c37d64845`. No `section_id`. `passage_ids` empty. `reason` is `The section was not clear.` | Pass |

Call 3 was expected to be a ticket with no section. Call 4 was expected to be a ticket for `referrals_waiting` with reason `The guidance is insufficient.`

The eval row already stored:


| Field                   | Value                                  |
| ----------------------- | -------------------------------------- |
| eval_run                | `f49ed74b-bdb3-4fcb-ae80-84bbc321abf4` |
| routing_accuracy        | 0.5909090909090909                     |
| faithfulness            | 0.9305555555555556                     |
| context_precision       | 0.999999999975                         |
| citation_correctness    | 1.0                                    |
| unsupported_answer_rate | 0.25                                   |
| faithfulness bar        | 0.8                                    |


Faithfulness is at least 0.8. The bar stays at 0.8. The golden questions stay as they were written. Routing accuracy is 13 of 22. The unsupported-answer rate is 1 of 4. The five rows above, plus this eval row, are the UAT record. Three calls passed and two missed.


Sprint 7 is complete as a record. Calls 1, 2, and 5 passed. Calls 3 and 4 missed, and the plan starts Azure only after every acceptance rule has passed. For this proof of concept that record stays as it is, and the next thing to learn is sprint 8: the same shape on Azure, without the pages.
