import streamlit as st
import requests
import os
import json
import time
import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from functools import lru_cache

st.set_page_config(page_title="LLM Chatbot", layout="wide")

app = FastAPI()

API_URL = os.getenv("API_URL", "http://localhost:8000")
DB_FILE = "db.json"

class QueryRequest(BaseModel):
    query: str

SYSTEM_PROMPT = "You are a professional AI assistant. Provide clear and informative answers in a formal tone."

TOGETHER_API_KEY = "188aa8e3ae9ba9f7bdb2ff337fad1bc2bf3c0c701af26d16055afde955f23625"
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"
HEADERS = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}

AVAILABLE_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "Qwen/Qwen2-72B-Instruct",
    "mistralai/Mixtral-8x7B-Instruct-v0.1"
]

MODEL_DISPLAY_NAMES = {model: model.split("/")[-1] for model in AVAILABLE_MODELS}

selected_model_key = st.sidebar.selectbox("Select Model", list(MODEL_DISPLAY_NAMES.values()), index=0)
selected_model = [key for key, value in MODEL_DISPLAY_NAMES.items() if value == selected_model_key][0]

@lru_cache(maxsize=100)
def query_together(prompt, model=selected_model, retries=3, delay=5):
    payload = {
        "model": model,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {prompt}\nAssistant:",
        "max_rpm": 60,
        "temperature": 0.5
    }
    
    for _ in range(retries):
        try:
            response = requests.post(TOGETHER_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("text", "").split("User", 1)[0].strip()
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return "The server is too busy. Please try again later."

def summarize_chat_history(history):
    text = " ".join([f"User: {msg['content']}" if msg['role'] == "user" else f"Assistant: {msg['content']}" for msg in history])
    if len(text) < 50:
        return text
    
    payload = {
        "model": selected_model,
        "prompt": f"Summarize the following conversation, keeping the context clear:\n{text}\nSummary:",
        "max_rpm": 60,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(TOGETHER_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    except requests.exceptions.RequestException:
        return "Failed to generate summary."

def summarize_and_store_chat_history():
    if len(st.session_state.messages) > 10:
        summary = summarize_chat_history(st.session_state.messages)
        st.session_state.messages = [{"role": "assistant", "content": summary}]
        with open(DB_FILE, "w") as file:
            json.dump({"chat_history": st.session_state.messages}, file)

@app.post("/chat")
def chat(request: QueryRequest):
    return {"response": query_together(request.query, model=selected_model)}

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

threading.Thread(target=run_fastapi, daemon=True).start()

st.title("🤖 LLM Chatbot")

if "messages" not in st.session_state:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            st.session_state.messages = json.load(file).get("chat_history", [])
    else:
        st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        bot_response = query_together(prompt, model=selected_model)
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    summarize_and_store_chat_history()
    with open(DB_FILE, "w") as file:
        json.dump({"chat_history": st.session_state.messages}, file)

if st.sidebar.button("Clear Chat"):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as file:
            json.dump({"chat_history": []}, file)
    st.session_state.messages = []
    st.rerun()
