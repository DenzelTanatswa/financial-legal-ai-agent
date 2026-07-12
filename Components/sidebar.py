import streamlit as st

def show_sidebar():
    st.sidebar.title("AI Agents")

    selected_agent = st.sidebar.selectbox(
        "Choose an AI Agent",
        ["Financial  Analyst",
          "Contract  Reviewer",
          "Invoice  Analyzer",
          "Tax  Assistant",
          " Compliance  Checker"
        ]
    )
    st.sidebar.divider()
    st.sidebar.success("System Status:Online")
    return selected_agent 