# signal_fetcher.py
# Live signal fetcher for AI Warm Lead Engine.
# Sources: Reddit via PRAW + Hacker News via Algolia API.

import os
import re
from datetime import datetime, timezone
from typing import List, Dict

import praw
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

REDDIT_SUBREDDITS = [
    "SaaS",
    "startups",
    "entrepreneur",
    "sales",
    "ProductManagement",
    "smallbusiness",
]

HN_API_URL = "https://hn.algolia.com/api/v1/search"

DEFAULT_NICHE = "B2B SaaS"


def _clean_text(text: str) -> str:
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(" ")

    text = re.sub(r"\s+", " ", text)
    text = text.replace("&amp;", "&")
    return text.strip()


def _keyword_list(pain_keyword: str) -> list[str]:
    base = pain_keyword.lower().strip()
    words = [w.strip() for w in re.split(r"[\s,]+", base) if len(w.strip()) > 2]

    related_terms = {
        "lead generation": ["leads", "lead gen", "prospecting", "outbound", "pipeline"],
        "outbound": ["cold email", "sales outreach", "prospecting", "reply rate"],
        "cold email": ["outbound", "reply rate", "deliverability", "sales outreach"],
        "onboarding": ["activation", "trial", "drop-off", "conversion"],
        "churn": ["retention", "customer success", "cancellation", "renewal"],
        "sales": ["pipeline", "prospecting", "qualification", "buyers"],
    }

    extra = related_terms.get(base, [])
    return list(dict.fromkeys([base] + words + extra))


def _infer_customer_type(text: str) -> str:
    text_lower = text.lower()

    if any(x in text_lower for x in ["founder", "cofounder", "co-founder", "startup"]):
        return "founders"
    if any(x in text_lower for x in ["growth", "marketing", "demand gen"]):
        return "growth teams"
    if any(x in text_lower for x in ["sales", "sdr", "ae", "outbound"]):
        return "sales teams"
    if any(x in text_lower for x in ["product", "pm", "activation"]):
        return "product teams"

    return "founders"


def _estimate_seniority(text: str, author_type: str = "User") -> int:
    text_lower = text.lower()

    if any(x in text_lower for x in ["founder", "ceo", "co-founder", "cofounder"]):
        return 10
    if any(x in text_lower for x in ["vp", "head of", "director"]):
        return 8
    if any(x in text_lower for x in ["manager", "lead"]):
        return 6

    if author_type == "HN":
        return 7

    return 6


def _has_buying_intent(text: str, pain_keyword: str) -> bool:
    text_lower = text.lower()
    keyword_lower = pain_keyword.lower()

    intent_phrases = [
        "looking for",
        "any tools",
        "recommend",
        "recommendations",
        "need a tool",
        "need help",
        "struggling with",
        "can't figure out",
        "there has to be",
        "how do you",
        "what do you use",
        "alternative to",
        "best way to",
        "wasting time",
        "manual",
        "pain",
        "problem",
        "issue",
        "frustrated",
        "expensive",
        "broken",
    ]

    keyword_match = keyword_lower in text_lower or any(
        term in text_lower for term in _keyword_list(pain_keyword)
    )

    intent_match = any(phrase in text_lower for phrase in intent_phrases)

    return keyword_match and intent_match


def fetch_reddit_signals(
    pain_keyword: str,
    niche: str = DEFAULT_NICHE,
    limit_per_subreddit: int = 7,
) -> List[Dict]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "warm-lead-engine/1.0")

    if not client_id or not client_secret:
        print("Reddit credentials missing. Skipping Reddit fetch.")
        return []

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    reddit.read_only = True

    leads = []
    search_terms = _keyword_list(pain_keyword)

    for subreddit_name in REDDIT_SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)

        for term in search_terms[:4]:
            try:
                posts = subreddit.search(term, sort="new", limit=limit_per_subreddit)

                for post in posts:
                    title = _clean_text(post.title)
                    body = _clean_text(post.selftext)

                    combined_text = f"{title}. {body}".strip()

                    if len(combined_text) < 80:
                        continue

                    if not _has_buying_intent(combined_text, pain_keyword):
                        continue

                    author_name = post.author.name if post.author else "Anonymous Reddit User"
                    url = f"https://reddit.com{post.permalink}"

                    leads.append(
                        {
                            "name": author_name,
                            "company": "Unknown",
                            "role": "Reddit User",
                            "niche": niche,
                            "customer_type": _infer_customer_type(combined_text),
                            "pain_signal": f"Posted in r/{subreddit_name}: '{combined_text[:350]}'",
                            "source_type": f"Reddit r/{subreddit_name}",
                            "pain_keywords": _keyword_list(pain_keyword),
                            "seniority_weight": _estimate_seniority(combined_text),
                            "url": url,
                            "created_at": datetime.fromtimestamp(
                                post.created_utc, tz=timezone.utc
                            ).isoformat(),
                        }
                    )

            except Exception as e:
                print(f"Reddit fetch error in r/{subreddit_name}: {e}")
                continue

    return _deduplicate_leads(leads)


def fetch_hn_signals(
    pain_keyword: str,
    niche: str = DEFAULT_NICHE,
    hits_per_page: int = 30,
) -> List[Dict]:
    leads = []

    search_terms = _keyword_list(pain_keyword)

    for term in search_terms[:4]:
        try:
            response = requests.get(
                HN_API_URL,
                params={
                    "query": term,
                    "tags": "comment",
                    "hitsPerPage": hits_per_page,
                },
                timeout=12,
            )
            response.raise_for_status()
            hits = response.json().get("hits", [])

            for hit in hits:
                comment_text = _clean_text(hit.get("comment_text", ""))

                if len(comment_text) < 80:
                    continue

                if not _has_buying_intent(comment_text, pain_keyword):
                    continue

                object_id = hit.get("objectID", "")
                author = hit.get("author", "HN User")

                leads.append(
                    {
                        "name": author,
                        "company": "Unknown",
                        "role": "Hacker News Commenter",
                        "niche": niche,
                        "customer_type": _infer_customer_type(comment_text),
                        "pain_signal": f"Hacker News comment: '{comment_text[:350]}'",
                        "source_type": "Hacker News",
                        "pain_keywords": _keyword_list(pain_keyword),
                        "seniority_weight": _estimate_seniority(comment_text, "HN"),
                        "url": f"https://news.ycombinator.com/item?id={object_id}",
                            "created_at": hit.get("created_at", ""),
                    }
                )

        except Exception as e:
            print(f"Hacker News fetch error for term '{term}': {e}")
            continue

    return _deduplicate_leads(leads)


def _deduplicate_leads(leads: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []

    for lead in leads:
        key = lead.get("url") or lead.get("pain_signal", "")[:120]

        if key in seen:
            continue

        seen.add(key)
        unique.append(lead)

    return unique


def fetch_live_signals(
    pain_keyword: str,
    niche: str = DEFAULT_NICHE,
    max_results: int = 30,
) -> List[Dict]:
    reddit_leads = fetch_reddit_signals(
        pain_keyword=pain_keyword,
        niche=niche,
        limit_per_subreddit=5,
    )

    hn_leads = fetch_hn_signals(
        pain_keyword=pain_keyword,
        niche=niche,
        hits_per_page=25,
    )

    combined = reddit_leads + hn_leads
    return _deduplicate_leads(combined)[:max_results]
