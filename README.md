# CETRI AI Assistant v2.0

[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Repo](https://img.shields.io/badge/repo-CETRI--AI-blueviolet)](https://github.com/chaturvedtejas/CETRI-AI---Jarvis-Clone)

![CETRI Demo](screenshots/demo.gif)

## What is CETRI?

CETRI is an AI-powered personal assistant inspired by JARVIS. It combines speech recognition, text-to-speech, language understanding, and desktop automation into a Python-based assistant that can listen, reason, and act.

Key capabilities:
- Voice and keyboard input
- Natural language understanding
- Task automation and system monitoring
- Conversation memory and context awareness

## Features

- Voice Commands
- AI Chat
- File & OS Automation
- System Monitoring
- Natural Language Processing
- Speech-to-Text with Whisper
- Text-to-Speech using pyttsx3
- Configurable experience
- Built-in testing framework

## Tech Stack

- Python 3.13
- OpenAI Whisper
- pyttsx3
- SpeechRecognition
- psutil
- requests
- pydantic-settings
- tkinter / console UI

## Architecture

CETRI is organized as a multi-component assistant:

```text
User Input (voice / keyboard)
    ↓
Speech-to-Text / Text Parser
    ↓
Intent Extraction & Context Engine
    ↓
LLM / Response Generator
    ↓
Action Dispatcher
    ↓
System Automation / Voice Output
```

Read more in `docs/architecture.md`.

## Repository Structure

```
CETRI-AI/
├── README.md
├── requirements.txt
├── LICENSE
├── .env.example
├── screenshots/
├── docs/
├── backend/
├── frontend/  # nested web/UI repo
├── CETRI_AI/   # installer artifacts
├── CETRI_AI_Installer/
├── main.py
├── test_cetri.py
└── .gitignore
```

## Demo

Add a `screenshots/demo.gif` or `screenshots/demo.png` to visually demonstrate CETRI in action.

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/chaturvedtejas/CETRI-AI---Jarvis-Clone.git
cd "CETRI AI"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env` and add your API keys:

```bash
copy .env.example .env
```

### 5. Run CETRI

```bash
python main.py
```

## Usage

CETRI supports both voice and text interaction:

- Voice input: press Enter at the prompt and speak
- Text input: type commands directly

### Example commands
- `Hello`
- `What time is it?`
- `Create a file named notes.txt`
- `System info`
- `Calculate 42 * 7`

## Memory & Context

CETRI can retain conversational context during a session. A future upgrade can persist user preferences:

- User: "My favorite language is Python."
- CETRI: "I will remember that."
- Later: "What's my favorite language?"
- CETRI: "Your favorite language is Python."

## Recommended Resume-Worthy Enhancements

These features strengthen the assistant and make the project more internship-ready:

1. Voice interaction and wake-word support
2. Persistent memory storage
3. Desktop automation and app launching
4. Email / reminder creation
5. Vision support and PDF analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License. See `LICENSE` for details.
