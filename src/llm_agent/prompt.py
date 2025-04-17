

CHATBOT_PROMPT = """You are TailorTrip, an AI travel assistant. Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: Let me help you with that.
"""

def get_chatbot_prompt(context: str, question: str) -> str:
    return CHATBOT_PROMPT.format(context=context, question=question)