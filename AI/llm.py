import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(

    model="gpt-4.1",

    temperature=0

)
from langchain_core.prompts import ChatPromptTemplate

from ai.prompts import FINANCIAL_PROMPT


def ask_financial_agent(context, question):

    prompt = ChatPromptTemplate.from_template(

        FINANCIAL_PROMPT

    )

    chain = prompt | llm

    return chain.invoke(

        {

            "context": context,

            "question": question

        }

    ).content