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
  const t = el("table");
  for (const [label, value] of rows) {
    const tr = el("tr");
    tr.append(el("th", label), el("td", value));
    t.append(tr);
  }
  return t;
}

function trace(data) {
  const details = el("details");
  details.append(el("summary", "How the agent got here"));
  const r = data.route;
  details.append(table([
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
      turn.append(el("div", data.answer, "answer"), trace(data));
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
  if (h.mode === "model") document.getElementById("mode").textContent = "Model mode: answers come from a real model.";
});
