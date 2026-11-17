// The page builds every element with textContent, never innerHTML, so nothing the server
// or the data returns can run as code in the browser.
const thread = document.getElementById("thread");
const form = document.getElementById("ask");
const input = document.getElementById("question");

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}

function table(rows) {
  const t = el("table", undefined, "trace");
  for (const [label, value] of rows) {
    const tr = el("tr");
    tr.append(el("th", label), el("td", value));
    t.append(tr);
  }
  return t;
}

// The rows the query returned, drawn as a table with a header, so numbers are read in columns.
function dataTable(result) {
  const t = el("table", undefined, "data");
  const head = el("tr");
  for (const column of result.columns) head.append(el("th", column));
  t.append(head);
  for (const row of result.rows) {
    const tr = el("tr");
    for (const value of row) tr.append(el("td", value));
    t.append(tr);
  }
  return t;
}

// The answer arrives as paragraphs; the demo label and the suggested next question get their own style.
function answerBlock(text) {
  const block = el("div", undefined, "answer");
  for (const paragraph of String(text).split("\n\n")) {
    let kind;
    if (paragraph.startsWith("Demo answer:")) kind = "note";
    else if (paragraph.startsWith("Next you could ask")) kind = "next";
    block.append(el("p", paragraph, kind));
  }
  return block;
}

// The route at a glance: what the router decided and what was used, before the full trace.
function pills(data) {
  const box = el("div", undefined, "pills");
  const items = [["intent", data.route.intent], ["tier", data.route.tier],
    ["tools", data.tools_called.join(", ") || "none"], ["decided by", data.route.via]];
  for (const [label, value] of items) {
    const pill = el("span", undefined, "pill");
    pill.append(el("b", label), document.createTextNode(String(value)));
    box.append(pill);
  }
  return box;
}

function trace(data) {
  const details = el("details");
  details.append(el("summary", "How the agent got here"));
  const r = data.route;
  details.append(table([
    ["Conversation title", data.title],
    ["Intent", `${r.intent} (decided by ${r.via}: ${r.reason})`],
    ["Model tier", `${r.tier}, ${r.model}, budget of ${r.budget} tool calls`],
    ["Tools offered", r.tools.join(", ") || "none"],
    ["Documents always loaded", r.fixed_docs.join(", ") || "none"],
    ["Skill", r.skill || "none"],
    ["Prompt blocks", data.prompt_blocks.map((b, i) => `${i + 1}: ${b.chars} chars${b.cached ? " (cached)" : ""}`).join("; ")],
    ["Tools called", data.tools_called.join(", ") || "none"],
    ["Model calls", data.model_calls.length ? data.model_calls.map((c) => `${c.model} offered [${c.tools.join(", ")}]`).join("; ") : "none"],
    ["Mode", data.mode === "demo" ? "demo: scripted model, real route, prompt and tools" : "real model"],
  ]));
  return details;
}

async function ask(question) {
  const turn = el("section", undefined, "turn");
  turn.append(el("div", question, "question"));
  thread.append(turn);
  form.querySelector("button").disabled = true;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    if (!response.ok) {
      turn.append(el("div", data.error || "The request was refused.", "answer error"));
    } else {
      turn.append(pills(data), answerBlock(data.answer));
      if (data.table && data.table.rows.length) turn.append(dataTable(data.table));
      turn.append(trace(data));
    }
  } catch (error) {
    turn.append(el("div", "The local server did not answer. Is it running?", "answer error"));
  } finally {
    form.querySelector("button").disabled = false;
    turn.scrollIntoView({ behavior: "smooth" });
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (question) ask(question);
  input.value = "";
});

for (const button of document.querySelectorAll(".example")) {
  button.addEventListener("click", () => ask(button.textContent));
}

fetch("/api/health").then((r) => r.json()).then((h) => {
  if (h.mode === "model") document.getElementById("mode").textContent = "Model mode: answers come from a real model";
});
