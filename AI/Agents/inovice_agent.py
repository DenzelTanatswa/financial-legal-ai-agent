from ai.llm import llm
from langchain_core.prompts import ChatPromptTemplate

inovice_prompt = """
You are an Invoice Audit specialist.

Analyze the inovice.

context:
{context}

Question:
{question}

Return:
##Vendor

##Invoice Number

##Amount

##Due Date

##Risks
"""
def inovice_agent(state):
    prompt = ChatPromptTemplate.from_template(Inovice_prompt)
    chain = prompt | llm
    answer = chain.inovke({
        "context": state["context"],
        "question": state["question"]"

    })
    state["response"] = answer.content
    
    return state
