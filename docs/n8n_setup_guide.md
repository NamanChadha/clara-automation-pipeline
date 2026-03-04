# 🚀 n8n Setup & Operations Guide

This guide covers how to set up, configure, and batch-run the Clara Automation Pipeline using n8n and Docker.

## 🐳 1. Docker Setup (Recommended)

The easiest way to run the pipeline is via Docker Compose. This starts both the n8n environment and the Python automation container.

### Step 1: Start the services
```bash
docker-compose up -d
```

### Step 2: Access n8n
Open your browser and navigate to:
**URL**: `http://localhost:5678`

---

## 🔑 2. Environment Variables

Create a `.env` file in the root directory (use `.env.example` as a template):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `N8N_BASIC_AUTH_USER` | Admin username for n8n | `admin` |
| `N8N_BASIC_AUTH_PASSWORD` | Admin password for n8n | `changeme` |
| `PYTHONPATH` | Python path for internal scripts | `/app` |
| `DATA_DIR` | Directory for transcripts | `./data` |
| `OUTPUT_DIR` | Directory for generated results | `./outputs` |

---

## 📥 3. Workflow Import Steps

To import the automation workflows into n8n:

1.  Open the n8n UI at `http://localhost:5678`.
2.  Navigate to **Workflows** in the left sidebar.
3.  Click **Add Workflow** > **Import from File**.
4.  Upload the JSON files from the `/workflows` directory:
    *   `pipeline_a_demo_to_agent.json` (Demo Pipeline)
    *   `pipeline_b_onboarding_update.json` (Onboarding Pipeline)
5.  Click **Save** and ensure the workflows are **Active**.

---

## 🔄 4. "Run All Dataset" (Batch Processing)

If you need to process all transcripts at once (e.g., during initialization), use the built-in batch runner.

### Method A: Via Docker (Preferred)
Run the following command to process the entire `data/transcripts` directory:
```bash
docker-compose run pipeline python scripts/run_pipeline.py --pipeline all
```

### Method B: Via Local Python
If you are running outside of Docker:
```bash
python scripts/run_pipeline.py --pipeline all
```

### What it does:
- Scans `data/transcripts/demo/` and `data/transcripts/onboarding/`.
- Pairs transcript files by account name.
- Generates `v1` (Demo), `v2` (Onboarding), and a `changelog.md` for every account in `outputs/accounts/`.

---

## 📂 5. Folder Mappings (Inside Docker)

If you are modifying scripts or workflows, keep these mappings in mind:
- `/data/transcripts` ➔ `./data`
- `/data/outputs" ➔ `./outputs`
- `/data/scripts` ➔ `./scripts`
- `/data/workflows` ➔ `./workflows`
