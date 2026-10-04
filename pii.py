"""PII detection, masking, simulated LLM and re-hydration.

Structured data (emails, cards, IDs...) uses regex. People, organisations and
places come from a Hugging Face XLM-RoBERTa NER pipeline injected by app.py.
"""
import re
from functools import lru_cache

SAMPLE = ("Hi, I'm Priya Sharma from Acme Corp in Bengaluru. Please draft a polite follow-up to Rahul Mehta "
          "(rahul.mehta@acme.io, +91 98765 43210) about invoice #4412 and Project Falcon. Charge it to my card "
          "4111 1111 1111 1111 and call me back at (415) 555-0132.")

NER_MODEL = "Davlan/xlm-roberta-base-ner-hrl"   # multilingual XLM-R: PER / ORG / LOC
NER_MIN_SCORE = 0.75
MAX_WATCH, MAX_WATCH_LEN = 50, 80

_ner = None

def set_ner(pipe):
    global _ner
    _ner = pipe
    _ner_spans.cache_clear()

def ner_ready() -> bool:
    return _ner is not None

@lru_cache(maxsize=256)
def _ner_spans(text: str):
    """[(start, end, group)] for PER / ORG / LOC. Cached so live typing stays fast."""
    if _ner is None or not text.strip():
        return ()
    out = []
    for e in _ner(text):
        s, t = e["start"], e["end"]
        while s < t and text[s].isspace():
            s += 1
        while t > s and text[t - 1].isspace():
            t -= 1
        if e["score"] >= NER_MIN_SCORE and t > s:
            out.append((s, t, e["entity_group"]))
    return tuple(out)

def luhn(raw: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", raw)]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, n in enumerate(reversed(digits)):
        if i % 2:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

# Order = priority. Specific patterns win overlaps against looser ones; NER goes last.
CATS = [
    dict(id="email", label="Emails", tag="EMAIL", icon="mail", on=True,
         re=re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    dict(id="card", label="Credit cards", tag="CARD", icon="credit-card", on=True,
         re=re.compile(r"\b(?:\d[ -]?){12,18}\d\b"), validate=luhn),
    dict(id="ssn", label="SSN / national IDs", tag="SSN", icon="fingerprint", on=True,
         re=re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    dict(id="ip", label="IP addresses", tag="IP", icon="globe", on=True,
         re=re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    dict(id="phone", label="Phone numbers", tag="PHONE", icon="phone", on=True,
         re=re.compile(r"(?<!\d)(?:(?:\+\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}"
                       r"|\+91[\s-]?[6-9]\d{4}[\s-]?\d{5}|[6-9]\d{4}[\s-]?\d{5})(?!\d)")),
    dict(id="name", label="Names", tag="NAME", icon="user", on=True, ner="PER"),
    dict(id="org", label="Organisations", tag="ORG", icon="building-2", on=True, ner="ORG"),
    dict(id="loc", label="Locations", tag="LOC", icon="map-pin", on=True, ner="LOC"),
]

def clean_watchlist(items) -> list:
    seen, out = set(), []
    for w in items or []:
        w = str(w).strip()[:MAX_WATCH_LEN]
        if w and w.lower() not in seen:
            seen.add(w.lower())
            out.append(w)
    return out[:MAX_WATCH]

def find_spans(text: str, enabled: dict, watch: list) -> list:
    found = []
    def add(s, e, tag):
        if all(e <= a or s >= b for a, b, _ in found):   # first claim wins
            found.append((s, e, tag))
    for w in sorted(watch, key=len, reverse=True):       # custom keywords: highest priority
        for m in re.finditer(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, re.I):
            add(m.start(), m.end(), "CUSTOM")
    for c in CATS:
        if not enabled.get(c["id"]):
            continue
        if "ner" in c:
            for s, e, g in _ner_spans(text):
                if g == c["ner"]:
                    add(s, e, c["tag"])
        else:
            for m in c["re"].finditer(text):
                if not c.get("validate") or c["validate"](m.group(0)):
                    add(m.start(), m.end(), c["tag"])
    return sorted(found)

def sanitize(text: str, enabled: dict, watch=None) -> dict:
    mapping, seen, counts, spans, out, pos = {}, {}, {}, [], [], 0
    u16 = lambda i: len(text[:i].encode("utf-16-le")) // 2   # JS string offsets
    for s, e, tag in find_spans(text, enabled, clean_watchlist(watch)):
        val = text[s:e]
        key = (tag, val.lower() if tag == "CUSTOM" else val)
        if key not in seen:                               # same value -> same token
            counts[tag] = counts.get(tag, 0) + 1
            seen[key] = f"<{tag}_{counts[tag]}>"
            mapping[seen[key]] = val
        out += [text[pos:s], seen[key]]
        pos = e
        spans.append(dict(token=seen[key], start=u16(s), end=u16(e)))
    out.append(text[pos:])
    return {"safe": "".join(out), "map": mapping, "total": len(mapping), "spans": spans}

def fake_llm(mapping: dict) -> str:
    """Stand-in model: it only ever sees tokens, and answers using them."""
    toks = list(mapping)
    pick = lambda tag: [t for t in toks if t.startswith(f"<{tag}_")]
    names, emails, phones, cards, custom = (pick(t) for t in ("NAME", "EMAIL", "PHONE", "CARD", "CUSTOM"))
    if not toks:
        return ("Thanks for your message. I didn't see any personal details in it, so there is "
                "nothing to protect here. Tell me what you'd like drafted and I'll get started.")
    lines = [f"Hello {(names[1:2] or names[:1] or ['there'])[0]},", "",
             "Thanks for your time earlier. Here's a short follow-up you can send as is:"]
    if custom: lines += ["", f"A quick update on {custom[0]} is attached."]
    if emails: lines += ["", f"I'll send the written summary to {emails[-1]} today."]
    if cards:  lines.append(f"The payment on file ({cards[0]}) will be charged once you confirm.")
    if phones: lines.append(f"If anything is unclear, call {phones[-1]} and we'll sort it out.")
    lines += ["", "Kind regards,", (names[:1] or ["Your assistant"])[0]]
    return "\n".join(lines)

def rehydrate(raw: str, mapping: dict) -> str:
    return re.sub(r"<[A-Z]+_\d+>", lambda m: mapping.get(m.group(0), m.group(0)), raw)