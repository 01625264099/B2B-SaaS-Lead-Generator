# app.py
# Streamlit B2B SaaS dashboard for the AI Warm Lead Engine.

import io
import sys
from pathlib import Path

LOCAL_PACKAGES = Path(__file__).resolve().parent / ".python-packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

import pandas as pd
import streamlit as st

from audit_report import generate_audit_report
from lead_engine import generate_leads


st.set_page_config(
    page_title="AI Warm Lead Engine",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main { background-color: #0f1117; }
        .stApp { background-color: #0f1117; }
        .metric-card {
            background: linear-gradient(135deg, #1a1d2e, #16213e);
            border: 1px solid #2d3561;
            border-radius: 12px;
            padding: 20px 24px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #4ade80;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        div[data-testid="stExpander"] {
            background: #1a1d2e;
            border: 1px solid #2d3561;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .stTextInput > div > div > input {
            background-color: #1a1d2e;
            color: #f1f5f9;
            border: 1px solid #2d3561;
        }
        section[data-testid="stSidebar"] {
            background-color: #0d1117;
            border-right: 1px solid #1e293b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## AI Warm Lead Engine")
    st.markdown("*Find prospects already showing buying intent before your competitors do.*")
    st.divider()

    st.markdown("### Search Criteria")
    data_mode_label = st.sidebar.radio(
        "Data Mode",
        ["Live: Reddit + Hacker News", "Mock: Sample Data"],
        index=0,
    )
    data_mode = "live" if data_mode_label.startswith("Live") else "mock"
    if data_mode == "live":
        st.sidebar.info("Live mode searches Reddit + Hacker News for recent public buying-intent signals.")
    else:
        st.sidebar.warning("Mock mode uses sample data only. Do not use mock data for client delivery.")
    niche = st.text_input(
        "Target Niche",
        value="B2B SaaS",
        placeholder="e.g. B2B SaaS, eCommerce, Agencies",
    )
    customer_type = st.text_input(
        "Customer Type",
        value="founders",
        placeholder="e.g. founders, sales teams, agencies",
    )
    pain_keyword = st.text_input(
        "Pain Keyword",
        value="lead generation",
        placeholder="e.g. lead generation, churn, onboarding",
    )

    st.divider()
    run_button = st.button("Find Warm Leads", use_container_width=True, type="primary")

    st.divider()
    st.markdown(
        "<small style='color:#64748b'>Live mode uses Reddit and Hacker News only. "
        "Reddit requires official API credentials in .env. No LinkedIn, G2, or Twitter/X scraping.</small>",
        unsafe_allow_html=True,
    )


if "leads" not in st.session_state:
    st.session_state.leads = []
if "niche" not in st.session_state:
    st.session_state.niche = ""
if "customer_type" not in st.session_state:
    st.session_state.customer_type = ""
if "pain_keyword" not in st.session_state:
    st.session_state.pain_keyword = ""
if "data_source" not in st.session_state:
    st.session_state.data_source = ""


if run_button:
    if not niche.strip() or not customer_type.strip() or not pain_keyword.strip():
        st.error("Please fill in all three search fields before running.")
    else:
        with st.spinner("Scanning Reddit and Hacker News intent signals..."):
            leads = generate_leads(
                niche=niche,
                customer_type=customer_type,
                pain_keyword=pain_keyword,
                mode=data_mode,
                max_results=5,
            )
            st.session_state.leads = leads
            st.session_state.niche = niche
            st.session_state.customer_type = customer_type
            st.session_state.pain_keyword = pain_keyword
            st.session_state.data_source = data_mode_label


st.markdown("# AI Warm Lead Engine")
st.markdown(
    f"**Target:** {st.session_state.niche or '-'} &nbsp;|&nbsp; "
    f"**Customer:** {st.session_state.customer_type or '-'} &nbsp;|&nbsp; "
    f"**Pain:** {st.session_state.pain_keyword or '-'} &nbsp;|&nbsp; "
    f"**Source:** {st.session_state.data_source or '-'}"
)
st.divider()

leads = st.session_state.leads

if not leads:
    st.info("Enter your search criteria in the sidebar and click Find Warm Leads to start.")
    st.stop()


st.markdown("## Lead Summary Metrics")
avg_score = round(sum(l["score"] for l in leads) / len(leads), 1)
max_score = max(l["score"] for l in leads)
high_intent_count = sum(1 for l in leads if l["urgency_level"] == "High")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{len(leads)}</div>'
        f'<div class="metric-label">Warm Leads Found</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{avg_score}</div>'
        f'<div class="metric-label">Average Lead Score</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{max_score}</div>'
        f'<div class="metric-label">Highest Lead Score</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{high_intent_count}</div>'
        f'<div class="metric-label">High-Intent Leads</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


st.markdown("## Warm Lead Results")

for i, lead in enumerate(leads, 1):
    with st.expander(f"#{i} - {lead['name']} | {lead['company']} | Score: {lead['score']}/100"):
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown(f"**Role:** {lead['role']}")
            st.markdown(f"**Source:** {lead['source_type']}")
            if lead.get("source_url"):
                st.markdown(f"**Source URL:** {lead['source_url']}")
            st.markdown(f"**Urgency Level:** `{lead['urgency_level']}`")
        with col_b:
            st.metric("Lead Score", f"{lead['score']} / 100")

        st.markdown("**Pain Signal Detected:**")
        st.info(lead["pain_signal"])

        st.markdown("**Why This Is a Warm Lead:**")
        st.markdown(lead["buying_intent_explanation"])

        st.markdown("**Outreach Angle:**")
        st.markdown(lead["outreach_angle"])

        st.markdown("**Best Next Action:**")
        st.success(lead["best_next_action"])


st.markdown("## Outreach Messages")
st.markdown("*Copy these personalized messages. Each references the prospect's actual pain signal.*")

for i, lead in enumerate(leads, 1):
    with st.expander(f"#{i} - {lead['name']} @ {lead['company']}"):
        st.code(lead["outreach_message"], language=None)


st.markdown("## Export Results")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    df = pd.DataFrame(st.session_state["leads"])
    if "source_url" not in df.columns:
        df["source_url"] = ""
    st.download_button(
        label="Download Leads CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="warm_leads.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_exp2:
    audit_md = generate_audit_report(
        st.session_state.niche,
        st.session_state.customer_type,
        st.session_state.pain_keyword,
        leads,
    )
    st.download_button(
        label="Download Opportunity Audit (Markdown)",
        data=audit_md,
        file_name="opportunity_audit.md",
        mime="text/markdown",
        use_container_width=True,
    )


st.markdown("## Opportunity Audit Preview")
with st.expander("View Full Opportunity Audit Report"):
    audit_md = generate_audit_report(
        st.session_state.niche,
        st.session_state.customer_type,
        st.session_state.pain_keyword,
        leads,
    )
    st.markdown(audit_md)

st.divider()
st.markdown(
    "<small style='color:#475569'>AI Warm Lead Engine - MVP v1.0 | "
    "Live warm leads powered by Reddit and Hacker News public APIs.</small>",
    unsafe_allow_html=True,
)
