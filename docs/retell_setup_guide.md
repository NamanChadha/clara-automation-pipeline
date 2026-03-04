# Retell Agent Setup Guide — Clara Automation Pipeline

This guide explains how to take the generated agent specs and set them up in Retell AI.

---

## Free Tier Overview

Retell AI offers a free tier with **$10 in credits** — enough to test our agents without spending any additional money.

Sign up at: https://app.retellai.com

---

## Option A: Manual Import (Recommended for Free Tier)

Since the free tier may not support programmatic agent creation via API, you can manually set up agents using our generated JSON specs.

### Step 1: Open the Agent Spec

Navigate to the generated output for your account:

```
outputs/accounts/<account_id>/v2/agent_spec.json
```

For example:
```
outputs/accounts/bens_electric_solutions/v2/agent_spec.json
```

### Step 2: Create Agent in Retell Dashboard

1. Go to https://app.retellai.com
2. Navigate to **Agents** → **Create Agent**
3. Set the following from the JSON:

| JSON Field | Retell Setting |
|------------|---------------|
| `agent_name` | Agent Name |
| `language` | Language |
| `voice_id` | Voice Selection |
| `voice_speed` | Speech Speed |
| `voice_temperature` | Voice Temperature |
| `responsiveness` | Responsiveness |
| `interruption_sensitivity` | Interruption Sensitivity |
| `enable_backchannel` | Enable Backchannel |

### Step 3: Set Up the Response Engine

1. In the agent settings, go to **Response Engine**
2. Select **Retell LLM** as the engine type
3. Create a new LLM configuration
4. Paste the content of `response_engine.system_prompt` from the JSON into the **System Prompt** field
5. Save

### Step 4: Configure Tools (Optional)

The generated spec includes tool definitions (`tool_invocations` field). If you want functional call transfers:

1. In the LLM configuration, go to **Tools**
2. Add a **Transfer Call** tool
3. Map the phone numbers from the `call_transfer_protocol.emergency_chain` field

### Step 5: Test the Agent

1. Click **Test Call** in the Retell dashboard
2. Simulate both emergency and non-emergency scenarios
3. Verify the agent follows the correct flow:
   - Proper greeting
   - Emergency vs non-emergency detection
   - Call routing/transfer
   - Information collection
   - Fallback messaging

---

## Option B: API Import (Works If Free Tier Allows)

If your Retell plan supports API-based agent creation:

```python
import requests
import json

RETELL_API_KEY = "your-api-key-here"

# Load the generated spec
with open("outputs/accounts/bens_electric_solutions/v2/agent_spec.json") as f:
    spec = json.load(f)

# Create agent via API
response = requests.post(
    "https://api.retellai.com/create-agent",
    headers={
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "agent_name": spec["agent_name"],
        "voice_id": spec["voice_id"],
        "language": spec["language"],
        "response_engine": {
            "type": "retell-llm",
            "llm_id": "YOUR_LLM_ID",
        },
    },
)

print(response.json())
```

---

## Testing Checklist

For each agent, verify these scenarios:

- [ ] **Business hours greeting**: Agent gives correct company greeting
- [ ] **After-hours greeting**: Agent notes office is closed
- [ ] **Emergency detection**: Agent correctly identifies emergencies
- [ ] **Emergency routing**: Agent transfers to on-call chain
- [ ] **Non-emergency handling**: Agent collects info and offers callback
- [ ] **Excluded services**: Agent declines and recommends alternatives
- [ ] **Fallback**: If no one answers, appropriate message is given
- [ ] **No internal tool disclosure**: Agent never mentions ServiceTrade, tools, etc. to caller
