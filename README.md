# 🔗 Agentic AI PMI Copilot

**AI-powered Post-Merger Integration analysis workflow for private equity and mid-market acquirers.**

An MVP demonstrating how agentic AI pipelines can accelerate post-merger integration (PMI) by ingesting documents from two merging organizations, extracting business intelligence, detecting integration risks and opportunities, and generating a reviewed, exportable report.

---

## Business Problem

Post-merger integrations fail at alarming rates — often because critical gaps, risks, and synergies are identified too late or not at all. Integration teams are buried in hundreds of documents across two organizations, manually hunting for mismatches in systems, processes, people, and policies.

**PMI Copilot** automates the heavy analytical lift:

| Manual PMI Approach | PMI Copilot Approach |
|---|---|
| Analysts read 50+ documents over weeks | AI parses and extracts in minutes |
| Gaps found ad-hoc during integration | Gaps surfaced systematically before Day 1 |
| Risks documented in scattered spreadsheets | Risks prioritized with evidence in one report |
| Synergies estimated on gut feel | Synergies identified with rationale and category |
| Recommendations vary by analyst experience | Consistent, evidence-backed action plans |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                         │
│   Upload → Analyze → Review/Edit → Approve → Export          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                            │
│   /upload  /analyze  /review  /export                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Agent Pipeline                              │
│                                                               │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐               │
│  │ Ingestion│──▶│ Parsing  │──▶│ Extraction │               │
│  │  Agent   │   │  Agent   │   │   Agent    │               │
│  └──────────┘   └──────────┘   └─────┬──────┘               │
│                                      │                        │
│            ┌─────────────────────────┼──────────────┐        │
│            ▼                         ▼              ▼        │
│     ┌───────────┐          ┌──────────────┐  ┌──────────┐   │
│     │ Gap Agent │          │  Risk Agent  │  │ Synergy  │   │
│     └─────┬─────┘          └──────┬───────┘  │  Agent   │   │
│           │                       │          └────┬─────┘   │
│           └───────────┬───────────┘               │          │
│                       ▼                           │          │
│              ┌─────────────────┐                  │          │
│              │ Recommendation  │◀─────────────────┘          │
│              │     Agent       │                              │
│              └────────┬────────┘                              │
│                       ▼                                       │
│              ┌─────────────────┐    ┌──────────────┐         │
│              │  Review Agent   │──▶ │ Report Agent │         │
│              │ (human-in-loop) │    └──────────────┘         │
│              └─────────────────┘                              │
└───────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Services Layer                             │
│   LLM Service  ·  Parser Service  ·  Storage Service         │
└──────────────────────────────────────────────────────────────┘
```

### Module Map

```
app/
├── main.py                  # FastAPI entry point
├── config.py                # Settings from .env
├── schemas/                 # Pydantic models
│   ├── documents.py         # Upload, parse, session models
│   ├── extraction.py        # Entity & classification models
│   ├── findings.py          # Gaps, risks, synergies, recs
│   └── review.py            # Review workflow & final report
├── agents/                  # Business logic agents
│   ├── ingestion_agent.py   # File validation & session mgmt
│   ├── parsing_agent.py     # PDF/DOCX/TXT/CSV parsing
│   ├── extraction_agent.py  # LLM entity extraction
│   ├── gap_agent.py         # Integration gap detection
│   ├── risk_agent.py        # Risk identification
│   ├── synergy_agent.py     # Synergy opportunity detection
│   ├── recommendation_agent.py  # Action plan generation
│   ├── review_agent.py      # Human review workflow
│   └── report_agent.py      # Final report generation
├── services/                # Shared infrastructure
│   ├── llm_service.py       # OpenAI API wrapper
│   ├── parser_service.py    # File format parsers
│   └── storage_service.py   # JSON-based session storage
├── api/                     # REST endpoints
│   ├── upload.py            # POST /sessions, /upload
│   ├── analyze.py           # POST /analyze, GET /findings
│   ├── review.py            # POST /review, /approve
│   └── export.py            # POST /export, GET /report
└── prompts/                 # LLM prompt templates
    ├── classify_document.txt
    ├── extract_entities.txt
    ├── detect_gaps.txt
    ├── detect_risks.txt
    ├── detect_synergies.txt
    ├── recommend_actions.txt
    └── executive_summary.txt

frontend/
└── streamlit_app.py         # Full workflow UI

data/
├── sample_docs/             # Example documents for demo
├── outputs/                 # Generated reports
└── sessions/                # Session state (auto-created)

