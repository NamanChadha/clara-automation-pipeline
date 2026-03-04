# Clara Automation Pipeline

A robust, enterprise-grade system for automating the transition of voice AI agents from **Demo (v1)** to **Onboarding (v2)**.

## 🚀 Overview

This pipeline solves the "Operational Gap" between sales demos and production deployment. By analyzing call transcripts (Demo & Onboarding), it prevents human error, avoids silent assumptions, and ensures 100% data fidelity for Retell AI agents.

## 📁 Repository Structure

- `scripts/`: Core logic for extraction, merging, and agent configuration.
  - `run_pipeline.py`: Main CLI batch runner.
  - `extract_memo.py`: Deep-parsing of transcripts into structured JSON.
  - `update_from_onboarding.py`: Version-controlled merging logic (v1 → v2).
  - `generate_agent_spec.py`: Produces Retell-ready system prompts and variables.
- `data/`: Raw inputs (Transcripts & Audio).
- `outputs/`: Versioned artifacts for every account.
  - `accounts/<id>/v1/`: Preliminary configuration.
  - `accounts/<id>/v2/`: Confirmed production configuration.
  - `accounts/<id>/changelog.md`: Human-readable version diff.

## 🛠️ How to Run

### Prerequisite: Setup n8n & Dependencies

1. **n8n & Docker**: Follow the [n8n Setup Guide](docs/n8n_setup_guide.md) for full containerized deployment and environment configuration.
2. **Local Dependencies**:
```powershell
pip install -r requirements.txt
```

### Run Full Pipeline
To process all paired transcripts and generate v1, v2, and Changelogs:
```powershell
python scripts/run_pipeline.py --pipeline all
```

### View Results
Check the versioned outputs directly in the file system:
```powershell
# Open outputs/accounts/bens_electric_solutions/changelog.md for the raw report
# Or check the v1 and v2 folders for JSON data
```

## 🧠 Engineering Principles

- **Systems Thinking**: Not a one-off script, but a repeatable data pipeline.
- **Prompt Discipline**: Agent prompts follow a mandatory Greeting → Purpose → Transfer flow with strict fallback handling.
- **Idempotency**: Re-running the pipeline produces identical, predictable results.
- **Responsible Data**: Explicitly tracks missing data via `questions_or_unknowns` instead of hallucinating.

## ✅ Submission Checklist

- [x] `/workflows`: n8n exports for Pipeline A and B.
- [x] `/outputs/accounts/`: v1, v2, and changelogs.
- [x] `/scripts`: All extraction and merging logic.
- [x] `README.md`: Project overview and setup.
- [x] **Loom Video**: [Watch Demo](https://www.loom.com/share/4b52276bc2b246a3a2c179841483b615)

### Recorded Demo (3-5 Minutes)
The video covers:
1. Workflow architecture (n8n).
2. Demo + Onboarding pair processing for "Ben's Electric Solutions".
3. High-fidelity output analysis (v1 → v2).
4. Automated changelog generation.
