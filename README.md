# Clara Automation Pipeline

> Zero-cost automation workflow: Demo Call → Retell Agent Draft → Onboarding Updates → Agent Revision

A fully automated pipeline that converts demo call transcripts into preliminary AI voice agent configurations (v1), then refines them with onboarding data (v2), with complete versioning, changelogs, and diff tracking.

---

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌────────────┐
│  Demo Transcript │────▶│ Parse & Norm │────▶│ Extract Memo (v1)│────▶│ Store JSON │
│  (.txt file)     │     │              │     │  Rule-based NLP  │     │ outputs/   │
└─────────────────┘     └──────────────┘     └──────────────────┘     └────────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Generate Agent   │
                                             │ Spec (v1)        │
                                             │ Retell-compatible│
                                             └──────────────────┘

┌───────────────────────┐     ┌──────────┐     ┌───────────────┐     ┌────────────┐
│ Onboarding Transcript │────▶│ Load v1  │────▶│ Diff & Merge  │────▶│ Store v2 + │
│ (.txt file)           │     │ Memo     │     │ → v2 Memo     │     │ Changelog  │
└───────────────────────┘     └──────────┘     └───────────────┘     └────────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Generate Agent   │
                                             │ Spec (v2)        │
                                             │ + changelog.md   │
                                             └──────────────────┘
```

### Data Flow

1. **Pipeline A** (Demo → v1): `transcript.txt` → `parse_transcript.py` → `extract_memo.py` → `generate_agent_spec.py` → `outputs/accounts/<id>/v1/`
2. **Pipeline B** (Onboarding → v2): `transcript.txt` → `update_from_onboarding.py` → diff/merge with v1 → `generate_agent_spec.py` → `outputs/accounts/<id>/v2/` + `changelog.md`

---

## Quick Start

### Prerequisites

- **Python 3.10+** (no external dependencies required)
- **Docker + Docker Compose** (for n8n workflow automation)

### Option 1: Run with Python (Simplest)

```bash
# Clone the repo
git clone <repo-url>
cd clara-automation-pipeline

# Run the full pipeline on all transcripts
python scripts/run_pipeline.py --pipeline all

# Or run just Pipeline A (demo → v1)
python scripts/run_pipeline.py --pipeline A

# Or run just Pipeline B (onboarding → v2)
python scripts/run_pipeline.py --pipeline B
```

### Option 2: Run with Docker

```bash
# Build and run the pipeline
docker-compose run pipeline

# Or start n8n for workflow automation
docker-compose up n8n
# Then open http://localhost:5678 (admin / changeme)
```

### Option 3: Run via n8n Workflows

1. Start n8n: `docker-compose up n8n`
2. Open http://localhost:5678
3. Import `workflows/pipeline_a_demo_to_agent.json`
4. Import `workflows/pipeline_b_onboarding_update.json`
5. Trigger via webhook or manual execution

---

## Plugging in Dataset Files

### Adding Transcripts

Place your transcript files in the appropriate directories:

```
data/transcripts/
├── demo/
│   ├── company_name_demo.txt        # Demo call transcript
│   └── ...
└── onboarding/
    ├── company_name_onboarding.txt  # Onboarding call transcript
    └── ...
```

**File naming convention**: Use matching prefixes so the pipeline can pair demo + onboarding transcripts:
- `bens_electric_demo.txt` ↔ `bens_electric_onboarding.txt`

**Transcript format**: Plain text with timestamped speaker turns:
```
Clara Demo Call - Company Name
Date: 2024-11-15
Participants: Alex (Clara Sales), John (Owner, Company Name)

[00:00:15] Alex: Hello, thanks for joining...
[00:00:30] John: Hi, we're Company Name...
```

### If You Have Audio Files Only

Use Whisper (free, open-source) to transcribe locally:
```bash
pip install openai-whisper
whisper recording.mp3 --model base --output_format txt
```

---

## Where Outputs Are Stored

```
outputs/
└── accounts/
    └── <account_id>/
        ├── v1/
        │   ├── account_memo.json    # Structured account data from demo
        │   └── agent_spec.json      # Retell agent config (preliminary)
        ├── v2/
        │   ├── account_memo.json    # Updated data from onboarding
        │   └── agent_spec.json      # Retell agent config (confirmed)
        ├── changelog.md             # Human-readable diff v1→v2
        └── changes.json             # Structured changes data
