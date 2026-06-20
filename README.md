# NexusOps AI — Enterprise Agent Suite

A collection of 10 AI agents built for regional businesses in Saarland, Germany. Each agent is accessible via a ChatGPT-like chat interface and powered by Google Gemini 2.5 Flash.

---

## Agents

| # | Agent | Client |
|---|-------|--------|
| 1 | Invoice Processing | Globus Group (St. Wendel) |
| 2 | Shift Replacement | Universitätsklinikum des Saarlandes (Homburg) |
| 3 | Work Permit Validation | Leistenschneider Personaldienstleistungen (Saarbrücken) |
| 4 | CV & Certificate Fraud Detection | Persowerk Deutschland GmbH (Saarbrücken) |
| 5 | Interview Support | Kohlpharma GmbH (Merzig) |
| 6 | Marketing Content / Filmmaker | Dr. Theiss Naturwaren GmbH (Homburg) |
| 7 | Customer Analytics | Dr. Theiss Naturwaren GmbH (Homburg) |
| 8 | Dynamic Pricing | Dr. Theiss Naturwaren GmbH (Homburg) |
| 9 | Competitive Gap Analysis | Dr. Theiss Naturwaren GmbH (Homburg) |
| 10 | Prompt-Injection-Resistant Email Agent | Rheinmetall |

---

## Requirements

- Python 3.9+
- A Google Gemini API key — get one at [aistudio.google.com](https://aistudio.google.com)

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd nexusops-ai
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
GEMINI_API_KEY=your_key_here
```

> **Note:** The app uses `gemini-2.5-flash`. Make sure your key has quota for this model. You can verify at [aistudio.google.com](https://aistudio.google.com).

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Select any agent from the sidebar.

---

## Project Structure

```
nexusops-ai/
│
├── app.py                        # Streamlit home page — agent directory
│
├── agents/                       # Core agent logic (no UI)
│   ├── invoice_agent.py          # Invoice extraction + department routing
│   ├── shift_agent.py            # Staff DB + shift gap matching
│   ├── work_permit_agent.py      # Permit validation + confidence score
│   ├── cv_fraud_agent.py         # Fraud risk scoring for CVs & certificates
│   ├── interview_agent.py        # Interview question generation (chat)
│   ├── marketing_agent.py        # Reel concept + safe zone guide
│   ├── analytics_agent.py        # Customer segmentation + targeting signals
│   ├── pricing_agent.py          # Signal-driven pricing recommendations
│   ├── competitive_agent.py      # Competitive gap + white-space analysis
│   └── secure_email_agent.py     # Injection-resistant email processor
│
├── pages/                        # One Streamlit page per agent
│   ├── 1_Invoice_Processing.py
│   ├── 2_Shift_Replacement.py
│   ├── 3_Work_Permit_Validation.py
│   ├── 4_CV_Fraud_Detection.py
│   ├── 5_Interview_Support.py
│   ├── 6_Marketing_Content.py
│   ├── 7_Customer_Analytics.py
│   ├── 8_Dynamic_Pricing.py
│   ├── 9_Competitive_Gap_Analysis.py
│   └── 10_Secure_Email_Agent.py
│
├── shared/
│   ├── llm.py                    # Gemini client — ask(), ask_with_file(), chat()
│   └── file_utils.py             # DOCX/XLSX text extraction, MIME helpers
│
├── samples/                      # Local demo files — not committed (see .gitignore)
│   ├── invoices/                 # 11 real invoices (PDF, PNG, DOCX)
│   ├── cvs/                      # 10 sample CVs (PDF)
│   ├── work_permits/             # 4 permits — 2 valid, 2 invalid
│   ├── certificates/             # 5 certificate images
│   ├── hospital_schedule.xlsx    # UKS shift schedule
│   ├── job_offers.pdf            # Kohlpharma job descriptions
│   └── dr_theiss_data.pdf        # Dr. Theiss product & market data
│
├── .env                          # Your API key — never committed
├── .env.example                  # Template
├── .gitignore
├── requirements.txt
└── tasks.txt                     # Original task brief
```

---

## How each agent works

**Invoice Processing (#1)** — Upload a PDF, image, or DOCX invoice. The agent extracts vendor, amount, line items, and VAT, then routes it to the correct internal department (IT, Finance, Marketing, etc.) with reasoning and anomaly flags.

**Shift Replacement (#2)** — Describe a last-minute shift gap (ward, time, qualification needed). The agent searches a staff database, picks the best available candidates, and drafts ready-to-send messages for each.

**Work Permit Validation (#3)** — Upload any permit document. The agent determines if it is a valid German work authorisation, extracts the holder name and expiry date, and returns a confidence score with a PASS / REJECT / REVIEW verdict.

**CV & Certificate Fraud Detection (#4)** — Upload a CV or certificate. The agent checks for AI-generation signals, timeline inconsistencies, skills mismatches, and certificate authenticity, returning a fraud risk score from 0–100.

**Interview Support (#5)** — Paste a job description. The agent generates role-specific technical and behavioural questions, red flags to watch for, and live test suggestions. Continues as a chat so the manager can evaluate candidate answers in real time.

**Marketing Content / Filmmaker (#6)** — Describe a product or upload an image. The agent writes a full reel concept (hook, scenes, CTA) with platform-specific safe zone guidance for TikTok and Instagram, plus a ready-to-post caption.

**Customer Analytics (#7)** — Upload a CSV or describe customer data. The agent identifies behavioural segments, detects seasonal patterns, and generates targeting signals with optimal ad channel, day, and time per segment.

**Dynamic Pricing (#8)** — Enter a product and its current price. The agent reads live signals (weather, holidays, sports fixtures, supply chain, competitor moves) and recommends a new price with confidence level and guardrails.

**Competitive Gap Analysis (#9)** — Describe a product or load the Dr. Theiss data pack. The agent maps the competitive landscape, identifies white-space gaps, and recommends 2–3 new product opportunities ranked by market potential.

**Secure Email Agent (#10)** — Paste an email and list its attachments. Before any LLM processing, the agent scans for prompt injection patterns. It then checks whether all required documents are present (CV, work/residence permit, criminal record statement) and flags missing items.

---

## Demo tips

- Every agent page has a **"Load Sample"** tab pre-wired to the provided test documents — no manual upload needed for demos.
- Agent #10 has a built-in **"Test Injection"** tab that demonstrates the security layer catching a malicious email in real time.
- The sidebar lists all agents — click any to switch instantly.
