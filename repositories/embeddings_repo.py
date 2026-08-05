from langchain_community.embeddings import HuggingFaceEmbeddings
from core.config import EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
