# Privacy Guard

A pure Python backend built with Flask that protects user privacy during AI interactions. It uses regex-based pattern matching to scan prompts for sensitive data (like emails, cards, and SSNs), swaps them out for consistent placeholder tokens (like `<EMAIL_1>`), and securely rehydrates the AI model's response so it reads naturally.

## Key Features

* **Python Backend:** Detection, masking, and restoring run natively in a centralized Flask application.


* **Consistent Tokens:** Repeated values reuse the same token, preserving conversational context for the LLM (e.g., matching a specific person to their email).


* **Live Filter Toggles:** Turn specific PII categories on or off and watch the safe payload update dynamically.


* **Smart Validation:** Credit card numbers must pass a Luhn check to prevent false positives on standard serial or order numbers.



## How It Works

1. **Find Personal Data:** Pattern matching scans the prompt for emails, phone numbers, cards, IDs, IP addresses, and optionally, names.


2. **Swap in Placeholders:** Each value becomes a mapped token (e.g., `<PHONE_1>`). The same value always gets the same token.


3. **Send the Safe Version:** Only the masked prompt goes to the model. The server keeps the real values and never forwards them.


4. **Restore the Answer:** When the reply returns, every token is swapped for the original value so the answer reads normally to the user.



## Installation

Clone the repository and set up your local environment:

```bash
git clone https://github.com/Syntax-Sage10/privacy-guard.git
cd privacy-guard

# Create and activate your virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

```

## Usage

Start the Flask development server:

```bash
python3 app.py

```

Open your browser and navigate to `[http://127.0.0.1:5000](http://127.0.0.1:5000)` to interact with the UI.

## Project Structure

* **`app.py`**: The Flask server, routing, and JSON API endpoints (`/api/sanitize`, `/api/send`).


* **`pii.py`**: The core data protection engine containing the regex categories, masking logic, Luhn validation, and the simulated LLM response generator.


* **`content.py`**: Interface copy, feature lists, FAQ, and the demonstration tagline.


* **`requirements.txt`**: Project dependencies, requiring `flask>=3.0`.



## Customization: Using a Real LLM

This repository currently uses a simulated model for demonstration purposes. To connect to a live API (like OpenAI, Anthropic, or Hugging Face):

1. Open `pii.py`.
2. Locate the `fake_llm()` function.


3. Replace the mock logic with your preferred API call, ensuring you pass the masked prompt to the model and return its text response.



## Limitations

This is a demonstration build. The current detection engine relies on regular expressions, meaning highly unusual formats or unconventional names may be missed. For production deployments handling highly sensitive data, it is recommended to augment the regex engine with a trained Named Entity Recognition (NER) model and implement robust user authentication.# llm-privacy-guard
