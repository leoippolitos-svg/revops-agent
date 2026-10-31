"""A scripted stand-in for the language model, so the chat can be shown with no key.

It implements the same one method as the real adapter, `complete(model, system, messages,
tools)` (agent.ModelClient), so the agent loop, the router, the profiles, the four prompt
blocks, the budget and the real read-only tools all run exactly as they would with a model.
Only the choice of tool and the final wording are scripted:

- on the first call it picks one tool the intent allows, with a fixed query for the topic
  of the question (the model queries of the data map);
- once a tool has answered, it writes a short answer from the real rows, labelled as a demo.

Nothing here pretends to be a model. Every answer says that no language model was called.
"""

import json
import re

# A fixed, read-only query per topic: the "verified queries" a semantic layer would offer.
TOPIC_QUERIES = [
    (r"\bmqls?\b|marketing qualified", "mql",
     "SELECT month, marketing_mqls, sales_mqls FROM gold.mql_monthly ORDER BY month DESC LIMIT 4"),
    (r"\bopen deals?\b|\bowners?\b|\bcapacity\b|\bworkload\b", "owner workload",
     "SELECT team, owner_id, open_deals, open_amount_usd FROM gold.owner_workload ORDER BY open_deals DESC LIMIT 5"),
    (r"conversion|win rate|funnel|stage|cohort", "funnel conversion",
     "SELECT cohort_month, deals_qualified, closed_won, closed_lost, still_open "
     "FROM gold.funnel_conversion_monthly ORDER BY cohort_month DESC LIMIT 4"),
    (r"\bcustomers?\b|active", "active customers",
     "SELECT month, active_customers, active_subscriptions FROM gold.active_customer_monthly ORDER BY month DESC LIMIT 4"),
    (r"quality|duplicate|without a company|don'?t match|mismatch", "data quality",
     "SELECT * FROM gold.data_quality_snapshot"),
]
DEFAULT_QUERY = ("mrr", "SELECT month, new_mrr_usd, churned_mrr_usd, ending_mrr_usd FROM gold.mrr_monthly "
                        "ORDER BY month DESC LIMIT 4")
NEXT_CUTS = {
    "metric_lookup": "by team or by segment?",
    "trend_analysis": "the last 12 months, or only full quarters?",
    "funnel_diagnosis": "only mature cohorts, or by segment?",
    "data_quality": "the list of records behind each flag?",
    "report_request": "as a one-page HTML report?",
    "definition_question": "how Sales and Marketing each use the term?",
    "past_work_lookup": "the full record of that work?",
}
LABEL = "Demo answer: no language model was called. The route, the prompt and the tool result are real."


class DemoModel:
    """Plays the model's part from a script and records every call for the page's trace."""

    def __init__(self):
        self.calls = []

    def complete(self, model, system, messages, tools):
        self.calls.append({"model": model, "tools": [t["name"] for t in tools], "messages": len(messages)})
        text = system if isinstance(system, str) else "\n".join(b["text"] for b in system)
        intent = (re.search(r"routed as `([a-z_]+)`", text) or [None, "metric_lookup"])[1]
        question = messages[0]["content"]
        offered = {t["name"] for t in tools}
        results = [m for m in messages if m["role"] == "tool"]
        usage = {"input_tokens": 0, "output_tokens": 0}  # no model, no tokens: cost stays at zero tokens
        if not results and offered:
            return {"text": None, "tool_call": self._pick_tool(intent, question, offered), "usage": usage}
        return {"text": self._answer(intent, results), "tool_call": None, "usage": usage}

    @staticmethod
    def _pick_tool(intent, question, offered):
        if intent == "past_work_lookup" and "search_records" in offered:
            return {"name": "search_records", "input": {"question": question, "k": 2}}
        if intent == "definition_question" or "query_gold" not in offered:
            return {"name": "search_context", "input": {"question": question, "k": 2}}
        for pattern, _, sql in TOPIC_QUERIES:
            if re.search(pattern, question, re.I):
                return {"name": "query_gold", "input": {"sql": sql}}
        return {"name": "query_gold", "input": {"sql": DEFAULT_QUERY[1]}}

    @staticmethod
    def _answer(intent, results):
        last = results[-1]
        try:
            data = json.loads(last["content"].split(" ... [result cut")[0])
        except ValueError:
            data = {}
        if last.get("is_error") or "error" in data:
            body = f"The {last['name']} call failed: {data.get('error', 'unreadable result')}"
        elif "rows" in data:
            rows = data["rows"][:4]
            cells = "; ".join(", ".join(f"{c}={v}" for c, v in zip(data.get("columns", []), r)) for r in rows)
            body = f"The query returned {data.get('total_rows', data.get('row_count', len(rows)))} row(s). {cells}"
        elif "results" in data:
            found = [f"{r['doc_id']} ({r.get('section') or r.get('title', '')})" for r in data["results"]]
            body = "Most relevant: " + ", ".join(found) if found else "Nothing relevant was found."
        else:
            body = "The tool answered, but with nothing to summarise."
        return f"{LABEL}\n\n{body}\n\nNext you could ask: {NEXT_CUTS.get(intent, 'a narrower question?')}"
