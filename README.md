# Deskline

Deskline is a learning simulation of a healthcare policy-navigation assistant. It is not commissioned by or affiliated with the NHS, and it is not a clinical decision-support system.

It demonstrates domain routing, constrained retrieval, citation-grounded answers, uncertainty handling, and human escalation on a small approved policy corpus. It does not diagnose, interpret symptoms, recommend treatment, give patient-specific clinical advice, replace clinicians, or make clinical decisions.

> Can Deskline route a question to the correct healthcare-policy domain and produce a cited answer grounded only in the appropriate evidence, while refusing or escalating when the evidence is insufficient?

The three sections are Appointments, Referrals & Waiting, and Records & Results. The architecture is a LangGraph application behind FastAPI, with PostgreSQL and pgvector, LangChain, a local model through Ollama, and RAGAS. The model is a component. The experiment is the orchestration.

## Documents

| Document | What it closes |
|---|---|
| [docs/discovery.md](docs/discovery.md) | The problem, the three sections, and acceptance criteria A1–A10. Discovery is closed. |
| [docs/alpha.md](docs/alpha.md) | Who uses Deskline, what is deployed, and what happens to one question. |
| [docs/alpha_build.md](docs/alpha_build.md) | Which component does each job, which library is used, and the build order. |
| [docs/evaluation.md](docs/evaluation.md) | Routing accuracy, faithfulness, citations, unsupported questions, and the leak test. |

## Layout

```text
deskline/
├── docs/
│   ├── discovery.md
│   ├── alpha.md
│   ├── alpha_build.md
│   └── evaluation.md
├── src/deskline/          # not created yet
│   ├── api/
│   ├── router/
│   ├── retrieval/
│   ├── generation/
│   ├── escalation/
│   └── evaluation/
├── tests/                 # not created yet
│   ├── routing/
│   ├── retrieval/
│   ├── leakage/
│   └── uat/
├── data/
│   ├── corpus/            # gitignored extracts
│   │   ├── appointments/
│   │   ├── referrals_waiting/
│   │   └── records_results/
│   └── metadata/          # provenance, committed
├── eval/golden.json       # not created yet
├── compose.yaml           # not created yet
└── pyproject.toml         # not created yet
```

Application code is not written yet. The corpus is gathered first. Raw page text stays in `data/corpus/` and is gitignored. `data/metadata/` records the publisher, URL, section, and retrieval date for each approved document.

## Build order

The order is in [docs/alpha_build.md](docs/alpha_build.md): corpus, minimal cited answers, routing, escalation, isolation, evaluation, Docker UAT, then Azure. UAT is passed on this machine before any cloud rollout. The page text is not part of that rollout.
