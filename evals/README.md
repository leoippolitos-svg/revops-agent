# Evals

| Set | Measures |
|---|---|
| `retrieval_cases.yaml` | Hit@3 and MRR for 50 questions with expected documents. Scored by `python evals/run_retrieval.py` |
| `router_cases.yaml` | Intent accuracy on 40 questions, the set the router rules were tuned on. Scored by `python evals/run_router.py` |
| `router_heldout.yaml` | Intent accuracy on 27 questions written before the router and never used to tune it, including requests to assign, provision and change an owner |
| `skills/<name>.yaml` | Whether each skill triggers on the right requests and not on others |
| `profile_cases.yaml` | For each question, the intent, the documents loaded and the tools offered, before any model call. Scored by `python evals/run_profiles.py`; deterministic, so the target is every case. It never calls a model and says nothing about answers |
| `context_ab/` | The same questions answered with and without the context layer (design and questions; no run yet) |

Targets are in [docs/standards/rag.md](../docs/standards/rag.md).
