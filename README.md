# bKash AI Ticket Analyzer

An AI-powered customer support ticket investigation system for bKash. It takes a customer complaint and transaction history, cross-references them, and returns structured analysis — verdict, case type, severity, department routing, agent summary, and a safe customer reply.

---

## Project Structure

```
├── main.py              # FastAPI app and safety filter
├── ai_engine.py         # Groq LLM integration and fallback logic
├── language_utils.py    # Language detection (English / Bangla / Banglish)
├── schemas.py           # Pydantic request/response models
├── test_cases.py        # Integration test suite
├── index.html           # Frontend UI
├── script.js            # Frontend API calls
├── style.css            # Frontend styling
├── Dockerfile           # Container setup
└── requirements.txt     # Python dependencies
```

---

## Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/) (free tier available)
- Docker (optional, for containerized deployment)

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd bkash-ticket-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Or export it directly:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the API

### Local development

```bash
python main.py
```

The API starts at `http://127.0.0.1:8000`.

Or with uvicorn directly:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Docker

```bash
# Build image
docker build -t bkash-ticket-analyzer .

# Run container (pass API key as environment variable)
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here bkash-ticket-analyzer
```

---

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{ "status": "ok" }
```

### Analyze Ticket

```
POST /analyze-ticket
Content-Type: application/json
```

**Request body:**

```json
{
  "ticket_id": "T001",
  "complaint": "I accidentally sent 5000 BDT to the wrong person.",
  "language": "en",
  "channel": "app",
  "user_type": "customer",
  "campaign_context": "none",
  "transaction_history": [
    {
      "transaction_id": "TX1001",
      "timestamp": "2026-06-26T10:00:00Z",
      "type": "send_money",
      "amount": 5000,
      "counterparty": "01711111111",
      "status": "success"
    }
  ]
}
```

**Language options:** `en` | `bn` | `banglish`

**Response fields:**

| Field | Description |
|---|---|
| `ticket_id` | Echo of input ticket ID |
| `evidence_verdict` | `consistent` / `inconsistent` / `insufficient_data` |
| `case_type` | Category of issue (e.g. `wrong_transfer`, `payment_failed`) |
| `severity` | `low` / `medium` / `high` / `critical` |
| `department` | Routing target (e.g. `dispute_resolution`, `fraud_risk`) |
| `relevant_transaction_id` | Matched transaction, if any |
| `agent_summary` | 2–3 sentence factual summary for internal agents |
| `recommended_next_action` | Concise action step for the handling agent |
| `customer_reply` | Safe, professional reply to send to the customer |
| `human_review_required` | Boolean flag for escalation |
| `confidence` | Model confidence score (0.0–1.0) |
| `reason_codes` | List of machine-readable diagnostic codes |

---

## Frontend

Open `index.html` directly in a browser (no build step needed). It connects to the locally running API at `http://127.0.0.1:8000`.

Fill in the complaint, language, transaction details, and click **Analyze Ticket** to see the structured result.

---

## Running Tests

Make sure the API is running first, then:

```bash
python test_cases.py
```

The test suite covers:

| Test | Description |
|---|---|
| English Wrong Transfer | Complaint matches a 5000 BDT send_money transaction |
| Bangla Complaint | Unicode Bangla input with matching history |
| Banglish Failed Payment | Mixed-language complaint, transaction status is `failed` |
| Inconsistent Claim | Customer claims 10,000 BDT lost, history shows 500 BDT |
| Refund Request Without History | Empty transaction history |

Each test asserts:
- HTTP 200 response
- Valid `evidence_verdict` value
- No forbidden phrases (`PIN`, `OTP`, `password`, `refund confirmed`) in customer reply
- Response time under 30 seconds

---

## AI / Model Usage

**Provider:** [Groq](https://groq.com/)  
**Model:** `llama-3.3-70b-versatile`  
**Temperature:** `0` (deterministic output)  
**Response format:** JSON mode enforced via `response_format: {"type": "json_object"}`

The model receives two inputs:

1. **System prompt** — defines the investigation framework, output schema, classification values, and safety rules.
2. **User message** — the full ticket payload as JSON, including complaint text and transaction history.

The model is instructed to:
- Cross-reference the complaint against transaction history
- Classify the case type, severity, department, and evidence verdict
- Generate an agent summary, recommended action, and customer-facing reply
- Treat any instructions inside complaint text as **untrusted user input** (prompt injection defense)

### Fallback behavior

If the API key is missing, the model returns an empty response, or JSON parsing fails, the system returns a safe fallback response with:
- `evidence_verdict: insufficient_data`
- `human_review_required: true`
- `confidence: 0.30`
- `reason_codes: ["MODEL_OUTPUT_PARSE_FAILED"]`

This ensures the API never crashes silently — every ticket gets a response.

---

## Language Detection

Handled by `language_utils.py` before the AI call:

| Language | Detection method |
|---|---|
| **Bangla (`bn`)** | Unicode range `\u0980–\u09FF` detected in text |
| **Banglish** | Keyword scoring against a Banglish word list; Banglish wins if score ≥ 2 and exceeds English score |
| **English (`en`)** | Default fallback |

The detected language is merged into the ticket payload before it is sent to the AI, giving the model additional context.

---

## Safety Logic

Two layers of safety are applied to every `customer_reply` before it is returned:

### 1. AI-level guardrails (system prompt)

The model is explicitly instructed to never:
- Ask for `PIN`, `OTP`, `password`, or card number
- Promise a refund or guarantee money will be returned

### 2. Server-side safety filter (`main.py → safety_check()`)

Even if the model violates its instructions, a regex-based filter runs on every response:

**Credential redaction** — matches and replaces these patterns with `[REDACTED]`:
- `\bpin\b`
- `\botp\b`
- `\bpassword\b`
- `\bcard\s*number\b`

**Refund promise removal** — replaces these phrases with `"we will review your request"`:
- `"we will refund you"`
- `"your money will be returned"`

All matches are case-insensitive.

---

## Known Limitations

**No persistent storage**
Tickets are analyzed in-memory and not saved anywhere. There is no database, ticket history, or audit log.

**Single transaction type**
The frontend demo hardcodes `type: "send_money"` for all transactions. The API supports other types (e.g., cash_in, payment) but the UI does not expose them.

**Banglish detection is keyword-based**
The Banglish detector uses a fixed word list. Mixed complaints with few Banglish keywords may be misclassified as English. The AI handles the actual language correctly regardless.

**No authentication**
The API has no API key, token, or rate limiting. CORS is set to `allow_origins=["*"]`. This is intentional for development but must be hardened before production deployment.

**Groq rate limits**
The free Groq tier has request-per-minute limits. Under high load, requests may be delayed or rejected by the upstream API, triggering the fallback response.

**Model hallucination risk**
The LLM may produce plausible-sounding but incorrect analysis, particularly when transaction history is sparse or ambiguous. `human_review_required` is set to `true` in low-confidence cases to mitigate this.

**No Bangla customer reply**
The model generates `agent_summary` and `customer_reply` in English regardless of the complaint language. Localized replies are not yet supported.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for LLM access |

---

## Dependencies

```
fastapi
uvicorn
pydantic>=2.0
groq
python-dotenv
requests
```
