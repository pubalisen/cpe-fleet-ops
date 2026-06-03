# CPE Fleet Ops Agent — ADK 2.0 Multi-Agent System

> Chrome Enterprise fleet management powered by Google ADK 2.0 multi-agent architecture.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                 CPE Fleet Ops Orchestrator (LlmAgent)            │
│   Routes requests to the appropriate fleet management workflow   │
├────────────┬────────────────┬───────────────┬───────────────────┤
│            │                │               │                   │
│  Sequential│   Loop         │   Parallel    │   Skills          │
│  Support   │   Policy       │   Security    │   Toolset         │
│  Intake    │   Automation   │   Posture     │                   │
│            │                │               │                   │
│  Triage    │  Drafter       │  DLP Check    │  enrollment       │
│    ↓       │    ↓           │  Extension    │  chrome-policy    │
│  Diagnose  │  Validator     │  Compliance   │  runbook-creator  │
│    ↓       │    ↓ (loop)    │               │                   │
│  Resolve   │  Stage         │               │                   │
└────────────┴────────────────┴───────────────┴───────────────────┘
```

## Workflows

| Workflow | ADK Pattern | Use Case |
|---|---|---|
| **Support Intake** | SequentialAgent | Triage → Diagnose → Resolve device/policy/extension issues |
| **Policy Automation** | LoopAgent | Draft ↔ Validate Chrome/ChromeOS policy changes iteratively |
| **Security Posture** | ParallelAgent | DLP + Extension + Compliance audits concurrently |
| **Knowledge** | SkillToolset | Policy reference, enrollment playbook, runbook creation |

## Skills

| Skill | Type | Description |
|---|---|---|
| `chrome-policy-quick-ref` | Inline | 50+ common policies with values and scopes |
| `chrome-policy-reference` | File-based | Full policy catalog with platform support |
| `enrollment-playbook` | File-based | Enrollment procedures and troubleshooting |
| `runbook-creator` | Meta | Generates new operational runbooks from requirements |

## Evaluation

2 eval sets with 12 total test cases:

| Eval Set | Cases | What It Tests |
|---|---|---|
| `response_quality` | 6 | Semantic correctness of responses across all workflows |
| `routing_accuracy` | 6 | Correct routing of requests to appropriate workflows |

## Quick Start

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
adk web app

# Run evaluations
adk eval app app/response_quality.evalset.json --config_file_path evals/eval_config.json
adk eval app app/routing_accuracy.evalset.json --config_file_path evals/eval_config.json
```

## Deploy to Cloud Run

```bash
gcloud run deploy cpe-fleet-ops \
  --source=. \
  --project=mygenerativeai \
  --region=us-central1 \
  --port=8080 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=mygenerativeai,GOOGLE_CLOUD_LOCATION=us-central1,ADK_FORCE_LOCAL_STORAGE=1" \
  --memory=2Gi \
  --timeout=300
```

## Test Prompts

```
# Support Intake
"Our Chromebooks won't enroll after a powerwash. About 15 devices affected."

# Policy Automation
"Block personal Google accounts on managed Chrome browsers in the Sales OU."

# Security Audit
"Run a full security audit on our Chrome fleet configuration."

# Knowledge
"What policy controls USB storage access on ChromeOS?"
```

## Tech Stack

- **SDK**: Google ADK 2.1.0
- **Model**: Gemini 2.5 Flash
- **Platform**: Vertex AI / Cloud Run
- **Grounding**: Vertex AI Search + Skills
