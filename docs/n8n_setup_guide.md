# n8n Setup Guide — Clara Automation Pipeline

This guide walks you through setting up and running the n8n workflow automation layer.

## Prerequisites

- Docker and Docker Compose installed
- Pipeline Python scripts working (test with `python scripts/run_pipeline.py --pipeline all` first)

---

## Step 1: Start n8n

```bash
docker-compose up n8n -d
```

Wait 10-15 seconds for n8n to initialize, then open: **http://localhost:5678**

Login credentials (from `.env`):
- **Username**: `admin`
- **Password**: `changeme`

---

## Step 2: Import Workflows

1. In the n8n dashboard, click **"+ Add Workflow"**
2. Click the **"..."** menu (top right) → **Import from File**
3. Select `workflows/pipeline_a_demo_to_agent.json`
4. Click **Save**
5. Repeat for `workflows/pipeline_b_onboarding_update.json`

---

## Step 3: Activate Workflows

1. Open each workflow
2. Toggle the **Active** switch to ON
3. The webhook URLs will be displayed in the Webhook node

---

## Step 4: Trigger Pipeline A (Demo → v1)

Send a POST request to the Pipeline A webhook:

```bash
curl -X POST http://localhost:5678/webhook/pipeline-a \
  -H "Content-Type: application/json" \
  -d '{"transcript_path": "/data/data/transcripts/demo/bens_electric_demo.txt"}'
```

Expected response:
```json
{
  "account_id": "bens_electric_solutions",
  "company_name": "Ben's Electric Solutions",
  "memo_path": "outputs/accounts/bens_electric_solutions/v1/account_memo.json",
  "spec_path": "outputs/accounts/bens_electric_solutions/v1/agent_spec.json",
  "status": "success",
  "pipeline": "A",
  "version": "v1"
}
```

---

## Step 5: Trigger Pipeline B (Onboarding → v2)

```bash
curl -X POST http://localhost:5678/webhook/pipeline-b \
  -H "Content-Type: application/json" \
  -d '{"transcript_path": "/data/data/transcripts/onboarding/bens_electric_onboarding.txt"}'
```

Expected response:
```json
{
  "account_id": "bens_electric_solutions",
  "company_name": "Ben's Electric Solutions",
  "memo_path": "outputs/accounts/bens_electric_solutions/v2/account_memo.json",
  "spec_path": "outputs/accounts/bens_electric_solutions/v2/agent_spec.json",
  "changelog_path": "outputs/accounts/bens_electric_solutions/changelog.md",
  "total_changes": 13,
  "status": "success"
}
```

---

## Step 6: Batch Processing

To process all transcripts, you can use the CLI runner directly:

```bash
# Inside Docker
docker-compose run pipeline python scripts/run_pipeline.py --pipeline all

# Or locally
python scripts/run_pipeline.py --pipeline all
```

---

## Architecture Notes

- **n8n** acts as the orchestration layer, calling Python scripts via `executeCommand` nodes
- The Python scripts are mounted into n8n's container at `/data/`
- Outputs are written to the shared `outputs/` volume
- Both workflows use webhook triggers so they can be called from external systems (Fireflies, Zapier, etc.)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| n8n won't start | Check Docker is running: `docker ps` |
| Webhook not responding | Ensure workflow is activated (toggle ON) |
| Python command fails | Check `/data/scripts/` path inside container |
| Permission denied | Ensure volume mounts have correct permissions |
