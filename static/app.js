const $ = (s) => document.querySelector(s);
const filters = {};
const post = (url, body) =>
  fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then((r) => r.json());

// Renders text into `el`, turning <TAG_n> tokens into chips. Uses textContent only, so input is never parsed as HTML.
function render(el, text, show = (t) => t) {
  el.replaceChildren();
  text.split(/(<[A-Z]+_\d+>)/).forEach((p) => {
    const m = p.match(/^<([A-Z]+)_\d+>$/);
    if (!m) return el.append(document.createTextNode(p));
    const s = document.createElement("span");
    s.className = "chip t-" + m[1]; s.title = p; s.textContent = show(p);
    el.append(s);
  });
}

let timer, seq = 0;
function refresh() {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    const id = ++seq, text = $("#prompt").value;
    const d = await post("/api/sanitize", { text, filters });
    if (id !== seq) return;                      // ignore out-of-order replies
    const box = $("#safe");
    if (!text.trim()) { box.innerHTML = '<p class="hint">The masked version of your prompt appears here as you type.</p>'; }
    else render(box, d.safe);
    $("#count").textContent = `${d.total} ${d.total === 1 ? "value" : "values"} masked`;
  }, 120);
}

document.querySelectorAll(".tog").forEach((b) => {
  filters[b.dataset.id] = b.getAttribute("aria-checked") === "true";
  b.addEventListener("click", () => {
    const on = b.getAttribute("aria-checked") !== "true";
    b.setAttribute("aria-checked", on); filters[b.dataset.id] = on; refresh();
  });
});
$("#prompt").addEventListener("input", refresh);
$("#clear").addEventListener("click", () => { $("#prompt").value = ""; refresh(); });

$("#send").addEventListener("click", async () => {
  const text = $("#prompt").value, btn = $("#send");
  if (!text.trim() || btn.disabled) return;
  btn.disabled = true; btn.classList.add("busy"); $("#sendlabel").textContent = "Sending masked prompt";
  $("#idle").hidden = true; $("#result").hidden = true; $("#wait").hidden = false;
  const [d] = await Promise.all([post("/api/send", { text, filters }), new Promise((r) => setTimeout(r, 1200))]);
  render($("#raw"), d.raw);
  render($("#restored"), d.raw, (t) => d.map[t] ?? t);
  $("#wait").hidden = true; $("#result").hidden = false;
  btn.disabled = false; btn.classList.remove("busy"); $("#sendlabel").textContent = "Send to LLM";
});
refresh();
