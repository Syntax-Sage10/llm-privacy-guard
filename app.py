import re
from flask import Flask, render_template, request, jsonify
from markupsafe import Markup, escape
import pii, content

app = Flask(__name__)

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
    return text, {c["id"]: bool(f.get(c["id"], c["on"])) for c in pii.CATS}

@app.get("/")
def home():
    return render_template("app.html", c=content, cats=pii.CATS, sample=pii.SAMPLE)

@app.get("/website")
def website():
    example = pii.sanitize(pii.SAMPLE, {c["id"]: True for c in pii.CATS})["safe"]
    return render_template("website.html", c=content, sample=pii.SAMPLE, example=example)

@app.post("/api/sanitize")
def api_sanitize():
    text, enabled = read_request()
    r = pii.sanitize(text, enabled)
    return jsonify(safe=r["safe"], total=r["total"])

@app.post("/api/send")
def api_send():
    text, enabled = read_request()
    r = pii.sanitize(text, enabled)            # 1. mask
    raw = pii.fake_llm(r["map"])               # 2. the "model" only sees tokens
    return jsonify(raw=raw, restored=pii.rehydrate(raw, r["map"]), map=r["map"])  # 3. restore

if __name__ == "__main__":
    app.run(debug=True)
