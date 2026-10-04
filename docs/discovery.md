# Discovery findings

Deskline is a learning simulation of a healthcare policy-navigation assistant. It is not commissioned by or affiliated with the NHS, and it is not a clinical decision-support system.

Deskline retrieves and explains information contained in its approved policy corpus. It does not provide clinical advice.

It does not:

- diagnose
- interpret symptoms
- recommend treatment
- provide patient-specific clinical advice
- replace clinicians
- make clinical decisions

The engineering question is unchanged by the domain:

> Can Deskline route a question to the correct healthcare-policy domain and produce a cited answer grounded only in the appropriate evidence, while refusing or escalating when the evidence is insufficient?

## Source decision

The corpus is official published guidance about healthcare administration. Three domains are used. They are broad enough to hold real public material, and distinct enough that routing is meaningful.

| Section | What the pages are about |
|---|---|
| Appointments | Appointments, changing or cancelling appointments, patient choice, and related processes. Section id `appointments`. |
| Referrals & Waiting | Referrals, referral pathways, elective care, and waiting processes. Section id `referrals_waiting`. |
| Records & Results | Access to health records, online services, and the process of obtaining test results. Section id `records_results`. |

Records & Results explains how a person obtains a result. It does not explain what a result means.

The Alpha corpus is small and chosen on purpose. The target is about five to ten authoritative documents or pages in each domain, not a general NHS knowledge base. The point of the corpus is that it was selected and evaluated, not that it is large.

Each document is an official published page. Copyright and reuse stay with the publisher. The licence is checked when the page is collected. This note is not a legal opinion. The wording is stored as published, with the source URL and the section id, under `data/corpus/<section>/`. Those files are a local container for the extract. They are not a rewritten policy. They are ignored by git and are not pushed, published, or resold. The repository holds metadata under `data/metadata/` and the questions written from the pages. Each citation names the source URL. A cloud copy of the page text is outside this arrangement, so the extracts and the chunks made from them stay on the local machine.

A metadata row records where a document came from:

```json
{
  "section": "referrals_waiting",
  "title": "",
  "url": "",
  "publisher": "",
  "retrieved_at": "",
  "document_type": "guidance"
}
```

`publisher` is the body that issued the page, such as NHS England or the NHS website. `document_type` is `guidance` for this Alpha. A row is written only for a document that is explicitly in the corpus.

## Problem

Patients and healthcare users often need to navigate several pieces of official guidance to understand administrative processes such as appointments, referrals, waiting pathways, records, and test results. Similar terminology occurs across these domains. Unrestricted retrieval can return information from the wrong policy area.

The user is a member of the public seeking information about NHS healthcare administrative processes.

The section is chosen by Deskline. The question is then either answered from that section’s pages, with the passage cited, or stopped. Stopping means a ticket a person can pick up, or a clinical signpost when the question asks for clinical advice.

An answer taken from the wrong section, an answer that is not supported by the chosen section’s pages, a guessed section when the question does not clearly belong to one section, and any clinical advice are treated as failure.

## Users and needs

No live patient and no live service is involved. A public information desk is simulated from the approved corpus. The test questions are written from those pages. The human is simulated: the handoff is the ticket stored by Deskline, and that record is read in UAT.

| User | Need | So that |
|---|---|---|
| Member of the public | The question is sent to the section that owns the process | Appointments, Referrals & Waiting, and Records & Results stay separate |
| Member of the public | An answer is taken from that section’s approved pages, and the passage is named | The answer can be checked against the source |
| Member of the public | When the question does not clearly belong to one section, a ticket is opened with no section | A guessed section is not answered, and no policy is stated |
| Member of the public | A handoff is made when that section’s pages do not cover the question | A rule the page does not state is withheld, and the gap is said out loud |
| Member of the public | A request for diagnosis, treatment, or interpretation of symptoms or results is refused | Clinical advice is not given, and the person is directed to a healthcare professional or service |
| Section staff | A ticket shows the question, the section if one was chosen, the passages that were considered, and the reason the system stopped | A reply can be made by a person, and missing answers can be seen |

## The three sections

One simulated desk is covered. Three sections are used.

| Section | Owns | A question that shows the route |
|---|---|---|
| Appointments | Changing or cancelling an appointment, patient choice, and appointment processes | “How can I change my hospital appointment?” This is Appointments. |
| Referrals & Waiting | Referrals, referral pathways, elective care, and waiting processes | “I’ve been referred but haven’t heard anything about my appointment.” This can be Referrals & Waiting or Appointments. |
| Records & Results | Access to health records, online services, and the process of seeing a test result | “My GP referred me for a test and I can’t see the result online.” This can be Referrals & Waiting or Records & Results. |

Words such as “appointment”, “referral”, “result”, “waiting”, “patient”, “GP”, and “hospital” are shared across the pages, and the pages give different processes. That overlap is why a route is required, and why the leak test includes documents that use those words.

A cross-domain question is not answered by merging two corpora. Retrieval uses one section. When more than one section is reasonable, or when none of them is, Deskline opens a ticket with no section.

