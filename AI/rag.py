def retrieve_context(vector_store, question):

    docs = vector_store.similarity_search(

        question,

        k=4

    )

    context = ""

    for doc in docs:

        context += doc.page_content + "\n"

    return context