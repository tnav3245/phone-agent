"""Give the phone agent a task.

    python run.py "Order my usual from Chipotle on Uber Eats"
    python run.py --step "Search Expedia for flights BOS to MIA on Dec 20"

--step asks you before every tap, which is a good idea for your first runs.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from phone_agent.agent import Agent
from phone_agent.wda import WDA, WDAError


def main():
    load_dotenv()
    p = argparse.ArgumentParser(description="Personal iPhone agent")
    p.add_argument("task", nargs="?", help="What you want done (in quotes)")
    p.add_argument("--step", action="store_true", help="Confirm every action before it happens")
    p.add_argument("--effort", default="medium", choices=["low", "medium", "high"],
                   help="How hard Claude thinks per step (higher = slower and costs more)")
    p.add_argument("--wda-url", default=os.getenv("WDA_URL", "http://localhost:8100"))
    args = p.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is missing. Copy .env.example to .env and paste your key in it.")

    task = args.task or input("What should I do? ").strip()
    if not task:
        return

    phone = WDA(args.wda_url)
    try:
        phone.status()
    except WDAError as e:
        sys.exit(str(e))

    Agent(phone, step_mode=args.step, effort=args.effort).run(task)


if __name__ == "__main__":
    main()
