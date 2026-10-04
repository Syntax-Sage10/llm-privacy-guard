TAGLINE = "Your prompt, minus the personal details."
SUBTITLE = ("Privacy Guard hides names, emails, phone numbers and card numbers before a prompt "
            "reaches an AI model, then puts them back in the answer.")

STEPS = [
    dict(icon="scan-search", title="Find personal data",
         body="Pattern matching scans your prompt for emails, phone numbers, cards, IDs, IP addresses and, optionally, names."),
    dict(icon="eye-off", title="Swap in placeholders",
         body="Each value becomes a token such as <EMAIL_1>. The same value always gets the same token, so the model can still follow who is who."),
    dict(icon="send", title="Send the safe version",
         body="Only the masked prompt goes to the model. The server keeps the real values and never forwards them."),
    dict(icon="undo-2", title="Restore the answer",
         body="When the reply comes back, every token is swapped for the original value, so the answer reads naturally."),
]
FEATURES = [
    dict(icon="server", title="Python backend", body="Detection, masking and restoring run in Flask, so the rules live in one place."),
    dict(icon="link-2", title="Consistent tokens", body="Repeated values reuse one token, so context survives masking."),
    dict(icon="badge-check", title="Cards are checked", body="Card numbers must pass the Luhn check, so order numbers are left alone."),
    dict(icon="sliders-horizontal", title="You choose the filters", body="Turn each category on or off and watch the safe payload update as you type."),
]
LIMITS = ("This is a demonstration. The model reply is simulated, and detection uses regular expressions, "
          "so unusual formats and names can be missed. For production use, add a trained entity-recognition "
          "model and authentication.")
FAQ = [
    dict(q="Does my text go to a real model?", a="No. The reply is generated locally by a stand-in function. Swap fake_llm() in pii.py for a real API call to use a live model."),
    dict(q="Why are names off by default?", a="Names are hard to spot with patterns. The detector looks for capitalised word pairs and titles, so it can flag ordinary phrases."),
    dict(q="What happens if I edit the prompt after sending?", a="The restored answer keeps the values from the moment you sent it. Send again to get a fresh reply."),
]