Two further edges, and one clinical edge:

- A question that belongs to none of the three, such as a job application, is turned into a ticket with no section chosen.
- A question that reaches the right section but is absent from its pages, such as the waiting time at a named hospital when no page states it, is turned into a ticket for that section. Deskline says the guidance it holds is not enough. It does not invent the wait.
- A question that asks for a diagnosis, a treatment, or an interpretation of symptoms or results, such as “What does this test result mean for me?”, is not answered from the policy pages. Deskline gives no clinical advice and directs the person to an appropriate healthcare professional or service, such as their GP, the clinician responsible for their care, or NHS 111.

## What a section is

A section is one policy domain: one set of documents and one ticket queue inside the shared assistant. Deskline is shared by Appointments, Referrals & Waiting, and Records & Results. A corpus is not shared. Every passage and every ticket is stored with that section’s id. Retrieval for a chosen section is filtered by that id. Only documents that have a metadata row in the approved corpus may be retrieved.

## What one request must do

1. **Refuse clinical advice first.** When the question asks for a diagnosis, a treatment, or an interpretation of symptoms or results, Deskline does not retrieve a policy answer and does not advise. It signposts.
2. **Route.** Appointments, Referrals & Waiting, or Records & Results is chosen when one section is clear.
3. **Stop when the route is not one section.** A ticket is opened with no section, and no policy is stated. “I’ve been referred but haven’t heard anything about my appointment” can be a referral, a wait, or an appointment, so it opens that ticket. A question that belongs to none of the three, such as a job application, opens the same kind of ticket. The person is not asked to choose a section.
4. **Retrieve.** After a section is chosen, passages are loaded only for that section, from the local corpus for its documents.
5. **Answer or stop.** Those passages are cited, or a ticket is opened. The question, the section if one was chosen, the passages that were seen, and the reason are recorded on the ticket. The reason is either that the section was not clear, or that the guidance in that section is not sufficient. When the guidance is insufficient, the reply says so.

When the section is already clear, the question is routed and answered. When the chosen section’s pages do not cover the question, a ticket is opened for that section. The person is not asked to supply the missing rule.

## Acceptance criteria

These rules are run in UAT. Solved is defined by them. They are healthcare rules. They are not the previous retail rules with the names changed.

**A1 — Correct domain.** A question about appointments is not answered using evidence that comes only from Referrals & Waiting or Records & Results. The same holds for each section. On the golden set, the route matches the section label written in advance. A question whose section is already clear is routed and answered.

**A2 — Evidence required.** Every substantive answer contains evidence from material retrieved for that question.

**A3 — Traceability.** The answer identifies the source document, by its URL, that supports its claims.

**A4 — Unsupported information.** When the corpus does not contain enough information, Deskline does not invent an answer.

**A5 — Ambiguity.** When the question could reasonably belong to more than one section, Deskline opens a ticket with no section. The reply states no policy and contains no citation.

**A6 — No section.** When the question belongs to none of the three sections, Deskline opens a ticket with no section and no policy statement. The person is not asked to choose a section.

**A7 — Cross-domain leakage.** Retrieval for one section does not silently use documents that belong to another section. This is checked directly by the leak test, on every directed pair of sections.

**A8 — Clinical advice.** When the user asks for a diagnosis, a treatment, or an interpretation of symptoms or results, Deskline does not provide clinical advice. It directs the user toward an appropriate healthcare professional or service.

**A9 — Approved corpus.** Only documents explicitly included in the Deskline corpus are used to answer policy questions.

**A10 — Uncertainty.** When the available guidance is insufficient, Deskline says so. It does not present an uncertain answer as established policy.

## Evaluation rules

These bind the criteria above. The measures themselves are specified in [evaluation.md](evaluation.md).

- About twenty questions are held in the golden set. They are written from the approved pages before any model output is inspected, then left fixed. The set includes questions whose correct behaviour is not an answer: clear routes, ambiguous routes, cross-domain routes, answerable questions, unsupported questions, escalations, and clinical-boundary questions.
- On the cases that should be answered, RAGAS faithfulness is at least 0.8. The bar is set before tuning. If it is missed by the first honest run, UAT is failed and the Alpha is continued. The bar is not moved to match the score.
- Routing accuracy and the unsupported-answer rate are recorded on that same run. An escalation case is judged by whether Deskline refused or escalated, not by how fluent an invented answer was.
- A before-and-after score is produced when that same frozen set is run again after a change to routing, chunking, or retrieval.

## Scope

**In scope**

- A learning simulation. Three sections: Appointments, Referrals & Waiting, and Records & Results.
- A small approved corpus, about five to ten official documents or pages in each section, with a metadata row for each document.
- A text question is received. A cited answer, a ticket, or a clinical signpost is returned.
- A section is routed to, then retrieval is limited to that section’s id.
- A reason is recorded on every ticket. Insufficient guidance is stated as insufficient.
- A repeatable eval is kept, in the order in [evaluation.md](evaluation.md): routing accuracy, retrieval correctness, faithfulness, citation correctness, unsupported-question handling, and cross-domain leakage.
- The same application shape is run under Docker on the local machine. Azure is the later home of that shape, after local UAT, and it does not receive a copy of the policy pages.
- The listed pages are extracted once into gitignored files under `data/corpus/`.

