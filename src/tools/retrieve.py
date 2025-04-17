from langchain_core.tools import tool

"""TO BE FILLED"""

@tool
def retrieve(input: str):
    """
    Retrieves top-k relevant string chunks from the RAG system based on user input.
    Args:
        input: The input string of user's query.
    Returns:
        A list of up to k relevant string chunks from the RAG system.
    """
    retrieved_chunks = []
    # Here writes the rag procedure (user_input->embedding->similarity search->related documents)
    return retrieved_chunks

