from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uuid
from typing import List, Dict
from system_input import SYSTEM_INPUTS
import json
import torch
from auto_embed import AutoEmbedding
from langchain_community.vectorstores import FAISS

# load embeddings
rag_config = {
        "faiss_path": "./rag",
        "model_name": "pritamdeka/S-PubMedBert-MS-MARCO",
        "embedding_type": "sentence_transformer",
        "chunk_size": 1024,
        "chunk_overlap": 256
    }
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
embeddings = AutoEmbedding(rag_config['model_name'], rag_config['embedding_type'], model_kwargs={"device": device})

# load rag_db
rag_db = FAISS.load_local(rag_config["faiss_path"], embeddings, allow_dangerous_deserialization=True)

# retrieve context and create prompt
retriever = rag_db.as_retriever(search_kwargs={"k": 5})

# Configuration for the LLM API (using environment variables for security)
API_KEY = "sk-rkaaajuldwebwppljkefybgzhtoslzjaukylvnivrzanbhjk"
LLM_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

# Predefined initial message
INITIAL_MESSAGE = "Hello! I am your intelligent medical assistant. I will support you with preventative care. Please note that the information I generate is for reference only!"

# Session storage (in-memory nested dictionary: user_id -> history_record_id -> history list)
sessions: Dict[str, Dict[int, List[Dict[str, str]]]] = {}

# Session ID mapping (session_id -> (user_id, history_record_id))
session_mapping: Dict[str, tuple[str, int]] = {}

# Maximum history length (including system message)
MAX_HISTORY = 10

# Define request and response models
class StartRequest(BaseModel):
    user_id: str
    history_record_id: int

class StartResponse(BaseModel):
    session_id: str
    initial_message: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

# Create FastAPI application
app = FastAPI()

# Function to summarize conversation history using the LLM
def summarize_history(history: List[Dict[str, str]]) -> str:
    """Calls the LLM to summarize the conversation history."""
    summary_prompt = (
        "Please summarize the following conversation history:\n" +
        "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    )
    summary_messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
        {"role": "user", "content": summary_prompt}
    ]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/QwQ-32B",
        "messages": summary_messages,
        "stream": False,
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    response = requests.post(LLM_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Failed to summarize history: {response.status_code}")

# Function to call RAG tool
def should_call_rag_tool(user_query: str) -> Dict:
    # Tool specification following OpenAI standards
    tool_spec = {
        "type": "function",
        "function": {
            "name": "retrieve_from_rag",
            "description": "Search the RAG database for medical information",
            "parameters": {
                "type": "object",
                "properties": {
                    "should_call_rag": {
                        "type": "boolean",
                        "description": "Whether to invoke RAG search"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Explanation for the decision"
                    },
                    "query_rewrite": {
                        "type": "string",
                        "description": "Optimized search query if applicable"
                    }
                },
                "required": ["should_call_rag", "reason"]
            }
        }
    }

    # API payload
    payload = {
        "model": "Qwen/QwQ-32B",
        "messages": [{"role": "user", "content": user_query}],
        "tools": [tool_spec],
        "tool_choice": {
            "type": "function",
            "function": {"name": "retrieve_from_rag"}
        },
        "temperature": 0.1
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload
        )
        response.raise_for_status()
        
        # Parse tool call response
        tool_call = response.json()["choices"][0]["message"]["tool_calls"][0]
        return json.loads(tool_call["function"]["arguments"])  # Already parsed as JSON
        
    except Exception as e:
        raise Exception(f"RAG tool decision failed: {str(e)}")

# /start endpoint: Start a new conversation for a user with a specific history record
@app.post("/start", response_model=StartResponse)
def start_conversation(request: StartRequest):
    user_id = request.user_id
    history_record_id = request.history_record_id

    # Validate history_record_id
    if history_record_id not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="history_record_id must be between 1 and 4")

    # Initialize user's session dictionary if it doesn't exist
    if user_id not in sessions:
        sessions[user_id] = {}

    # Check if the user already has a session for this history_record_id
    if history_record_id in sessions[user_id]:
        # Find the existing session_id from session_mapping
        for session_id, (stored_user_id, stored_history_id) in session_mapping.items():
            if stored_user_id == user_id and stored_history_id == history_record_id:
                return {"session_id": session_id, "initial_message": INITIAL_MESSAGE}

    # Generate a new session if not found
    session_id = str(uuid.uuid4())
    
    # Store the session with both session_id and history
    sessions[user_id][history_record_id] = [{"role": "system", "content": SYSTEM_INPUTS[history_record_id]}]
    session_mapping[session_id] = (user_id, history_record_id)

    return {"session_id": session_id, "initial_message": INITIAL_MESSAGE}

# /chat endpoint: Handle user messages and generate replies
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id
    user_message = request.message

    # Check whether use tool
    decision = should_call_rag_tool(user_message)
    if decision.get("query_rewrite"):
        retrieved_docs = retriever.invoke(decision['query_rewrite'])
        context = f"## **References:** \n\n---\n\n" + "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        user_message += context
        print(decision)
        print(context)

    # Check if the session exists
    if session_id not in session_mapping:
        raise HTTPException(status_code=404, detail="Session not found")

    # Retrieve user_id and history_record_id from session mapping
    user_id, history_record_id = session_mapping[session_id]

    # Get the current session's history
    history = sessions[user_id][history_record_id]

    # Add the user's message to the history
    history.append({"role": "user", "content": user_message})

    # Check if history exceeds the maximum length and summarize if necessary
    if len(history) > MAX_HISTORY:
        system_message = history[0] if history[0]["role"] == "system" else None
        summary = summarize_history(history[1:] if system_message else history)
        new_history = [system_message] if system_message else []
        new_history.append({"role": "assistant", "content": summary})
        new_history.append({"role": "user", "content": user_message})
        sessions[user_id][history_record_id] = new_history
        history = new_history

    # Prepare messages for the LLM
    messages = history

    # Call the LLM API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": messages,
        "stream": False,
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    response = requests.post(LLM_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error calling LLM API")

    # Extract and store the LLM's reply
    reply = response.json()["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": reply})

    return {"reply": reply}

# Run the service with: uvicorn main:app --host 0.0.0.0 --port 8080
# curl -X POST http://localhost:8080/start -H "Content-Type: application/json" -d '{"user_id": "userA", "history_record_id": 1}'
# curl -X POST http://localhost:8080/chat -H "Content-Type: application/json" -d '{"session_id": "some-uuid", "message": "Hi, how are you?"}'