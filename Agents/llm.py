from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
