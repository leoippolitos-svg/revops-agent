# Evals

| Set | Measures |
|---|---|
| `retrieval_cases.yaml` | Hit@3 and MRR for 50 questions with expected documents. Scored by `python evals/run_retrieval.py` |
| `router_cases.yaml` | Intent accuracy |
| `skills/<name>.yaml` | Whether each skill triggers on the right requests and not on others |
| `context_ab/` | The same questions answered with and without the context layer (design and questions; no run yet) |

Targets are in [docs/standards/rag.md](../docs/standards/rag.md).
