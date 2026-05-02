# AI Warm Lead Engine

A simple Python + Streamlit MVP that generates warm lead opportunities from either mock data or live Reddit + Hacker News signals.

## Features

- Enter a niche, customer type, and pain keyword
- Generate 5 warm leads from mock data or live Reddit + Hacker News data
- View each lead's name, company, role, pain signal, source type, warm-lead reason, outreach message, and score
- Download generated leads as CSV from Streamlit
- Export generated leads to `leads_output.csv` from the CLI test
- Download an Opportunity Audit Markdown report from Streamlit
- Export the audit report to `opportunity_audit.md` from the CLI test

## Project Files

```text
ai-warm-lead-engine/
|-- app.py
|-- audit_report.py
|-- lead_engine.py
|-- signal_fetcher.py
|-- scoring.py
|-- sample_data.py
|-- requirements.txt
|-- test_flow.py
`-- README.md
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Live Data Setup

Live mode uses official/free APIs only:

- Reddit official OAuth API
- Hacker News public Firebase API

It does not scrape LinkedIn, G2, or Twitter/X.

For Reddit, copy `.env.example` to `.env` and add your Reddit API credentials:

```text
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=ai-warm-lead-engine/0.1 by your_reddit_username
```

If Reddit credentials are missing or live APIs return no matches, the app falls back to mock data so the dashboard still works.

Run the CLI logic test and write `leads_output.csv` and `opportunity_audit.md`:

```bash
python test_flow.py
```

## Exports

- `leads_output.csv`: generated lead list with score, pain signal, source type, warm-lead reason, and outreach message.
- `opportunity_audit.md`: Markdown report with executive summary, target niche, total leads found, top 3 strongest leads, common pain signals, outreach strategy, and next steps.

## Example Inputs

- Niche: `B2B SaaS`
- Customer type: `founders`
- Pain keyword: `onboarding`

## Notes

The scoring rules remain in `scoring.py`. Live Reddit and Hacker News signals are normalized into the same lead shape before scoring, export, and audit generation.
