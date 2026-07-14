from ai.llm import llm 
from longchain_core.prompts import ChatPromptTemplate

legal_prompt = """
You are a senior Legal Analyst.

Review the document carefully.

Context:
{context}

Question:
{question}

Provide: 

## Contract Summary 

## Important Clauses

## Risks 

## Recommendations
"""

def legal_agent(state):
    prompt = ChatPromptTemplate.from_template(legal_prompt)
    chain = prompt | llm

    answer = chain.invoke({
        "context": state["context"],
        "question": state["question"]
    })
    state["response"] = answer.content
    return state