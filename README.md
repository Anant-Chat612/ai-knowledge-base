# 🧠 AI Knowledge Base (Local & Private)

A modern, offline desktop application built with Python and Flet that lets you manage notes and query them using a local AI model (via Ollama) and SQLite.

## ✨ Features
- **Material 3 UI**: Clean, rounded dark/light compatible interface built with Flet.
- **Full CRUD Operations**: Add, search, edit, and delete notes effortlessly.
- **Local SQLite Database**: Stores all your documents securely and locally on your machine.
- **Ollama AI Integration**: Query your notes using a local LLM (like Llama 3) completely offline—no cloud accounts or internet required!

## 🛠️ Tech Stack
- **Python**
- **Flet** (UI Framework)
- **SQLite** (Local Database)
- **Ollama** (Local AI Inference)

## 🚀 Running the App Locally
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ai-knowledge-base.git](https://github.com/YOUR_USERNAME/ai-knowledge-base.git)
   cd ai-knowledge-base

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install flet certifi
   
4. Ensure Ollama is running on your machine, then launch the app:
   python main.py

