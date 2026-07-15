from ai.graph import graph
from ai.vector_store import build_vector_store
from ai.rag import retrieve_context


def analyze_document(text, document_type, question):
    # Build vector store
    vector_store = build_vector_store(text)

    # Retrieve relevant context
    context = retrieve_context(vector_store, question)

    # Create workflow state
    state = {
        "question": question,
        "context": context,
        "document_type": document_type,
        "selected_agent": "",
        "response": ""
    }

    # Run LangGraph workflow
    result = graph.invoke(state)

    return result["response"]