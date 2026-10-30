# Evals

| Set | Measures |
|---|---|
| `retrieval_cases.yaml` | Hit@3 and MRR for 50 questions with expected documents. Scored by `python evals/run_retrieval.py` |
| `router_cases.yaml` | Intent accuracy on 40 questions, the set the router rules were tuned on. Scored by `python evals/run_router.py` |
| `router_heldout.yaml` | Intent accuracy on 27 questions written before the router and never used to tune it, including requests to assign, provision and change an owner |
| `skills/<name>.yaml` | Whether each skill triggers on the right requests and not on others |
| `context_ab/` | The same questions answered with and without the context layer (design and questions; no run yet) |

Targets are in [docs/standards/rag.md](../docs/standards/rag.md).