**Out of scope**

- Diagnosis, interpretation of symptoms or results, treatment recommendations, patient-specific clinical advice, and clinical decisions.
- Any presentation of this assistant as an NHS service, as commissioned work, or as a clinical decision-support system.
- Healthcare domains outside these three sections.
- A second organisation, payments, patient accounts, and a full staff inbox.
- Email, phone, or a chat widget. One text interface is used.
- Training or fine-tuning of a model. The model is a replaceable component.
- Languages other than English.
- Real patient data.
- Kubernetes. Container Apps is the rollout target.
- Publication or resale of the extracted pages, including a page-text file committed to git or a copy uploaded to Azure.
- Answering a policy question from a document that is not in the approved corpus.

## Constraints

**From the problem**

- The corpus is the official pages chosen for the three sections, extracted once into unmodified files under `data/corpus/`. Questions and citations are traced to those pages. Metadata for each document is kept under `data/metadata/`.
- That extract, and any chunks made from it, are kept on the local machine and excluded from the repository.
- The chat model and the embedding model can be replaced. Their keys are kept outside the code. The route, the clinical refusal, and the stop decision are owned by the graph.
- The acceptance rules are passed under Docker on the local machine before any Azure spend is made.

**From the role being rehearsed**

The build is constrained by the following. They are separate from the domain.

- Loading, splitting, embedding, and retrieval are done with LangChain.
- The decisions are owned by LangGraph: refuse clinical advice, route, retrieve, grade, generate, check, escalate.
- Groundedness is measured repeatedly with RAGAS. Faithfulness of at least 0.8 is the bar.
- The local runtime is Docker. After local UAT, the application shape can be rolled out to Azure Container Apps, Azure Database for PostgreSQL, and Key Vault. The policy extracts are not part of that upload.

## Risks

| Risk | How it will be noticed |
|---|---|
| The question is sent to the wrong section | The route does not match the golden-set label, or the citation is taken from another section |
| A section is chosen when the question is still ambiguous | An ambiguous case is returned with a citation instead of a ticket with no section |
| Two sections are silently merged | A cross-domain question is answered from more than one section’s documents |
| The person is asked to choose a section | The reply is a question instead of a ticket |
| A policy is stated when the section was not clear | The ticket for an unclear question contains a rule from the pages |
| A rule that is not in the passage is added to the answer | Faithfulness drops, or a UAT case has no valid citation |
| A passage from another section is retrieved | A foreign section id is returned by the leak test |
| A question that the page does answer is escalated by the right section | A “should answer” case becomes a ticket |
| A question that the page does not cover is answered by the right section | A “should escalate” case states a wait, a step, or a rule that is not on the page |
| Insufficient guidance is stated as if it were policy | The reply does not say that the corpus is insufficient |
| Clinical advice is given | A diagnosis, treatment, or result interpretation appears in the reply |
| A document outside the approved corpus is used | The citation URL has no metadata row |
| The golden set is edited after model answers have been seen | The pages stop being what the score measures. The set is written from the pages first and left fixed while tuning is done |
| The page text is committed or uploaded | An extract appears in git, or the page text is written to Azure |
| The extracted pages are rewritten | The stored text differs from the public page |
| The UAT script is missing one of the endings | A correct route, a citation, a ticket, or a clinical signpost cannot be shown |

## Assumptions closed

- The user is simulated. The user is a member of the public. The sections are Appointments, Referrals & Waiting, and Records & Results.
- Deskline is not commissioned by or affiliated with the NHS, and it is not a clinical decision-support system.
- The source pages remain on the publisher’s website. One unmodified personal copy is kept in gitignored files on this machine. Metadata is kept in the repository. About twenty golden questions are written from those pages after the corpus exists, and before any model output is inspected.
- A person is represented by a ticket row that can be read.
- English only is used.
- The first interface is an API or a single plain page.
- One request carries one question. Deskline answers it or opens a ticket. It does not ask the person to choose a section.
- The model can be replaced. The experiment is the route, the constrained retrieval, the evidence, and the decision to answer or escalate.

## Handoff to Alpha

The shape to be built is drawn in [alpha.md](alpha.md): a context view, a container view, and one sequence of a question. How it is built, and in which order, is in [alpha_build.md](alpha_build.md). How it is scored is in [evaluation.md](evaluation.md).

The corpus is gathered before application code is written. A thin Deskline may then be built for these three sections. Clinical advice is refused by the graph. A section is routed to when it is clear, and a ticket is opened when it is not. Retrieval uses that section’s id, and a citation is returned or a ticket is opened with a reason. Local UAT is the route labels, the unclear-section tickets, the clinical-boundary cases, the leak test, and one RAGAS run on the frozen golden set. Azure is deferred until that UAT has been passed, and the page text is not included in that deployment.

Discovery is closed on these findings. The domain is not reopened. The next work is the corpus, then the code.
