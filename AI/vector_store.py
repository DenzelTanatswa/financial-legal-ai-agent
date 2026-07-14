from langchain_community.vectorstores import FAISS

from ai.embeddings import embeddings


def build_vector_store(text):

    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

    return FAISS.from_texts(

        chunks,

        embeddings
    )