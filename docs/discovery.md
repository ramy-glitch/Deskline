# Discovery findings

The assistant is called Deskline. The company is Halfords. Deskline is a learning simulation. It has not been commissioned by Halfords.

## Source decision

A customer help centre with separate operational rules is published by Halfords. Returns, warranties, and faulty-product aftercare are already separated on its public help pages. Those pages are the corpus.

| Section | Public source |
|---|---|
| Returns | [Returns information](https://www.halfords.com/help-and-advice/orders-and-bookings/returns-and-refunds/returns-information) and the [returns and refunds FAQ](https://www.halfords.com/customer-services/faqs/returns-and-refunds) |
| Warranties | [Warranties](https://www.halfords.com/customer-services/faqs/warranties) |
| Repairs | The after-sales rules on the [returns information](https://www.halfords.com/help-and-advice/orders-and-bookings/returns-and-refunds/returns-information) page, and the after-sales clause in the [terms and conditions](https://www.halfords.com/help-and-advice/customer-services/policies-and-customer-security/terms-and-conditions/terms-and-conditions/terms-and-conditions.html) |

The pages are public to read. Copyright in them is retained by Halfords. Under the [terms of use](https://www.halfords.com/help-and-advice/customer-services/policies-and-customer-security/terms-and-conditions/terms-of-use/terms-of-use.html), extracts may be downloaded for personal use, and the site may not be reproduced or resold outside those terms. The help pages in the table are not disallowed by `robots.txt`. Carts, accounts, search, and checkout are disallowed, and they are left untouched.

The listed pages are scraped once. The policy wording is stored as published, with the source URL and the section id, in JSON files under `data/corpus/`. Those files are a local container for the extract. They are not a rewritten policy. They are ignored by git and are not pushed, published, or resold. The repository holds the URLs and the questions that are written from the pages. Each citation names the source URL. This follows Halfords’ published terms. It is not a legal opinion. A cloud copy of the page text is outside this permission, so the extracts and the chunks that are made from them stay on the local machine.

## Problem

Questions are asked by Halfords customers about rules that have already been published on those pages. The rules belong to different sections, and they are easily mixed up. A change-of-mind return, a fault inside 30 days, and a fault after 30 days are given different endings. A bike frame and a bike component are covered for different lengths of time.

The section is chosen by Deskline. The question is then either answered from that section’s pages, with the passage cited, or handed over as a ticket that can be picked up by a person.

Three outcomes are treated as failure: an answer taken from the wrong section, an answer that is not supported by the chosen section’s pages, and a guessed section when the question does not clearly belong to one section.

## Users and needs

No live client is involved. A Halfords customer-support desk is simulated from the public pages above. The test questions are written from those pages. The human is simulated: the handoff is the ticket that is stored by Deskline, and that record is read in UAT.

| User | Need | So that |
|---|---|---|
| Customer | The question is sent to the section that owns the rule | Returns, Warranties, and Repairs are kept as separate text |
| Customer | An answer is taken from that section’s public page, and the passage is named | The answer can be checked against the site |
| Customer | A clarifying question is asked when the section is unclear | One of the three sections can be named, and no policy is stated in that question |
| Customer | A handoff is made when the section stays unclear, or when that section’s pages do not cover the question | A rule that the page does not state is withheld |
| Section staff | A ticket shows the question, the section if one was chosen, the passages that were considered, and the reason the system stopped | A reply can be made by a person, and missing answers can be seen |

## The company and its sections

One company is covered. Three sections are used. This split is already used on the public pages: warranty and guarantee claims are dealt with in store, and refunds sit on the returns policy. A fault after the change-of-mind window is described as a repair or replacement, which is a different ending from a refund.

| Section | Owns | A question that can be answered from the public pages |
|---|---|---|
| Returns | Change-of-mind returns, the condition of the item, bike refunds, refund timing | “Can I get a full refund on a bike I have already ridden?” A full bike refund is stated by the returns FAQ to require an unused bike, and wear is deducted. |
| Warranties | Standard cover, Halfords bike frame and fork cover, what happens when an item is exchanged under warranty | “I have owned my Carrera for three years and the frame has cracked. Is the frame covered?” A limited lifetime warranty on the frame and rigid forks of Halfords bikes is offered by the warranties page for the original owner. Other components are covered for one year unless another period is stated by the manufacturer. |
| Repairs | A manufacturing fault after 30 days, and a fault that is not a manufacturing fault | “The gears failed four months after I bought the bike. Do you repair it or refund it?” After 30 days, a manufacturing fault is handled as a repair and/or replacement. A fault that is not a manufacturing fault can be offered as a chargeable repair. |

Words such as “30 days”, “fault”, “refund”, and “bike” are shared by the pages, and different outcomes are given. That overlap is the reason a route is required.

Two further cases define the edges:

- A question that belongs to none of the three, such as a job application, is turned into a ticket with no section chosen.
- A question that reaches the right section but is absent from its pages, such as the cost of a particular chargeable repair, is turned into a ticket for that section. A chargeable repair is said to be available. A price is not stated.

## What a section is

A section is one set of pages and one ticket queue inside the shared assistant. Deskline is shared by Returns, Warranties, and Repairs. A corpus is not shared. Every passage and every ticket is stored with that section’s id. Retrieval for a chosen section is filtered by that id.

## What one request must do

1. **Route.** Returns, Warranties, or Repairs is chosen when one section is clear.
2. **Ask once, when the route is not clear.** The three sections are named by the clarifying question, and no policy is stated. A customer who says “the bike is damaged, what can you do?” is asked whether this is a return, a warranty claim, or a repair. One clarifying question is the limit.
3. **Retrieve.** After a section is chosen, passages are loaded only for that section, from the local JSON for its pages.
4. **Answer or stop.** Those passages are cited, or a ticket is opened. The question, the section if one was chosen, the passages that were seen, and the reason are recorded on the ticket. The reason is either that the section was still unclear after the customer replied, or that an answer is not supported by the section’s pages.

A second unclear reply is turned into a ticket with no section. A further question is not asked.

When the section is already clear, the question is routed immediately and no clarifying question is asked. When the chosen section’s pages do not cover the question, a ticket is opened for that section. The customer is not asked to supply the missing rule.

## Success criteria

These rules are run in UAT. Solved is defined by them.

1. Every golden-set question that belongs to a section is labeled with that section in advance. The label is matched by Deskline’s route.
2. An in-policy question is returned as an answer with at least one citation from the routed section’s public page.
3. An ambiguous question is returned as one clarifying question, with no citation and no ticket.
4. After a scripted reply in which one section is named, that section is matched by the route.
5. After a reply in which a section is still not named, a ticket is returned with no section and no policy statement.
6. A question whose section is already clear is routed immediately, and no clarifying question is asked.
7. A question that belongs to a section, but whose answer is not on that section’s pages, is returned as a ticket for that section, with no policy statement.
8. No passage from another section is returned by retrieval for the chosen section. This is checked directly by a leak test.
9. About twenty questions are held in the golden set. They are written from the public pages before any model output is inspected. Route-and-answer cases, ambiguous two-turn cases, and both kinds of escalation are included. On the cases that should be answered, RAGAS faithfulness is at least 0.8. The escalation cases are escalated.
10. A before-and-after score is produced when that same frozen set is run again after a change to routing, chunking, or retrieval.

The 0.8 bar is set before tuning. If it is missed by the first honest run, UAT is failed and the Alpha is continued. The bar is not moved to match the score.

## Scope

**In scope**

- One company, Halfords, and three sections: Returns, Warranties, and Repairs.
- A text question is received. A cited answer, one clarifying question, or a ticket is returned.
- A section is routed to, then retrieval is limited to that section’s id.
- A reason is recorded on every ticket.
- A repeatable eval is kept: route accuracy against the labels, plus RAGAS faithfulness and context precision.
- The same application shape is run under Docker on the local machine. Azure is the later home of that shape, after local UAT, and it does not receive a copy of the Halfords pages.
- The listed help pages are scraped once, for personal use, into gitignored JSON under `data/corpus/`.

**Out of scope**

- Halfords teams that sit outside these pages, including Motoring Club, autocentres, and breakdown cover.
- A second company, payments, customer accounts, and a full staff inbox.
- Email, phone, or a chat widget. One text interface is used.
- Training or fine-tuning of a model.
- Languages other than English.
- Real customer data, or the corpus from the dissertation.
- Kubernetes. Container Apps is the rollout target.
- Any presentation of this assistant as an official Halfords service.
- Publication or resale of the scraped pages, including a JSON file committed to git or a copy uploaded to Azure.
- Paths disallowed by `robots.txt`, including carts, accounts, search, and checkout.

## Constraints

**From the problem**

- The corpus is the public Halfords URLs in the table above, scraped once into unmodified JSON under `data/corpus/`. Questions and citations are traced to those pages.
- That JSON, and any chunks made from it, are kept on the local machine and excluded from the repository.
- The chat model and the embedding model can be replaced. Their keys are kept outside the code. The route, the one clarifying question, and the stop decision are owned by the graph.
- The acceptance rules are passed under Docker on the local machine before any Azure spend is made.

**From the role being rehearsed**

The build is constrained by the following. They are separate from the client problem.

- Loading, splitting, embedding, and retrieval are done with LangChain.
- The decisions are owned by LangGraph: route, ask the customer once, retrieve, grade, generate, check, escalate.
- Groundedness is measured repeatedly with RAGAS.
- The local runtime is Docker. After local UAT, the application shape can be rolled out to Azure Container Apps, Azure Database for PostgreSQL, and Key Vault. The Halfords extracts are not part of that upload.

## Risks

| Risk | How it will be noticed |
|---|---|
| The question is sent to the wrong section | The route does not match the golden-set label, or the citation is taken from another section |
| A section is chosen when the question is still ambiguous | An ambiguous case is returned with a citation or a ticket instead of one clarifying question |
| A second question is asked | A two-turn case that stays unclear produces another question instead of a ticket |
| A policy is stated by the clarifying question | The first reply on an ambiguous case contains a rule from the pages |
| A rule that is not in the passage is added to the answer | Faithfulness drops, or a UAT case has no valid citation |
| A passage from another section is retrieved | A foreign section id is returned by the leak test |
| A question that the page does answer is escalated by the right section | A “should answer” case becomes a ticket |
| A question that the page does not cover is answered by the right section | A “should escalate” case states a price, a time, or a rule that is not on the page |
| The golden set is edited after model answers have been seen | The pages stop being what the score measures. The set is written from the pages first and left fixed while tuning is done |
| The Halfords text is committed or uploaded | A JSON file appears in git, or the page text is written to Azure |
| The scraped pages are rewritten | The JSON text differs from the public page |
| The UAT script is missing one of the four endings | A correct route, a citation, a clarifying question, or a ticket cannot be shown |

## Assumptions closed

- The client is simulated. The company is Halfords. The sections are Returns, Warranties, and Repairs.
- The source pages remain on Halfords’ website. One unmodified personal copy is kept in gitignored JSON on this machine. About twenty golden questions are written from those pages.
- A person is represented by a ticket row that can be read.
- English only is used.
- The first interface is an API or a single plain page.
- One clarifying question is the maximum.

## Handoff to Alpha

The shape to be built is drawn in [alpha.md](alpha.md): a context view, a container view, and one sequence of a question. A thin Deskline may then be built for Halfords’ three public sections. A section is routed to by the graph, the customer is asked once when the route is unclear, retrieval uses that section’s id, and a citation is returned or a ticket is opened with a reason. Local UAT is the route labels, the two-turn clarifying cases, the leak test, and one RAGAS run on the frozen golden set. Azure is deferred until that UAT has been passed, and the Halfords text is not included in that deployment.

Discovery is closed on these findings.
