import streamlit as st

AGENT_ICONS = {
    "Financial Analyst":  "📊",
    "Contract Reviewer":  "📝",
    "Invoice Analyzer":   "🧾",
    "Tax Assistant":      "🧮",
    "General Assistant":  "🤖",
}

def show_sidebar(detected_agent=None):
    st.sidebar.title("🤖 AI Agent System")
    st.sidebar.divider()

    st.sidebar.markdown("##### 🔍 Auto-Detected Agent")
    if detected_agent:
        icon = AGENT_ICONS.get(detected_agent, "🤖")
        st.sidebar.success(f"{icon} **{detected_agent}**")
    else:
        st.sidebar.info("Upload a document to auto-detect the agent.")

    st.sidebar.divider()
    st.sidebar.markdown("##### 📋 Agent Directory")
    for agent, icon in AGENT_ICONS.items():
        active = "← active" if agent == detected_agent else ""
        st.sidebar.markdown(f"{icon} {agent} {active}")

    st.sidebar.divider()
    st.sidebar.success("🟢 System Status: Online")
