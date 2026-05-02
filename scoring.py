# scoring.py
# Rule-based lead scoring from 1-100.
# Four scoring dimensions: source credibility, role seniority,
# pain keyword match depth, and urgency language detection.

SOURCE_SCORES = {
    "G2 Review": 25,
    "LinkedIn Post": 22,
    "ProductHunt Comment": 20,
    "Twitter/X Thread": 18,
    "Reddit r/SaaS": 17,
    "Reddit r/startups": 16,
    "Reddit r/ProductManagement": 14,
}

URGENCY_PHRASES = [
    "there has to be a better way",
    "very open to automation",
    "would pay for itself",
    "burning",
    "exactly what we need",
    "wish there was",
    "need it to actually",
    "any tools actually",
    "need earlier signals",
    "if this actually",
    "better way",
    "serious buyers",
]

SENIORITY_LABELS = {
    "founder": 10,
    "co-founder": 10,
    "ceo": 10,
    "cto": 9,
    "vp": 8,
    "director": 7,
    "head": 7,
    "lead": 6,
    "manager": 5,
}


def _source_score(lead: dict) -> int:
    return SOURCE_SCORES.get(lead.get("source_type", ""), 10)


def _seniority_score(lead: dict) -> int:
    role = lead.get("role", "").lower()
    for title, score in SENIORITY_LABELS.items():
        if title in role:
            return score
    return lead.get("seniority_weight", 5)


def _keyword_match_score(lead: dict, pain_keyword: str) -> int:
    """Score how deeply the user's pain keyword matches the lead's signals."""
    keyword = pain_keyword.lower().strip()
    lead_keywords = [k.lower() for k in lead.get("pain_keywords", [])]
    pain_signal = lead.get("pain_signal", "").lower()

    exact_match_in_list = keyword in lead_keywords
    partial_match_in_list = any(keyword in kw or kw in keyword for kw in lead_keywords)
    match_in_signal = keyword in pain_signal

    if exact_match_in_list and match_in_signal:
        return 30
    elif exact_match_in_list:
        return 25
    elif partial_match_in_list and match_in_signal:
        return 20
    elif partial_match_in_list:
        return 15
    elif match_in_signal:
        return 12
    else:
        return 5


def _urgency_score(lead: dict) -> int:
    """Detect urgency language in the pain signal."""
    signal = lead.get("pain_signal", "").lower()
    for phrase in URGENCY_PHRASES:
        if phrase in signal:
            return 15
    return 5


def score_lead(lead: dict, pain_keyword: str) -> int:
    """
    Compute a lead score from 1-100 across four dimensions:
    - Source credibility (max 25)
    - Role seniority (max 10)
    - Pain keyword match depth (max 30)
    - Urgency language (max 15)
    Remaining 20 points come from base score.
    """
    base = 20
    source = _source_score(lead)
    seniority = _seniority_score(lead)
    keyword = _keyword_match_score(lead, pain_keyword)
    urgency = _urgency_score(lead)
    raw = base + source + seniority + keyword + urgency
    return min(raw, 100)


def get_urgency_level(score: int) -> str:
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    return "Low"


def get_buying_intent_explanation(lead: dict, score: int) -> str:
    source = lead.get("source_type", "an online platform")
    role = lead.get("role", "a professional")
    company = lead.get("company", "their company")
    urgency = get_urgency_level(score)

    if score >= 80:
        return (
            f"This prospect is a {role} at {company} who expressed a direct, active pain point "
            f"via {source}. The language used indicates immediate frustration with an existing "
            f"solution or workflow — a strong in-market buying signal. Urgency: {urgency}."
        )
    elif score >= 60:
        return (
            f"This prospect is a {role} at {company} who surfaced a relevant operational problem "
            f"on {source}. They are evaluating solutions but have not yet committed — a warm "
            f"mid-funnel signal worth engaging now. Urgency: {urgency}."
        )
    else:
        return (
            f"This prospect at {company} is showing early awareness of the problem on {source}. "
            f"They are not yet actively searching for a solution but could be converted with the "
            f"right framing. Urgency: {urgency}."
        )


def get_best_next_action(score: int, source_type: str) -> str:
    if score >= 80:
        return "Send a personalized outreach message within 24 hours referencing their exact pain signal."
    elif score >= 60:
        if "LinkedIn" in source_type:
            return "Connect on LinkedIn, comment on their post with value, then follow up with a DM."
        elif "Reddit" in source_type:
            return "Reply to their Reddit thread with a helpful insight, then send a DM with a sample lead."
        else:
            return "Send a soft outreach with a relevant case study or 3 sample warm leads."
    return "Add to a nurture sequence. Share a relevant resource first before a direct pitch."


def get_outreach_angle(lead: dict) -> str:
    pain = lead.get("pain_signal", "").lower()
    if "onboarding" in pain or "activation" in pain:
        return "Focus on activation drop-off and how warm leads who already show intent convert 3× faster than cold lists."
    elif "churn" in pain or "retention" in pain:
        return "Lead with retention — show how buying-intent signals let you rescue accounts before they decide to leave."
    elif "cold email" in pain or "reply rate" in pain or "outbound" in pain:
        return "Lead with reply rate improvement — warm leads with context get 5–8× higher reply rates than cold lists."
    elif "scoring" in pain or "qualification" in pain or "intent" in pain:
        return "Focus on signal quality over volume — show how buying-intent scoring replaces gut-feel qualification."
    elif "manual" in pain or "time" in pain or "hours" in pain:
        return "Lead with time savings — quantify the hours spent on manual research vs. automated intent detection."
    else:
        return "Focus on pipeline efficiency — warm leads with buying-intent context reduce time-to-close significantly."
