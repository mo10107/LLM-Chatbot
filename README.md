# LLM Chatbot

This project is a chatbot interface using Together API with Streamlit and FastAPI, allowing model selection and conversation history.

## Features
- Choose from multiple AI models.
- Real-time chat with response caching.
- FastAPI backend serving responses.
- Summarized conversation history.
- Dockerized for easy deployment.

## Project Structure
The chatbot is built using **Streamlit** for the frontend and **FastAPI** for handling backend API requests. It includes:
- `main.py`: The core script integrating the UI and API.
- `Dockerfile`: Defines the Docker container environment.
- `requirements.txt`: Lists required dependencies.

## Setup

### Clone the repository
```sh
git clone https://github.com/yourusername/llm-chatbot.git
cd llm-chatbot
```

### Install dependencies
```sh
pip install -r requirements.txt
```

### Run the application
```sh
python main.py
```

## Docker Deployment

### Build and Run
```sh
docker build -t llm-chatbot .
docker run -p 8501:8501 -p 8000:8000 llm-chatbot
```

Now, open `http://localhost:8501` in your browser to access the chatbot.

## Environment Variables
Set `TOGETHER_API_KEY` before running the app.
```sh
export TOGETHER_API_KEY=your_api_key_here
```
