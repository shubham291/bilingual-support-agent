# Bilingual Customer Support Agent

A Python API that reads customer messages in Arabic or English, tags them by topic and urgency, and drafts a reply from policy documents, with the source of each answer. Personal data is hidden before anything is sent to the AI, and trick or off-topic messages are blocked.

Built with Python, FastAPI, Pydantic and LangChain.

## Example

Request:

```json
{ "message": "My Emirates ID 784-1990-1234567-1 expired, what do I do?" }
```

Response:

```json
{
  "blocked": false,
  "pii_found": ["EMIRATES_ID"],
  "triage": {
    "language": "en",
    "category": "emirates_id",
    "urgency": "high",
    "summary": "User's Emirates ID has expired and is asking how to renew it."
  },
  "reply": "To renew your Emirates ID, use the ICP app or website [1] ...",
  "sources": ["emirates-id"],
  "needs_human": true
}
```

## How it works

```
message
  1. Block trick messages      ("ignore your instructions...", in English or Arabic)
  2. Hide personal data        Emirates ID, UAE phone numbers, emails → [EMIRATES_ID], [PHONE], [EMAIL]
  3. Triage                    language, topic, urgency (AI, checked against a Pydantic model)
  4. Off-topic?                → fixed reply, no further AI call
  5. Find policy text          LangChain search over the policy documents
  6. Draft the reply           only from the found text, with sources; refuses if nothing relevant is found
  7. Urgent?                   → needs_human = true
```

The AI only ever sees the masked text, so ID numbers and phone numbers never leave the server.

## Policy documents

The demo knowledge base is in `data/policies/`: short help-desk guidance on Emirates ID renewal, visa expiry, VAT/TRN, service levels and privacy (one document is in Arabic). Each file has labels at the top (title, date, audience). Documents marked `audience: staff` are never shown to customers.

This is demo content written for the project, not official government guidance.

## Tests

`eval.py` runs 10 sample messages through the full pipeline and checks the results:

| What is checked | Cases |
|---|---|
| Topic and urgency, Arabic and English | 5 |
| Personal data is hidden | 2 |
| Off-topic request is caught | 1 |
| Trick messages are blocked (English and Arabic) | 2 |

Result: 10/10 passing.

```bash
python eval.py
```

## Run it locally

```bash
git clone https://github.com/shubham291/bilingual-support-agent.git
cd bilingual-support-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your Vercel AI Gateway key:

```
AI_GATEWAY_API_KEY=your_key
```

Start the API:

```bash
fastapi dev main.py
```

Open http://127.0.0.1:8000/docs to try it in the browser.

## Project files

| File | What it does |
|---|---|
| `main.py` | The API endpoint and the order of the steps |
| `triage.py` | Asks the AI for language, topic, urgency and a summary |
| `guardrails.py` | Hides personal data and blocks trick messages |
| `rag.py` | Loads, splits and searches the policy documents, and drafts the reply |
| `knowledge.py` | Prepares the document search once when the server starts |
| `eval.py` | The 10-case test |
| `data/policies/` | The policy documents |
| `learning/` | Practice files from learning Python |

## Limits

- The trick-message check uses a list of known phrases, so reworded attacks can get through.
- The test set is small (10 messages).
- Documents are kept in memory, which suits a small knowledge base but not a large one.

## Next

- Docker and a deployment on AWS
- More test messages, including harder Arabic cases
