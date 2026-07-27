import streamlit as st


AGENT_ICONS = {
    "Financial Analyst": "◈",
    "Contract Reviewer": "◫",
    "Invoice Analyzer": "▣",
    "Tax Assistant": "◇",
    "General Assistant": "✦",
}


def show_sidebar(detected_agent=None):
    st.sidebar.markdown("""
    <div class="sidebar-brand">
      <div class="brand-mark">A</div>
      <div><div class="brand-name">Aureon</div><div class="brand-subtitle">INTELLIGENCE STUDIO</div></div>
    </div>
    <div class="sidebar-label">WORKSPACE</div>
    <div class="nav-item nav-active"><span>◈</span> Document intelligence</div>
    <div class="nav-item"><span>◌</span> Analysis history</div>
    <div class="nav-item"><span>▤</span> Knowledge vault</div>
    <div class="sidebar-label agent-label">ASSIGNED SPECIALIST</div>
    """, unsafe_allow_html=True)

    if detected_agent:
        icon = AGENT_ICONS.get(detected_agent, "✦")
        card = f'<div class="agent-card"><span class="agent-symbol">{icon}</span><div><b>{detected_agent}</b><small>Ready to review</small></div><span class="status-dot"></span></div>'
    else:
        card = '<div class="agent-card"><span class="agent-symbol">✦</span><div><b>Auto-routing enabled</b><small>Awaiting a document</small></div><span class="status-dot"></span></div>'
    st.sidebar.markdown(card, unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-label agent-label">SPECIALIST NETWORK</div>', unsafe_allow_html=True)

    for agent, icon in AGENT_ICONS.items():
        selected = "network-active" if agent == detected_agent else ""
        st.sidebar.markdown(f'<div class="network-agent {selected}"><span>{icon}</span>{agent}</div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-footer"><span class="pulse-dot"></span> All systems operational</div>', unsafe_allow_html=True)