tests/
├── test_parsers.py          # Parser unit tests
├── test_agents.py           # Agent logic tests
└── test_reports.py          # Report formatting tests
```

---

## Workflow

| Step | Agent | What Happens |
|------|-------|-------------|
| 1. Upload | Ingestion Agent | User uploads PDF/DOCX/TXT/CSV files. Files are validated and saved to a session. |
| 2. Parse | Parsing Agent | Each file is converted to normalized text and sections. CSVs get column/row metadata. |
| 3. Extract | Extraction Agent | LLM classifies each document and extracts entities (companies, systems, roles, KPIs, etc.). |
| 4. Gaps | Gap Agent | LLM analyzes cross-document data for duplicate systems, overlapping roles, missing ownership, etc. |
| 5. Risks | Risk Agent | LLM identifies operational, technical, and people risks with severity ratings and evidence. |
| 6. Synergies | Synergy Agent | LLM detects cost savings, efficiency gains, and value-creation opportunities. |
| 7. Recommend | Recommendation Agent | LLM generates a prioritized action plan with owners, timelines, and impact estimates. |
| 8. Review | Review Agent | Human reviews all findings. Can approve, edit, reject, or annotate individual items. |
| 9. Export | Report Agent | Generates executive summary via LLM, assembles full Markdown + JSON report. |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- OpenAI API key (GPT-4o-mini or GPT-4o recommended)

### Installation

```bash
# Clone / download the project
cd pmi-copilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the App

**Option 1: Streamlit UI (recommended for demo)**
```bash
cd pmi-copilot
streamlit run frontend/streamlit_app.py
```
Opens at `http://localhost:8501`

**Option 2: FastAPI backend**
```bash
uvicorn app.main:app --reload --port 8000
```
API docs at `http://localhost:8000/docs`

### Running Tests
```bash
pytest tests/ -v
```

---

## Example Use Case

**Scenario:** A PE firm is acquiring TargetCo Solutions and merging it into AcquireCo Inc.

1. **Upload** three files from `data/sample_docs/`:
   - `acquireco_operating_model.txt` — Acquirer's org, systems, and KPIs
   - `targetco_operating_model.txt` — Target's org, systems, and known issues
   - `systems_inventory.csv` — Side-by-side system comparison with costs

2. **Run Analysis** — the pipeline processes all three documents through 6 AI agents.

3. **Review Findings** — the UI shows:
   - **Gaps:** Duplicate CRM (Salesforce vs HubSpot), incompatible HRIS (Workday vs BambooHR), different project management tools, conflicting cloud providers
   - **Risks:** Key person dependency on Tom Nguyen, no disaster recovery plan at TargetCo, no endpoint security at TargetCo, tribal knowledge risk
   - **Synergies:** CRM consolidation ($120K savings), cloud standardization, unified BI platform, shared services optimization
   - **Recommendations:** Prioritized 30/60/90-day action plan with owners

4. **Approve & Export** — download a structured Markdown or JSON report for the integration team.

---

## How Human Review Improves Trust

The human-in-the-loop review step is not optional decoration — it is a core design principle:

| Problem | How Review Solves It |
|---------|---------------------|
| LLMs can hallucinate findings | Analyst verifies every gap, risk, and synergy before it enters the report |
| Context is king | Domain experts can edit recommendations based on deal-specific knowledge |
| Stakeholder confidence | "AI-assisted, human-verified" carries more weight than "AI-generated" |
| Accountability | Every finding has a review status — approved, edited, or rejected — creating an audit trail |
| Iteration | Analysts can reject weak findings and re-run specific sections |

The review workflow transforms the system from a black-box AI tool into a **collaborative intelligence platform** where AI does the heavy lifting and humans ensure quality.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, Pydantic |
| Frontend | Streamlit |
| LLM | OpenAI GPT-4o-mini (configurable) |
| File Parsing | PyPDF2, python-docx, pandas |
| Storage | JSON file-based (session storage) |
| Testing | pytest |

---

## Extending the MVP

- **Database:** Replace `storage_service.py` with SQLite/PostgreSQL
- **LLM Provider:** Swap `llm_service.py` to use Anthropic, Gemini, or local models
- **Auth:** Add FastAPI middleware for multi-user sessions
- **Advanced Parsing:** Add OCR (Tesseract), table extraction (Camelot), or structured PDF parsing
- **Async Pipeline:** Make agent steps async with background tasks
- **Vector Search:** Add embeddings for cross-document semantic matching

---

## License

MIT — built as a portfolio demonstration project.
