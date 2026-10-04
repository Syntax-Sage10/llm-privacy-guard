# Privacy Guard

A Flask app that protects personal data during AI interactions. It detects sensitive values in a prompt, swaps them for consistent placeholder tokens (like `<EMAIL_1>`), and restores them in the model's reply.

## Features

* **Trained name detection:** A Hugging Face XLM-RoBERTa token-classification pipeline (`Davlan/xlm-roberta-base-ner-hrl`) finds people (`PER`), organisations (`ORG`) and locations (`LOC`). It loads once at startup in `app.py` and uses Apple Silicon (MPS), CUDA or CPU, whichever is available. Names are on by default.
* **Regex for structured data:** Emails, cards (Luhn-checked), SSNs, IP addresses and phone numbers.
* **Consistent tokens:** Repeated values reuse one token, so context survives masking.
* **Custom watchlist:** Add project names or codenames. Matches (case-insensitive, whole word) become `<CUSTOM_n>`.
* **Synchronized hover:** Hover a token in the safe payload to highlight its original text in your prompt.
* **One-click export:** Copy the sanitized prompt or download it as `sanitized-prompt.txt`.
* **Liquid glass UI:** Frosted panels over a slowly morphing mesh gradient, with glass-tile chips that glow on hover.
* **Presentation page (`/website`):** System architecture diagram, compliance positioning, live demo script and roadmap.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open http://127.0.0.1:5000. The first run downloads the NER model (about 1 GB). If the model cannot load, the server still runs with the regex categories and the app shows a notice.

## Project structure

* `app.py`: Flask routes, global NER pipeline loading, JSON API (`/api/sanitize`, `/api/send`).
* `pii.py`: Detection, overlap resolution, masking, watchlist, simulated LLM, rehydration.
* `content.py`: Interface copy, architecture, compliance, demo script, roadmap.
* `templates/`, `static/`: UI.

## API

Both endpoints accept `{ "text": "...", "filters": {"email": true, ...}, "watchlist": ["Project Falcon"] }`.
`/api/sanitize` returns `safe`, `total`, `spans` and `ner`. `/api/send` returns `raw`, `restored` and `map`.

## Using a real LLM

In `pii.py`, replace `fake_llm()` with an API call that sends only the masked prompt (`sanitize(...)["safe"]`) and returns the reply text. `rehydrate()` then restores the values.

## Limitations

This is a demonstration. Regexes can miss unusual formats, the NER model can miss or mislabel names, and the token map is held in request memory only. Add authentication, encrypted storage and audit logging before production use.

## Roadmap

Run as a localised API service or an encrypted edge gateway: a proxy in front of enterprise systems that masks outbound requests, encrypts the token map, and restores responses.