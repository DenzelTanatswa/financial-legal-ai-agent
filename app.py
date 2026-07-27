import json

import streamlit as st
from dotenv import load_dotenv

from AI.analysis import analyze_document
from Components.sidebar import show_sidebar
from Utilis import extract_text
from Utilis.document_classifier import classify_document
from Utilis.document_router import route_document
from Utilis.entity_extractor import extract_entities
from Utilis.file_handler import save_uploaded_file

load_dotenv()

st.set_page_config(page_title="Aureon | Intelligence Studio", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17233c; --muted:#72809a; --line:#dfe5ef; --canvas:#f7f8fc; --navy:#15264a; --teal:#08a6a6; --mint:#dff7f3; --violet:#7158e7; }
* { font-family:'Manrope',sans-serif; }.stApp { background:var(--canvas); color:var(--ink); }.block-container { max-width:1440px; padding:2.1rem 3.2rem 3.2rem; } [data-testid="stHeader"] { background:rgba(247,248,252,.88); }
[data-testid="stSidebar"] { background:#102140; border-right:1px solid #233859; } [data-testid="stSidebar"] > div:first-child { padding:1.8rem 1rem 1rem; }
.sidebar-brand { display:flex; gap:10px; align-items:center; color:white; padding:0 10px 2rem; }.brand-mark { width:34px; height:34px; display:grid; place-items:center; border-radius:10px; background:linear-gradient(135deg,#1bd0c2,#4d74e8); font-weight:800; }.brand-name { font-size:1.15rem; font-weight:800; letter-spacing:-.06em; }.brand-subtitle,.sidebar-label { font:500 .61rem 'DM Mono',monospace; letter-spacing:.14em; color:#8fa4c6; }.sidebar-label { padding:0 10px; margin:1.55rem 0 .65rem; }.agent-label { margin-top:2rem; }.nav-item,.network-agent { color:#b8c8df; padding:10px; border-radius:8px; font-size:.83rem; margin:3px 0; }.nav-item span,.network-agent span { display:inline-block; width:25px; color:#70ded4; font-size:1rem; }.nav-active { background:#20375d; color:#fff; font-weight:700; }.agent-card { display:flex; align-items:center; gap:10px; padding:12px 10px; border:1px solid #2c466e; background:#1a3156; border-radius:10px; color:#fff; }.agent-card small { display:block; color:#8fa4c6; font-size:.68rem; margin-top:2px; }.agent-symbol { color:#70ded4; font-size:1.25rem; }.status-dot,.pulse-dot { width:7px; height:7px; border-radius:50%; background:#4ee1a2; margin-left:auto; box-shadow:0 0 0 3px rgba(78,225,162,.14); }.network-active { background:#1b3257; color:#fff; }.sidebar-footer { margin:2.5rem 10px 0; padding-top:16px; border-top:1px solid #2a4267; color:#8fa4c6; font-size:.68rem; display:flex; align-items:center; gap:8px; }.sidebar-footer .pulse-dot { margin:0; width:6px; height:6px; }
.topline { display:flex; justify-content:space-between; align-items:center; font:500 .68rem 'DM Mono',monospace; color:var(--muted); letter-spacing:.06em; }.secure-pill { color:#26736e; background:var(--mint); border-radius:999px; padding:6px 10px; }.hero { margin:1.5rem 0 2rem; }.eyebrow,.section-header { font:500 .67rem 'DM Mono',monospace; letter-spacing:.12em; color:var(--teal); margin:0 0 .65rem; }.hero h1 { font-size:clamp(2rem,3vw,3.15rem); line-height:1.12; letter-spacing:-.065em; margin:0; color:var(--ink); }.hero p { color:var(--muted); margin:.8rem 0 0; font-size:.95rem; }
.metric-card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1.15rem 1.2rem; min-height:122px; box-shadow:0 7px 18px rgba(25,42,70,.035); }.metric-top { display:flex; align-items:center; justify-content:space-between; }.metric-icon { width:30px; height:30px; display:grid; place-items:center; border-radius:8px; background:#f0f3fa; color:var(--violet); font-weight:800; }.metric-delta { color:#147b70; background:#e5f7f2; padding:4px 7px; border-radius:5px; font:500 .61rem 'DM Mono',monospace; }.metric-label { color:var(--muted); font-size:.72rem; font-weight:600; margin-top:.9rem; }.metric-value { color:var(--ink); font-size:1.7rem; line-height:1.25; font-weight:800; letter-spacing:-.06em; }
.work-panel { background:#fff; border:1px solid var(--line); border-radius:16px; padding:1.45rem; box-shadow:0 8px 28px rgba(25,42,70,.04); }.panel-title { font-weight:800; letter-spacing:-.04em; font-size:1rem; margin:0 0 .25rem; }.panel-copy { color:var(--muted); font-size:.78rem; margin:0 0 1.25rem; } [data-testid="stFileUploader"] { border:1.5px dashed #a9b8d1; border-radius:12px; background:#f9fbff; padding:.3rem; } [data-testid="stFileUploader"] section { padding:1.3rem 1rem; } [data-testid="stFileUploader"] button { border-color:#cbd5e5; color:var(--navy); border-radius:7px; } [data-testid="stTextInput"] input { border-color:#d4ddea; border-radius:8px; font-size:.82rem; }.stToggle label { font-size:.78rem!important; color:#506079!important; }.stButton > button { border-radius:8px; font-weight:800; letter-spacing:.01em; min-height:2.7rem; background:linear-gradient(100deg,#167f91,#4e5fce); border:0; box-shadow:0 7px 14px rgba(49,89,173,.2); }.stButton > button:hover { background:linear-gradient(100deg,#126d7b,#4452b7); transform:translateY(-1px); }
.results-head { display:flex; align-items:center; justify-content:space-between; margin-top:2.25rem; }.results-kicker { font:500 .67rem 'DM Mono',monospace; color:var(--muted); letter-spacing:.1em; }.live-badge { border:1px solid #b7e6dc; border-radius:999px; color:#147b70; background:#effbf8; padding:5px 9px; font-size:.67rem; font-weight:700; }.analysis-box { background:linear-gradient(135deg,#14284c,#243b69); border-radius:16px; padding:3.5rem 2rem; min-height:245px; color:#c4d1e7; overflow:hidden; position:relative; }.analysis-box:after { content:''; position:absolute; width:280px; height:280px; right:-70px; top:-130px; border-radius:50%; background:radial-gradient(circle,#35cbbb22,transparent 68%); }.empty-symbol { width:50px; height:50px; display:grid; place-items:center; background:#ffffff12; border:1px solid #ffffff20; border-radius:14px; font-size:1.35rem; }.stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--line); }.stTabs [data-baseweb="tab"] { color:var(--muted); font-size:.78rem; padding:.7rem .85rem; }.stTabs [aria-selected="true"] { color:var(--teal)!important; font-weight:800; }.stTabs [data-baseweb="tab-highlight"] { background:var(--teal); } @media (max-width:700px) { .block-container { padding:1.25rem; }.topline { display:none; } }
</style>
""", unsafe_allow_html=True)

detected_agent = st.session_state.get("detected_agent")
show_sidebar(detected_agent)

st.markdown('<div class="topline"><span>INTELLIGENCE WORKSPACE / 2026</span><span class="secure-pill">● ENCRYPTED &amp; PRIVATE</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">DOCUMENT INTELLIGENCE</div><h1>Decisions, clarified.</h1><p>Turn complex financial and legal documents into clear, defensible insight.</p></div>', unsafe_allow_html=True)

metrics = [("◈", "Documents analyzed", "128", "+12 this week"), ("◫", "Contracts reviewed", "45", "+3 this week"), ("▣", "Invoices processed", "67", "+8 this week"), ("✓", "Compliance checks", "34", "+5 this week")]
for col, (icon, label, value, delta) in zip(st.columns(4), metrics):
    col.markdown(f'<div class="metric-card"><div class="metric-top"><div class="metric-icon">{icon}</div><div class="metric-delta">↑ {delta}</div></div><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
left, right = st.columns([2, 1], gap="large")
with left:
    st.markdown('<div class="work-panel"><p class="panel-title">Add a document</p><p class="panel-copy">PDF, Word, text, spreadsheets — your specialist is selected automatically.</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "csv", "xlsx"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"{uploaded_file.name} is ready for analysis")
    st.markdown('</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="work-panel"><p class="panel-title">Review settings</p><p class="panel-copy">Configure the output for this analysis.</p>', unsafe_allow_html=True)
    st.info(f"**{detected_agent}**" if detected_agent else "A specialist will be selected after upload.", icon="🤖")
    detailed = st.toggle("Detailed report", value=True)
    export = st.toggle("Export results", value=False)
    question = st.text_input("Review focus", value="Summarize this document.")
    run = st.button("Run analysis", type="primary", use_container_width=True, disabled=not uploaded_file)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="results-head"><div><div class="results-kicker">ANALYSIS CONSOLE</div><h3 style="margin:.35rem 0 0;letter-spacing:-.04em">Review findings</h3></div><div class="live-badge">● READY</div></div>', unsafe_allow_html=True)

if run:
    with st.spinner(f"Classifying and analysing {uploaded_file.name}…"):
        filepath = save_uploaded_file(uploaded_file)
        extracted = extract_text(filepath)
        doc_type = classify_document(extracted)
        entities = extract_entities(extracted)
        routed = route_document(doc_type)
        st.session_state.detected_agent = routed
        result = analyze_document(text=extracted, document_type=doc_type, question=question)

    structured = result["structured"]
    confidence = result["confidence_score"]
    rationale = result["confidence_rationale"]
    steps = result["reasoning_steps"]
    risks = structured.get("risks", [])
    findings = structured.get("key_findings", [])
    recommendations = structured.get("recommendations", [])
    validation_report = result.get("validation_report")
    collab_agents = result.get("collaborating_agents", [])
    agent_responses = result.get("agent_responses", [])
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Key findings", "Risk flags", "Reasoning", "Validation"])
    with tab1:
        st.markdown(f"**Document:** `{uploaded_file.name}`  \\n+**Detected type:** {doc_type}  \\n+**Assigned specialist:** {routed}  \\n+**Mode:** {'Detailed' if detailed else 'Standard'}")
        color = "#22a06b" if confidence >= .75 else "#d99013" if confidence >= .5 else "#d74a49"
        st.markdown(f"**Confidence:** <span style='color:{color};font-weight:800'>{confidence:.0%}</span>", unsafe_allow_html=True)
        st.progress(confidence, text=rationale or "")
        st.markdown("**Executive summary**")
        st.markdown(result["summary"])
        with st.expander("Extracted text preview"):
            st.text(extracted[:3000] + ("…" if len(extracted) > 3000 else ""))
    with tab2:
        st.markdown(f"**Amounts:** {', '.join(entities['Amounts']) or 'None'}  \\n+**Dates:** {', '.join(entities['Dates']) or 'None'}  \\n+**Emails:** {', '.join(entities['Emails']) or 'None'}")
        for item in findings: st.markdown(f"- {item}")
        if recommendations:
            st.markdown("**Recommendations**")
            for item in recommendations: st.markdown(f"- {item}")
    with tab3:
        if risks:
            for risk in risks:
                severity, description = risk.get("severity", "LOW").upper(), risk.get("description", "")
                label = f"{severity} — {description}"
                (st.error if severity == "HIGH" else st.warning if severity == "MEDIUM" else st.info)(label)
        else: st.success("No risk flags identified.")
    with tab4:
        for step in steps:
            with st.expander(f"Step {step.get('step', '?')}: {step.get('action', '')}"):
                st.markdown(step.get("observation", ""))
        if collab_agents and detailed:
            st.markdown("**Collaborating specialists:** " + ", ".join(collab_agents))
            for response in agent_responses:
                with st.expander(response.get("agent_name", "Specialist")):
                    st.markdown(response.get("summary", ""))
    with tab5:
        if validation_report:
            passed, score = validation_report.get("passed", False), validation_report.get("overall_score", 0)
            st.success("Validation passed") if passed else st.error("Validation needs review")
            st.progress(score, text=f"Overall quality score: {score:.0%}")
            for check in validation_report.get("checks", []): st.markdown(f"{'✓' if check.get('passed') else '×'} **{check.get('check_name', '').replace('_', ' ').title()}** — {check.get('detail', '')}")
        else: st.info("Validation report not available.")
    if export:
        st.download_button("Download report (JSON)", data=json.dumps(result, indent=2), file_name=f"{uploaded_file.name}_report.json", mime="application/json")
else:
    st.markdown('<div class="analysis-box" style="display:flex;flex-direction:column;align-items:center;justify-content:center;"><div class="empty-symbol">✦</div><div style="font-size:1.05rem;color:#fff;font-weight:700;margin-top:1rem">Your analysis will appear here</div><div style="font-size:.8rem;margin-top:.4rem">Add a document, set your review focus, and run the analysis.</div></div>', unsafe_allow_html=True)
