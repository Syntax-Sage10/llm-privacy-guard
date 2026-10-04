TAGLINE = "Your prompt, minus the personal details."
SUBTITLE = ("Privacy Guard hides names, organisations, places, emails, phone numbers and card numbers before a "
            "prompt reaches an AI model, then puts them back in the answer.")

STEPS = [
    dict(icon="scan-search", title="Find personal data",
         body="Patterns catch emails, phone numbers, cards, IDs and IP addresses. A multilingual XLM-RoBERTa model finds people, organisations and places."),
    dict(icon="eye-off", title="Swap in placeholders",
         body="Each value becomes a token such as <EMAIL_1>. The same value always gets the same token, so the model can still follow who is who."),
    dict(icon="send", title="Send the safe version",
         body="Only the masked prompt goes to the model. The server keeps the real values and never forwards them."),
    dict(icon="undo-2", title="Restore the answer",
         body="When the reply comes back, every token is swapped for the original value, so the answer reads naturally."),
]
FEATURES = [
    dict(icon="brain-circuit", title="Trained name detection", body="A Hugging Face NER model loads once at startup and runs on Apple Silicon (MPS), CUDA or CPU."),
    dict(icon="link-2", title="Consistent tokens", body="Repeated values reuse one token, so context survives masking."),
    dict(icon="list-plus", title="Custom watchlist", body="Add project names or codenames. They become <CUSTOM_1> wherever they appear."),
    dict(icon="badge-check", title="Cards are checked", body="Card numbers must pass the Luhn check, so order numbers are left alone."),
    dict(icon="mouse-pointer-click", title="Hover to reveal", body="Point at a token in the safe payload to see the original text highlighted in your prompt."),
    dict(icon="download", title="Copy or download", body="Export the sanitized prompt to the clipboard or a .txt file for documentation."),
]

# Presentation material
ARCH = [
    dict(icon="user", title="User input", body="The raw prompt, with real names and numbers, stays inside your boundary."),
    dict(icon="server", title="Local Flask backend", body="Detects, masks and stores the token map in memory."),
    dict(icon="cloud", title="External LLM", body="Receives only the tokenized payload, such as <NAME_1> and <CARD_1>."),
    dict(icon="undo-2", title="Rehydrated output", body="The backend swaps tokens back and returns a readable answer."),
]
COMPLIANCE = [
    dict(icon="shield-check", title="Data stays local", body="Real values are held by the backend and never forwarded to the model provider."),
    dict(icon="scale", title="Built for strict frameworks", body="Minimising personal data sent to third parties supports GDPR, DPDP and HIPAA-style data-handling policies."),
    dict(icon="file-text", title="Documented by design", body="Export the sanitized payload as a record of exactly what left your environment."),
]
DEMO = [
    "Open the app with the sample prompt and show the safe payload filling with tokens.",
    "Point out that Priya Sharma and Rahul Mehta get different tokens, while a repeated value reuses its token.",
    "Hover a token to show the original text highlighted in the prompt.",
    "Toggle a filter off and on and watch the payload update as you type.",
    "Add \"Project Falcon\" to the watchlist, then send and show the restored answer.",
]
ROADMAP = ("Next, Privacy Guard can run as a localised API service or an encrypted edge gateway: a drop-in proxy "
           "that sits in front of enterprise systems, masks every outbound request, encrypts the token map in "
           "transit and at rest, and restores responses, so any internal tool gains privacy without changes.")

LIMITS = ("This is a demonstration. The model reply is simulated. Structured data uses regular expressions, so unusual "
          "formats can be missed, and the NER model can miss or mislabel some names. Add authentication, encrypted "
          "storage and audit logging before production use.")
FAQ = [
    dict(q="Does my text go to a real model?", a="No. The reply is generated locally by a stand-in function. Swap fake_llm() in pii.py for a real API call to use a live model."),
    dict(q="How are names detected?", a="A pre-trained XLM-RoBERTa token-classification model finds people, organisations and locations. It loads once when the server starts."),
    dict(q="What happens if I edit the prompt after sending?", a="The restored answer keeps the values from the moment you sent it. Send again to get a fresh reply."),
]