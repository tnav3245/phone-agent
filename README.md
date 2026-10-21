# phone-agent

A personal AI agent that uses the apps already logged in on your iPhone,
like a human thumb, to do things like order Uber Eats or book on Expedia.
It never stores your passwords or card numbers. Every purchase needs two approvals from you:

1. You type **yes** to a summary of the order and total on your PC, and
2. You confirm **Apple Pay with Face ID** on the phone. Software can't do this step.

## How it works

```
 Windows PC                                   iPhone (USB)
┌───────────────────────────┐               ┌──────────────────────────┐
│ run.py  (agent loop)      │ ── tap(x,y) ─▶│ WebDriverAgent           │
│  1. take screenshot       │ ◀─ screen ────│  (Apple's UI-test tool)  │
│  2. ask Claude what next  │               │                          │
│  3. do it, repeat         │               │  Uber Eats, Expedia, ... │
└───────────────────────────┘               └──────────────────────────┘
```

- `phone_agent/wda.py`: talks to WebDriverAgent (screenshot, tap, type, scroll, open app)
- `phone_agent/agent.py`: the Claude loop, the safety rules and the purchase lock
- `phone_agent/apps.json`: the apps the agent may open (add more here)
- `scripts/start_phone.ps1`: connects Windows to the phone
- `test_connection.py`: checks the phone connection without using Claude
- `run.py`: give it a task

## Get started

Follow **[SETUP_WINDOWS.md](SETUP_WINDOWS.md)** step by step. Then:

```powershell
python run.py --step "Open Uber Eats and search for Chipotle. Don't order anything."
```

## Good to know

- **Cost:** each step sends one screenshot to Claude. Expect roughly $0.25 to $1 in API usage
  per order. See console.anthropic.com for actual spend.
- **Terms of service:** many apps prohibit automated use. Use this for your own
  occasional personal orders. Your account could be flagged if you overuse it.
- **Free Apple ID:** WebDriverAgent must be reinstalled with Sideloadly every 7 days.
