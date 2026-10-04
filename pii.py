"""PII detection, masking, simulated LLM and re-hydration (pure Python, regex based)."""
import re

SAMPLE = ("Hi, I'm Priya Sharma. Please draft a polite follow-up to Rahul Mehta "
          "(rahul.mehta@acme.io, +91 98765 43210) about invoice #4412. Charge it to my card "
          "4111 1111 1111 1111 and call me back at (415) 555-0132.")

STOP = set("Hi Hello Dear Please Thanks Thank Send Email Call Draft Write Hey Regards Best Subject "
           "Invoice Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March "
           "April May June July August September October November December".split())

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

def not_common_words(m: str) -> bool:
    return not any(w in STOP for w in m.split())

# Order matters: specific patterns run before looser ones (card/SSN before phone).
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
    dict(id="name", label="Names", tag="NAME", icon="user", on=False,
         re=re.compile(r"\b(?:(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+)?[A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,})+\b"),
         validate=not_common_words),
]

def sanitize(text: str, enabled: dict) -> dict:
    mapping, seen, counts = {}, {}, {}   # token->original, original->token, per-tag counters
    safe = text
    for c in CATS:
        if not enabled.get(c["id"]):
            continue
        def swap(m, c=c):
            val = m.group(0)
            if c.get("validate") and not c["validate"](val):
                return val
            if val in seen:                      # same value -> same token
                return seen[val]
            counts[c["tag"]] = counts.get(c["tag"], 0) + 1
            token = f"<{c['tag']}_{counts[c['tag']]}>"
            seen[val], mapping[token] = token, val
            return token
        safe = c["re"].sub(swap, safe)
    return {"safe": safe, "map": mapping, "total": len(mapping)}

def fake_llm(mapping: dict) -> str:
    """Stand-in model: it only ever sees tokens, and answers using them."""
    toks = list(mapping)
    pick = lambda tag: [t for t in toks if t.startswith(f"<{tag}_")]
    names, emails, phones, cards = pick("NAME"), pick("EMAIL"), pick("PHONE"), pick("CARD")
    if not toks:
        return ("Thanks for your message. I didn't see any personal details in it, so there is "
                "nothing to protect here. Tell me what you'd like drafted and I'll get started.")
    lines = [f"Hello {(names[1:2] or names[:1] or ['there'])[0]},", "",
             "Thanks for your time earlier. Here's a short follow-up you can send as is:"]
    if emails: lines += ["", f"I'll send the written summary to {emails[-1]} today."]
    if cards:  lines.append(f"The payment on file ({cards[0]}) will be charged once you confirm.")
    if phones: lines.append(f"If anything is unclear, call {phones[-1]} and we'll sort it out.")
    lines += ["", "Kind regards,", (names[:1] or ["Your assistant"])[0]]
    return "\n".join(lines)

def rehydrate(raw: str, mapping: dict) -> str:
    return re.sub(r"<[A-Z]+_\d+>", lambda m: mapping.get(m.group(0), m.group(0)), raw)
