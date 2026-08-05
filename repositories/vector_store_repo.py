from langchain_community.vectorstores import FAISS
from repositories.embeddings_repo import embeddings
from core.config import CHUNK_SIZE, RAG_TOP_K


def build_vector_store(text: str) -> FAISS:
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    return FAISS.from_texts(chunks, embeddings, metadatas=[{"chunk": index + 1} for index in range(len(chunks))])


def retrieve_context(vector_store: FAISS, question: str) -> str:
    docs = vector_store.similarity_search(question, k=RAG_TOP_K)
    return "\n".join(doc.page_content for doc in docs)


def retrieve_sources(vector_store: FAISS, question: str) -> list[str]:
    """User-safe retrieval references; source files without page metadata use chunks."""
    docs = vector_store.similarity_search(question, k=RAG_TOP_K)
    return [f"Document section {doc.metadata.get('chunk', index + 1)}" for index, doc in enumerate(docs)]
