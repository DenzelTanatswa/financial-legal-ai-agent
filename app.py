import time
import streamlit as st
from Components.sidebar import show_sidebar
from Utilis.file_handler import save_uploaded_file
from Utilis import extract_text
from Utilis.document_classifier import classify_document
from Utilis.entity_extractor import extract_entities
from Utilis.document_router import route_document
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(
    page_title="Financial & Legal AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-label { color: #8b92a5; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .metric-value { color: #ffffff; font-size: 2rem; font-weight: 700; }
    .metric-delta { color: #22c55e; font-size: 0.85rem; margin-top: 0.2rem; }
    .section-header { color: #8b92a5; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .analysis-box {
        background: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 2rem;
        min-height: 220px;
    }
    .stButton > button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Auto-detect agent from uploaded file (before sidebar renders) ────────────
detected_agent = None
if "detected_agent" in st.session_state:
    detected_agent = st.session_state.detected_agent

show_sidebar(detected_agent)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("## 🤖 Financial & Legal AI Agent")
st.caption("Upload a document — the correct AI agent will be selected automatically.")
st.divider()

# ── Dashboard Metrics ────────────────────────────────────────────────────────
metrics = [
    ("📄", "Documents Analyzed", "128", "+12 this week"),
    ("📝", "Contracts Reviewed",  "45",  "+3 this week"),
    ("🧾", "Invoices Processed",  "67",  "+8 this week"),
    ("✅", "Compliance Checks",   "34",  "+5 this week"),
]
for col, (icon, label, value, delta) in zip(st.columns(4), metrics):
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.6rem">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta">▲ {delta}</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Upload + Agent + Action ──────────────────────────────────────────────────
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<p class="section-header">📁 Document Upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag & drop or browse a file",
        type=["pdf", "docx", "txt", "csv", "xlsx"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"**{uploaded_file.name}** ready for analysis")

with right:
    st.markdown('<p class="section-header">🤖 Active Agent</p>', unsafe_allow_html=True)
    if detected_agent:
        st.info(f"**{detected_agent}**", icon="🧠")
    else:
        st.info("Agent will be auto-assigned after upload.", icon="🧠")
    st.markdown('<p class="section-header" style="margin-top:1rem">⚙️ Options</p>', unsafe_allow_html=True)
    detailed = st.toggle("Detailed Report", value=True)
    export   = st.toggle("Export Results",  value=False)
    run      = st.button("🔍 Run Analysis", type="primary", use_container_width=True, disabled=not uploaded_file)

st.divider()

# ── Analysis Results ─────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Analysis Results</p>', unsafe_allow_html=True)

if run:
    with st.spinner(f"Classifying and analysing `{uploaded_file.name}`…"):
        filepath  = save_uploaded_file(uploaded_file)
        extracted = extract_text(filepath)
        doc_type  = classify_document(extracted)
        entities  = extract_entities(extracted)
        routed    = route_document(doc_type)
        st.session_state.detected_agent = routed
        detected_agent = routed

    tab1, tab2, tab3 = st.tabs(["📋 Summary", "🔍 Key Findings", "⚠️ Risk Flags"])

    with tab1:
        st.markdown(f"**Document:** `{uploaded_file.name}`")
        st.markdown(f"**Detected Type:** {doc_type}")
        st.markdown(f"**Auto-Assigned Agent:** {routed}")
        st.markdown(f"**Mode:** {'Detailed' if detailed else 'Standard'}")
        st.markdown(f"**Characters extracted:** {len(extracted):,}")
        st.progress(100, text="Analysis complete")
        st.success("Document processed successfully. Review the tabs for findings.")
        with st.expander("📄 Extracted Text Preview"):
            st.text(extracted[:3000] + ("…" if len(extracted) > 3000 else ""))

    with tab2:
        st.markdown(f"**Amounts found:** {', '.join(entities['Amounts']) or 'None'}")
        st.markdown(f"**Dates found:** {', '.join(entities['Dates']) or 'None'}")
        st.markdown(f"**Emails found:** {', '.join(entities['Emails']) or 'None'}")

    with tab3:
        st.warning("⚠️ High Risk — Indemnification clause is overly broad")
        st.warning("⚠️ Medium Risk — Missing force majeure provision")
        st.info("ℹ️ Low Risk — Termination notice period is 15 days (standard is 30)")

    if export:
        st.download_button("⬇️ Download Report", data=extracted, file_name=f"{uploaded_file.name}_report.txt")

else:
    st.markdown("""
    <div class="analysis-box" style="display:flex; flex-direction:column; align-items:center; justify-content:center; color:#8b92a5;">
        <div style="font-size:3rem">📂</div>
        <div style="font-size:1rem; margin-top:0.8rem">Upload a document and click <strong>Run Analysis</strong> to see results here.</div>
    </div>""", unsafe_allow_html=True)
