const $ = (s) => document.querySelector(s);
const filters = {};
const watchlist = [];
let spans = [], lastSafe = "";
const post = (url, body) =>
  fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then((r) => r.json());

// Renders text into `el`, turning <TAG_n> tokens into chips. Uses textContent only, so input is never parsed as HTML.
function render(el, text, show = (t) => t) {
  el.replaceChildren();
  text.split(/(<[A-Z]+_\d+>)/).forEach((p) => {
    const m = p.match(/^<([A-Z]+)_\d+>$/);
    if (!m) return el.append(document.createTextNode(p));
    const s = document.createElement("span");
    s.className = "chip t-" + m[1]; s.title = p; s.dataset.token = p; s.textContent = show(p);
    el.append(s);
  });
}

/* ---- Synchronized hover: mirror layer sits behind the textarea and paints <mark> over the original text ---- */
const prompt_ = $("#prompt"), mirror = $("#mirror");
function paintMirror(token) {
  const text = prompt_.value;
  mirror.replaceChildren();
  let pos = 0;
  if (token) {
    spans.filter((s) => s.token === token && s.end <= text.length).forEach((s) => {
      mirror.append(document.createTextNode(text.slice(pos, s.start)));
      const mk = document.createElement("mark");
      mk.textContent = text.slice(s.start, s.end);
      mirror.append(mk); pos = s.end;
    });
  }
  mirror.append(document.createTextNode(text.slice(pos) + "\n"));
  mirror.scrollTop = prompt_.scrollTop;
}
prompt_.addEventListener("scroll", () => { mirror.scrollTop = prompt_.scrollTop; });
$("#safe").addEventListener("mouseover", (e) => { const c = e.target.closest(".chip"); if (c) paintMirror(c.dataset.token); });
$("#safe").addEventListener("mouseout", (e) => { if (e.target.closest(".chip")) paintMirror(null); });

let timer, seq = 0;
function refresh() {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    const id = ++seq, text = prompt_.value;
    let d;
    try { d = await post("/api/sanitize", { text, filters, watchlist }); }
    catch { $("#safe").innerHTML = '<p class="hint">Could not reach the server. Check that app.py is running.</p>'; return; }
    if (id !== seq) return;                      // ignore out-of-order replies
    spans = d.spans; lastSafe = d.safe;
    const box = $("#safe");
    if (!text.trim()) { box.innerHTML = '<p class="hint">The masked version of your prompt appears here as you type.</p>'; }
    else render(box, d.safe);
    $("#count").textContent = `${d.total} ${d.total === 1 ? "value" : "values"} masked`;
    $("#nernote").hidden = d.ner;
    paintMirror(null);
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
