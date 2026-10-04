import re
from flask import Flask, render_template, request, jsonify
from markupsafe import Markup, escape
import pii, content

app = Flask(__name__)


def load_ner():
    """Load the Hugging Face XLM-RoBERTa NER pipeline once, on the best device available."""
    try:
        import torch
        from transformers import pipeline
        if torch.backends.mps.is_available():
            device, label = "mps", "Apple Silicon (MPS)"
        elif torch.cuda.is_available():
            device, label = 0, "CUDA GPU"
        else:
            device, label = -1, "CPU"
        pipe = pipeline("token-classification", model=pii.NER_MODEL,
                        aggregation_strategy="simple", device=device)
        pipe("Warm up: Priya Sharma works at Acme in Pune.")   # first call is slow; pay it at startup
        print(f"[privacy-guard] NER ready: {pii.NER_MODEL} on {label}")
        return pipe
    except Exception as ex:   # server still runs, regex categories keep working
        print(f"[privacy-guard] NER unavailable ({ex}). Names, organisations and locations are disabled.")
        return None


pii.set_ner(load_ner())       # global: loaded once at startup, shared by every request


@app.template_filter("chips")
def chips(text):
    """Escape text and wrap <TAG_n> tokens in coloured chips."""
    out = []
    for part in re.split(r"(<[A-Z]+_\d+>)", text):
        m = re.fullmatch(r"<([A-Z]+)_\d+>", part)
        out.append(Markup(f'<span class="chip t-{m.group(1)}">{escape(part)}</span>') if m else escape(part))
    return Markup("").join(out)


def read_request():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))[:5000]
    f = data.get("filters") or {}
    enabled = {c["id"]: bool(f.get(c["id"], c["on"])) for c in pii.CATS}
    watch = data.get("watchlist") if isinstance(data.get("watchlist"), list) else []
    return text, enabled, pii.clean_watchlist(watch)


@app.get("/")
def home():
    return render_template("app.html", c=content, cats=pii.CATS, sample=pii.SAMPLE, ner=pii.ner_ready())


@app.get("/website")
def website():
    on = {c["id"]: True for c in pii.CATS}
    example = pii.sanitize(pii.SAMPLE, on, ["Project Falcon"])["safe"]
    return render_template("website.html", c=content, sample=pii.SAMPLE, example=example)


@app.post("/api/sanitize")
def api_sanitize():
    text, enabled, watch = read_request()
    r = pii.sanitize(text, enabled, watch)
    return jsonify(safe=r["safe"], total=r["total"], spans=r["spans"], ner=pii.ner_ready())


@app.post("/api/send")
def api_send():
    text, enabled, watch = read_request()
    r = pii.sanitize(text, enabled, watch)     # 1. mask
    raw = pii.fake_llm(r["map"])               # 2. the "model" only sees tokens
    return jsonify(raw=raw, restored=pii.rehydrate(raw, r["map"]), map=r["map"])  # 3. restore


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)    # reloader would load the model twice