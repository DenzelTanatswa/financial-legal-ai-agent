import streamlit as st
from Components.sidebar import show_sidebar
from Utilis.file_handler import save_uploaded_file
from Utilis import extract_text
from Utilis.document_classifier import classify_document
from Utilis.entity_extractor import extract_entities
from Utilis.document_router import route_document
from AI.analysis import analyze_document
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Financial & Legal AI Agent", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background: #1e2130; border: 1px solid #2e3250;
        border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center;
    }
    .metric-label { color: #8b92a5; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .metric-value { color: #ffffff; font-size: 2rem; font-weight: 700; }
    .metric-delta { color: #22c55e; font-size: 0.85rem; margin-top: 0.2rem; }
    .section-header { color: #8b92a5; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
    .analysis-box { background: #1e2130; border: 1px solid #2e3250; border-radius: 12px; padding: 2rem; min-height: 220px; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

detected_agent = st.session_state.get("detected_agent")
show_sidebar(detected_agent)

st.markdown("## 🤖 Financial & Legal AI Agent")
st.caption("Upload a document — the correct AI agent will be selected automatically.")
st.divider()

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
    st.info(f"**{detected_agent}**" if detected_agent else "Agent will be auto-assigned after upload.", icon="🧠")
    st.markdown('<p class="section-header" style="margin-top:1rem">⚙️ Options</p>', unsafe_allow_html=True)
    detailed = st.toggle("Detailed Report", value=True)
    export   = st.toggle("Export Results",  value=False)
    question = st.text_input("Question", value="Summarize this document.")
    run      = st.button("🔍 Run Analysis", type="primary", use_container_width=True, disabled=not uploaded_file)

st.divider()
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

        result = analyze_document(text=extracted, document_type=doc_type, question=question)

    structured        = result["structured"]
    confidence        = result["confidence_score"]
    rationale         = result["confidence_rationale"]
    steps             = result["reasoning_steps"]
    risks             = structured.get("risks", [])
    findings          = structured.get("key_findings", [])
    recommendations   = structured.get("recommendations", [])
    validation_report = result.get("validation_report")
    validation_passed = result.get("validation_passed", True)
    collab_agents     = result.get("collaborating_agents", [])
    agent_responses   = result.get("agent_responses", [])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Summary", "🔍 Key Findings", "⚠️ Risk Flags", "🧠 Reasoning", "✅ Validation"]
    )

    with tab1:
        st.markdown(f"**Document:** `{uploaded_file.name}`")
        st.markdown(f"**Detected Type:** {doc_type}")
        st.markdown(f"**Auto-Assigned Agent:** {routed}")
        if collab_agents:
            st.markdown(f"**Collaborating Agents:** {', '.join(collab_agents)}")
        st.markdown(f"**Mode:** {'Detailed' if detailed else 'Standard'}")
        st.markdown(f"**Characters extracted:** {len(extracted):,}")

        color = "#22c55e" if confidence >= 0.75 else "#f59e0b" if confidence >= 0.5 else "#ef4444"
        st.markdown(
            f"**Confidence Score:** <span style='color:{color}; font-weight:700'>{confidence:.0%}</span>",
            unsafe_allow_html=True
        )
        st.progress(confidence, text=rationale or "")

        st.markdown("**Summary:**")
        st.markdown(result["summary"])
        st.progress(100, text="Analysis complete")
        st.success("Document processed successfully. Review the tabs for findings.")

        with st.expander("📄 Extracted Text Preview"):
            st.text(extracted[:3000] + ("…" if len(extracted) > 3000 else ""))

        if detailed and structured:
            skip = {"agent_name", "document_type", "summary", "key_findings", "risks",
                    "recommendations", "confidence_score", "confidence_rationale",
                    "reasoning_steps", "validation_passed", "validation_notes", "collaboration"}
            extra = {k: v for k, v in structured.items() if k not in skip and v}
            if extra:
                with st.expander("📌 Agent-Specific Fields"):
                    for k, v in extra.items():
                        st.markdown(f"**{k.replace('_', ' ').title()}:** {', '.join(v) if isinstance(v, list) else v}")

    with tab2:
        st.markdown(f"**Amounts found:** {', '.join(entities['Amounts']) or 'None'}")
        st.markdown(f"**Dates found:** {', '.join(entities['Dates']) or 'None'}")
        st.markdown(f"**Emails found:** {', '.join(entities['Emails']) or 'None'}")
        if findings:
            st.markdown("---")
            st.markdown("**AI Key Findings:**")
            for f in findings:
                st.markdown(f"- {f}")
        if recommendations:
            st.markdown("**Recommendations:**")
            for r in recommendations:
                st.markdown(f"- {r}")

    with tab3:
        if risks:
            for risk in risks:
                sev    = risk.get("severity", "LOW").upper()
                desc   = risk.get("description", "")
                clause = risk.get("clause")
                label  = f"⚠️ {sev} — {desc}" + (f" *(ref: {clause})*" if clause else "")
                if sev == "HIGH":
                    st.error(label)
                elif sev == "MEDIUM":
                    st.warning(label)
                else:
                    st.info(label)
        else:
            st.success("✅ No risk flags identified.")

    with tab4:
        if steps:
            for step in steps:
                with st.expander(f"Step {step.get('step', '?')}: {step.get('action', '')}"):
                    st.markdown(f"**Observation:** {step.get('observation', '')}")
        else:
            st.info("No reasoning steps available.")

        if collab_agents and detailed and agent_responses:
            st.markdown("---")
            st.markdown("**Per-Agent Reasoning:**")
            for resp in agent_responses:
                agent_name = resp.get("agent_name", "Agent")
                agent_conf = resp.get("confidence_score", 0.0)
                with st.expander(f"🤖 {agent_name} — confidence {agent_conf:.0%}"):
                    st.markdown(resp.get("summary", ""))
                    for s in resp.get("reasoning_steps", []):
                        st.markdown(f"- **Step {s.get('step')}** {s.get('action')}: {s.get('observation')}")

    with tab5:
        if validation_report:
            overall = validation_report.get("overall_score", 0.0)
            passed  = validation_report.get("passed", False)
            v_color = "#22c55e" if passed else "#ef4444"
            st.markdown(
                f"**Validation Status:** <span style='color:{v_color}; font-weight:700'>{'PASSED ✅' if passed else 'FAILED ❌'}</span>",
                unsafe_allow_html=True
            )
            st.progress(overall, text=f"Overall Quality Score: {overall:.0%}")
            st.markdown("**Checks:**")
            for check in validation_report.get("checks", []):
                icon   = "✅" if check.get("passed") else "❌"
                name   = check.get("check_name", "").replace("_", " ").title()
                detail = check.get("detail", "")
                st.markdown(f"{icon} **{name}** — {detail}")
        else:
            st.info("Validation report not available.")

    if export:
        import json
        st.download_button(
            "⬇️ Download Report (JSON)",
            data=json.dumps(result, indent=2),
            file_name=f"{uploaded_file.name}_report.json",
            mime="application/json"
        )

else:
    st.markdown("""
    <div class="analysis-box" style="display:flex; flex-direction:column; align-items:center; justify-content:center; color:#8b92a5;">
        <div style="font-size:3rem">📂</div>
        <div style="font-size:1rem; margin-top:0.8rem">Upload a document and click <strong>Run Analysis</strong> to see results here.</div>
    </div>""", unsafe_allow_html=True)