```

---

## Retell Agent Setup

### Creating a Retell Account

1. Go to https://app.retellai.com and sign up (free tier: $10 credits)
2. Navigate to Dashboard → API Keys
3. Copy your API key

### Importing Agent Configuration

Since Retell's free tier may not support programmatic agent creation:

1. Open `outputs/accounts/<id>/v2/agent_spec.json`
2. In Retell Dashboard, click **Create Agent**
3. Set **Agent Name** from `agent_name` field
4. Select **Voice** matching `voice_id` field
5. Create a **Response Engine** (Retell LLM)
6. Paste the `system_prompt` from `response_engine.system_prompt` into the prompt configuration
7. Configure voice settings (`voice_speed`, `voice_temperature`, etc.)
8. Save and test

---

## Dashboard (Bonus)

A local web dashboard is included for viewing outputs and diffs:

```bash
# Serve the dashboard locally (requires Python)
cd dashboard
python -m http.server 8080

# Open http://localhost:8080
```

Features:
- Account selector with all processed accounts
- v1 and v2 JSON viewers with syntax highlighting
- Side-by-side diff viewer showing field-level changes
- Changelog display
- Agent spec viewer with version toggle

---

## Project Structure

| Directory | Contents |
|-----------|----------|
| `scripts/` | Python pipeline scripts |
| `scripts/utils/` | Extraction patterns, storage, templates, tracker |
| `data/transcripts/` | Input transcript files (demo + onboarding) |
| `workflows/` | n8n workflow JSON exports |
| `outputs/` | Generated account memos, agent specs, changelogs |
| `dashboard/` | Web-based diff viewer and dashboard |
| `tasks/` | Pipeline task tracker (auto-generated) |

---

## Known Limitations

1. **Rule-based extraction**: Uses regex and keyword matching instead of LLM. Handles structured transcripts well but may miss nuanced or unusual phrasing. Production version would use an LLM for better extraction.

2. **Transcript format dependency**: Expects timestamped speaker turns in a specific format. Transcripts without timestamps or structured speaker labels may need preprocessing.

3. **Retell mock integration**: Agent specs are generated locally as JSON files. Actual Retell API integration would require using their SDK/API with valid credentials.

4. **No real-time webhook**: The n8n workflows are configured with webhook triggers but operate in batch mode locally. Production deployment would support real-time file processing.

---

## What I Would Improve with Production Access

| Improvement | How |
|------------|-----|
| **LLM extraction** | Use GPT-4 or Claude for much more accurate and nuanced data extraction from transcripts |
| **Real Retell API** | Programmatically create and update agents via Retell's REST API |
| **Whisper integration** | Auto-transcribe audio recordings in the pipeline |
| **Real-time triggers** | n8n webhooks connected to file upload systems or form submissions |
| **Conflict resolution UI** | Interactive web interface for resolving ambiguous data during v1→v2 merge |
| **Asana/Jira integration** | Automatically create task items for each new account |
| **Database storage** | Supabase or PostgreSQL instead of local JSON files |
| **CI/CD pipeline** | Automated testing and deployment of agent configuration changes |
| **Multi-version history** | Support v1, v2, v3... with full Git-like version history |
| **A/B testing** | Compare different agent prompts for the same account |

---

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Pipeline scripts | Python 3.11 | Free |
| Extraction | Rule-based NLP (regex + keywords) | Free |
| Automation orchestrator | n8n (self-hosted Docker) | Free |
| Data storage | Local JSON files | Free |
| Task tracking | Markdown file | Free |
| Dashboard | HTML/CSS/JS (vanilla) | Free |
| Containerization | Docker + Docker Compose | Free |
| **Total** | | **$0** |

---

## Zero-Cost Compliance

This solution uses **no paid services, APIs, or subscriptions**:
- ✅ No paid LLM calls (rule-based extraction)
- ✅ n8n self-hosted (no cloud plan)
- ✅ Local file storage (no database subscription)
- ✅ Retell mock integration (JSON spec output)
- ✅ All tools are open-source or free-tier

---

## License

This project is built as an assignment demonstration. All transcript data is synthetic and does not contain real customer information.
