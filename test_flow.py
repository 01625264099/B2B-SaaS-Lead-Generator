# test_flow.py
# Run with: python test_flow.py

import sys
from pathlib import Path

LOCAL_PACKAGES = Path(__file__).resolve().parent / ".python-packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

from lead_engine import generate_leads
from audit_report import generate_audit_report
import csv

NICHE = "B2B SaaS"
CUSTOMER_TYPE = "founders"
PAIN_KEYWORD = "lead generation"

leads = generate_leads(
    niche=NICHE,
    customer_type=CUSTOMER_TYPE,
    pain_keyword=PAIN_KEYWORD,
    mode="live",
    max_results=5,
)

if not leads:
    print("No leads found.")
    raise SystemExit

print("\nLIVE WARM LEADS\n")

for i, lead in enumerate(leads, 1):
    print(f"#{i}")
    print(f"Name: {lead['name']}")
    print(f"Company: {lead['company']}")
    print(f"Role: {lead['role']}")
    print(f"Score: {lead['score']}")
    print(f"Urgency: {lead['urgency_level']}")
    print(f"Source: {lead['source_type']}")
    print(f"URL: {lead.get('source_url', '')}")
    print("-" * 60)

with open("leads_output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=leads[0].keys())
    writer.writeheader()
    writer.writerows(leads)

with open("opportunity_audit.md", "w", encoding="utf-8") as f:
    f.write(generate_audit_report(NICHE, CUSTOMER_TYPE, PAIN_KEYWORD, leads))

print("\nDone.")
print("Created: leads_output.csv")
print("Created: opportunity_audit.md")
