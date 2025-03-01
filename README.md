# LLM Chatbot

## Overview
This project is a chatbot interface using **Streamlit** and **FastAPI**, integrating **Together API** to provide real-time conversational AI. It supports **multiple models**, **chat history**, and **Docker deployment**.

## Components

### 1. `main.py` - The Main Application
This file contains:
- **Streamlit UI** for the chatbot.
- **FastAPI backend** to serve responses.
- **Model selection and caching**.
- **Chat history management**.

### 2. `Dockerfile` - Containerization
Defines the environment for running the application in **Docker**.

### 3. `requirements.txt` - Dependencies
Lists the Python dependencies required to run the chatbot.

---

## Code Breakdown

### **1. Import Required Libraries**
```python
import streamlit as st
import requests
import os
import json
import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from functools import lru_cache
```

- `streamlit`: UI framework for chatbot interaction.
- `fastapi`: Backend API for handling chat requests.
- `uvicorn`: Runs the FastAPI server.
- `requests`: Makes API requests to Together API.
- `pydantic`: Defines structured request models.
- `lru_cache`: Caches responses to optimize performance.

---

### **2. Initialize FastAPI and Streamlit**
```python
st.set_page_config(page_title="LLM Chatbot", layout="wide")
app = FastAPI()
```
- `FastAPI` runs the backend for processing chat requests.
- `Streamlit` provides the chatbot UI.

---

### **3. API Configuration**
```python
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"
HEADERS = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}
```
- Retrieves API Key from environment variables.
- Defines the Together API URL and authentication headers.

---

### **4. Model Selection**
```python
AVAILABLE_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "Qwen/Qwen2-72B-Instruct",
    "mistralai/Mixtral-8x7B-Instruct-v0.1"
]
MODEL_DISPLAY_NAMES = {model: model.split("/")[-1] for model in AVAILABLE_MODELS}
selected_model_key = st.sidebar.selectbox("Select Model", list(MODEL_DISPLAY_NAMES.values()), index=0)
selected_model = [key for key, value in MODEL_DISPLAY_NAMES.items() if value == selected_model_key][0]
```
- Allows users to **select an AI model** from the sidebar.
- Displays only the **model name** instead of the full path.

---

### **5. Query the Together API**
```python
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
```
- Sends the user prompt to the **Together API**.
- Uses **caching** to store previous responses and reduce API calls.

---

### **6. FastAPI Chat Endpoint**
```python
@app.post("/chat")
def chat(request: QueryRequest):
    return {"response": query_together(request.query, model=selected_model)}
```
- Defines a **POST API** endpoint that processes chat requests.

---

### **7. Run FastAPI Server**
```python
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)
threading.Thread(target=run_fastapi, daemon=True).start()
```
- Runs **FastAPI** as a background thread while Streamlit runs in the foreground.

---

### **8. Streamlit Chat UI**
```python
st.title("🤖 LLM Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```
- Displays chat history.

---

### **9. Handle User Input**
```python
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        bot_response = query_together(prompt, model=selected_model)
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
```
- Captures user input and sends it to the **Together API**.
- Updates the chat interface with the response.

---

### **10. Clear Chat Button**
```python
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
```
- Clears chat history and **refreshes the UI**.

---

## **Deployment**

### **1. Run Locally**
```sh
pip install -r requirements.txt
python main.py
```

### **2. Run with Docker**
```sh
docker build -t llm-chatbot .
docker run -p 8501:8501 -p 8000:8000 llm-chatbot
```

Now, open `http://localhost:8501` in your browser to access the chatbot.

---

## **Environment Variables**
Set `TOGETHER_API_KEY` before running:
```sh
export TOGETHER_API_KEY=your_api_key_here
```

## **Conclusion**
This project provides an **interactive chatbot** with **multiple AI models**, **conversation history**, and **real-time responses**. The system is fully **Dockerized** and can be deployed with ease.

---
