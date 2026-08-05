import json
from time import perf_counter
import streamlit as st
from dotenv import load_dotenv

from services.analysis_service import analyze_document
from services.document_service import save_uploaded_file, extract_text, classify_document, route_document, extract_entities
from ui.sidebar import show_sidebar
from core.database import init_database
from services.auth_service import authenticate_user, register_user
from services.persistence_service import add_message, create_document, delete_document, get_document_text, get_history, get_user_analytics, get_user_documents, save_analysis
from services.report_service import generate_pdf_report
from services.logging_service import log_event

load_dotenv()
init_database()

if "user_id" not in st.session_state:
    st.set_page_config(page_title="Aureon | Login", layout="centered")
    st.title("Aureon Intelligence Studio")
    st.caption("Local development access — passwords are securely hashed.")
    login_tab, register_tab = st.tabs(["Login", "Register"])
    with login_tab:
        with st.form("login"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login"):
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user_id, st.session_state.user_email = user.id, user.email
                    st.rerun()
                st.error("Invalid email or password.")
    with register_tab:
        with st.form("register"):
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password (8+ characters)", type="password", key="register_password")
            if st.form_submit_button("Create account"):
                try:
                    user = register_user(email, password)
                    st.session_state.user_id, st.session_state.user_email = user.id, user.email
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    st.stop()

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
with st.sidebar:
    st.caption(f"Signed in as {st.session_state.user_email}")
    if st.button("Logout", use_container_width=True):
        for key in ("user_id", "user_email", "document_id", "document_text", "document_type", "last_result"):
            st.session_state.pop(key, None)
        st.rerun()
    documents = get_user_documents(st.session_state.user_id)
    if documents:
        choices = {f"{item['filename']} · {item['document_type']}": item["id"] for item in documents}
        selected = st.selectbox("Document history", ["Current document"] + list(choices), key="history_document")
        if selected != "Current document" and st.button("Open document", use_container_width=True):
            document_id = choices[selected]
            saved = get_document_text(st.session_state.user_id, document_id)
            st.session_state.document_id = document_id
            st.session_state.document_text = saved["text"]
            st.session_state.document_type = saved["document_type"]
            st.success("Previous document opened. Ask a follow-up question in the workspace.")
        if selected != "Current document" and st.button("Delete document", use_container_width=True):
            delete_document(st.session_state.user_id, choices[selected])
            if st.session_state.get("document_id") == choices[selected]:
                for key in ("document_id", "document_text", "document_type", "last_result"):
                    st.session_state.pop(key, None)
            st.rerun()

st.markdown('<div class="topline"><span>INTELLIGENCE WORKSPACE / 2026</span><span class="secure-pill">● ENCRYPTED &amp; PRIVATE</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">DOCUMENT INTELLIGENCE</div><h1>Decisions, clarified.</h1><p>Turn complex financial and legal documents into clear, defensible insight.</p></div>', unsafe_allow_html=True)

metrics = [("◈", "Documents analyzed", "128", "+12 this week"), ("◫", "Contracts reviewed", "45", "+3 this week"), ("▣", "Invoices processed", "67", "+8 this week"), ("✓", "Compliance checks", "34", "+5 this week")]
for col, (icon, label, value, delta) in zip(st.columns(4), metrics):
    col.markdown(f'<div class="metric-card"><div class="metric-top"><div class="metric-icon">{icon}</div><div class="metric-delta">↑ {delta}</div></div><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

with st.expander("My analytics"):
    analytics = get_user_analytics(st.session_state.user_id)
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Documents", analytics["total_documents"])
    a2.metric("Analyses", analytics["total_analyses"])
    a3.metric("Successful", analytics["successful_analyses"])
    a4.metric("Avg. processing", f"{analytics['average_processing_time']}s")
    st.caption(f"Most-used specialist: {analytics['most_used_agent']} · Failed analyses: {analytics['failed_analyses']}")
    if analytics["documents_by_type"]:
        st.bar_chart(analytics["documents_by_type"])

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
    run = st.button("Run analysis", type="primary", use_container_width=True, disabled=not uploaded_file and not st.session_state.get("document_text"))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="results-head"><div><div class="results-kicker">ANALYSIS CONSOLE</div><h3 style="margin:.35rem 0 0;letter-spacing:-.04em">Review findings</h3></div><div class="live-badge">● READY</div></div>', unsafe_allow_html=True)

if run:
    with st.spinner("Analysing document…"):
        started = perf_counter()
        if uploaded_file:
            filepath = save_uploaded_file(uploaded_file)
            text = extract_text(filepath)
        else:
            text = st.session_state["document_text"]
        classification = classify_document(text)
        doc_type = classification.document_type
        agent_name = route_document(doc_type)
        st.session_state["detected_agent"] = agent_name

        if uploaded_file:
            document_id = create_document(st.session_state.user_id, uploaded_file.name, uploaded_file.type or "unknown", doc_type, classification.confidence, text)
            st.session_state.document_id = document_id
            st.session_state.document_text = text
            st.session_state.document_type = doc_type
        document_id = st.session_state.document_id
        history = get_history(st.session_state.user_id, document_id)
        add_message(st.session_state.user_id, document_id, "user", question)
        result = analyze_document(text, doc_type, question, history)
        add_message(st.session_state.user_id, document_id, "assistant", result["summary"])
        save_analysis(st.session_state.user_id, document_id, result, perf_counter() - started)
        log_event("document_processed", user_id=st.session_state.user_id, document_id=document_id, document_type=doc_type, processing_seconds=round(perf_counter() - started, 3), validation_passed=result.get("validation_passed", False))
        st.session_state.last_result = result
        entity_result = extract_entities(text)

    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Structured", "Entities", "Validation"])

    with tab1:
        st.markdown(f'<div class="analysis-box"><p>{result["summary"]}</p></div>', unsafe_allow_html=True)
        analysis_confidence = result["analysis_confidence"]
        st.markdown(f"**AI/system confidence:** {analysis_confidence['label']} (system score {analysis_confidence['confidence'] * 100:.0f}/100)")
        st.caption(analysis_confidence["disclaimer"])
        if analysis_confidence["rationale"]:
            st.caption(f"Signal basis: {analysis_confidence['rationale']}")
        if detailed and result.get("reasoning_steps"):
            st.markdown("**Reasoning steps**")
            for step in result["reasoning_steps"]:
                st.markdown(f"- **{step.get('action')}** → {step.get('observation')}")

    with tab2:
        st.json(result["structured"])

    with tab3:
        st.markdown(f"**Document classification:** {classification.document_type} — {classification.confidence_label} (system score {classification.confidence * 100:.0f}/100)")
        st.caption(classification.confidence_note)
        st.markdown(f"**Entity extraction:** {entity_result.confidence_label} (system score {entity_result.confidence * 100:.0f}/100)")
        st.caption(entity_result.confidence_note)
        for label, values in entity_result.entities.items():
            if values:
                st.markdown(f"**{label}:** {', '.join(values)}")
        st.markdown("**Why this classification**")
        indicators = ", ".join(classification.matched_signals) or "No strong matching indicators"
        st.write(f"{agent_name} selected because the document contains: {indicators}.")
        st.markdown("**Agents and retrieved sections**")
        st.write("Agents used: " + ", ".join(item.get("agent_name", "Specialist") for item in result.get("agent_responses", [])))
        st.write("Retrieved: " + ", ".join(result.get("source_references", [])))

    with tab4:
        report = result.get("validation_report") or {}
        passed = result.get("validation_passed", True)
        st.success("Validation passed ✓") if passed else st.error("Validation failed ✗")
        if report.get("checks"):
            for check in report["checks"]:
                icon = "✅" if check["passed"] else "❌"
                st.markdown(f"{icon} **{check['check_name']}** — {check['detail']}")

    if export:
        st.download_button("Download JSON", data=json.dumps(result, indent=2), file_name="analysis.json", mime="application/json")
    document_info = {"filename": getattr(uploaded_file, "name", "Previous document"), "document_type": doc_type, "classification_label": classification.confidence_label}
    try:
        pdf_report = generate_pdf_report(document_info, result)
        st.download_button("Generate PDF Report", data=pdf_report, file_name="aureon_report.pdf", mime="application/pdf")
    except RuntimeError as exc:
        st.info(str(exc))
else:
    st.markdown('<div class="analysis-box" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem"><div class="empty-symbol">✦</div><p style="margin:0;font-size:.88rem">Upload a document and click <b>Run analysis</b> to begin.</p></div>', unsafe_allow_html=True)
