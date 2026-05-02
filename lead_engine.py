# lead_engine.py
# Coordinates lead generation: fetch, filter, score, enrich, return top leads.

from sample_data import SAMPLE_LEADS
from signal_fetcher import fetch_live_signals

from scoring import (
    score_lead,
    get_urgency_level,
    get_buying_intent_explanation,
    get_best_next_action,
    get_outreach_angle,
)


def _build_outreach_message(lead, niche, pain_keyword):
    name_first = lead.get("name", "there").split()[0]
    source = lead.get("source_type", "online")
    company = lead.get("company", "your company")
    url = lead.get("url", "")

    pain_short = lead.get("pain_signal", "")[:160].rstrip(",. ") + "..."

    source_line = f"\n\nSource I found: {url}" if url else ""

    return (
        f"Hi {name_first}, I came across your post on {source} where you mentioned: "
        f'"{pain_short}" — that caught my attention.\n\n'
        f"I’m building warm-lead intelligence for {niche} teams that are dealing with "
        f"{pain_keyword}. Instead of sending hundreds of cold messages, the system finds "
        f"people already showing public buying-intent signals around the exact pain.\n\n"
        f"I put together a quick signal-based lead audit that could help {company}. "
        f"Would it be useful if I sent over 3 sample leads with scores, source context, "
        f"and suggested outreach angles?"
        f"{source_line}"
    )


def _matches(lead, niche, customer_type, pain_keyword):
    niche = niche.lower().strip()
    customer_type = customer_type.lower().strip()
    pain_keyword = pain_keyword.lower().strip()

    niche_match = niche in lead.get("niche", "").lower()

    ctype_match = (
        customer_type in lead.get("customer_type", "").lower()
        or customer_type in lead.get("role", "").lower()
        or any(customer_type in kw.lower() for kw in lead.get("pain_keywords", []))
    )

    pain_match = (
        pain_keyword in lead.get("pain_signal", "").lower()
        or any(
            pain_keyword in kw.lower() or kw.lower() in pain_keyword
            for kw in lead.get("pain_keywords", [])
        )
    )

    return sum([niche_match, ctype_match, pain_match]) >= 1


def _enrich_lead(lead, niche, pain_keyword):
    score = score_lead(lead, pain_keyword)

    enriched = {
        "name": lead.get("name", "Unknown"),
        "company": lead.get("company", "Unknown"),
        "role": lead.get("role", "Unknown"),
        "pain_signal": lead.get("pain_signal", ""),
        "source_type": lead.get("source_type", "Unknown"),
        "source_url": lead.get("url", ""),
        "created_at": lead.get("created_at", ""),
        "why_warm_lead": (
            f"This prospect surfaced a public pain signal around '{pain_keyword}' via "
            f"{lead.get('source_type', 'an online source')}. The signal suggests active "
            f"frustration, research, or potential buying intent."
        ),
        "outreach_message": _build_outreach_message(lead, niche, pain_keyword),
        "score": score,
        "urgency_level": get_urgency_level(score),
        "buying_intent_explanation": get_buying_intent_explanation(lead, score),
        "best_next_action": get_best_next_action(score, lead.get("source_type", "")),
        "outreach_angle": get_outreach_angle(lead),
    }

    return enriched


def generate_leads(
    niche,
    customer_type,
    pain_keyword,
    mode="live",
    max_results=5,
):
    """
    mode='mock' uses sample_data.py.
    mode='live' uses Reddit + Hacker News.
    """

    if mode == "mock":
        raw_leads = SAMPLE_LEADS
    else:
        raw_leads = fetch_live_signals(
            pain_keyword=pain_keyword,
            niche=niche,
            max_results=40,
        )

        # Fallback if live APIs return too little data.
        if len(raw_leads) < 3:
            raw_leads = SAMPLE_LEADS

    filtered = [
        lead
        for lead in raw_leads
        if _matches(lead, niche, customer_type, pain_keyword)
    ]

    if len(filtered) < max_results:
        filtered = raw_leads

    enriched = [_enrich_lead(lead, niche, pain_keyword) for lead in filtered]
    enriched.sort(key=lambda x: x["score"], reverse=True)

    return enriched[:max_results]
